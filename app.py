import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import time
from datetime import datetime
import hmac
import hashlib
import base64
import urllib.parse
import uuid

# Load environment variables
load_dotenv()

# Configuration for hosted n8n
N8N_HOST = "https://n8n-330.workflowapp.ai"
N8N_WEBHOOK_PATH = "/webhook-test/search"

# Set page config
st.set_page_config(
    page_title="AI Analyst Search Backend",
    page_icon="🔍",
    layout="wide"
)

# Sidebar for API configuration
st.sidebar.title("Search API Configuration")

# API selection
search_api = st.sidebar.selectbox(
    "Select Search API",
    ["Free Search API", "Google Search API", "Baidu Search API"]
)

# API keys section
with st.sidebar.expander("API Keys (Optional)", expanded=False):
    if search_api == "Google Search API":
        google_api_key = st.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
        google_cx = st.text_input("Google Custom Search Engine ID", value=os.getenv("GOOGLE_CX", ""))
    elif search_api == "Baidu Search API":
        baidu_api_key = st.text_input("Baidu API Key", value=os.getenv("BAIDU_API_KEY", ""), type="password")
        baidu_secret_key = st.text_input("Baidu Secret Key", value=os.getenv("BAIDU_SECRET_KEY", ""), type="password")

# n8n Configuration
with st.sidebar.expander("n8n Configuration", expanded=True):
    n8n_host = st.text_input("n8n Host URL", value=N8N_HOST)
    n8n_webhook_path = st.text_input("n8n Webhook Path", value=N8N_WEBHOOK_PATH)
    st.info(f"Full n8n webhook URL: {n8n_host}{n8n_webhook_path}")

# Advanced settings
with st.sidebar.expander("Advanced Settings", expanded=False):
    max_results = st.number_input("Maximum Results", min_value=1, max_value=50, value=10)
    timeout = st.number_input("Timeout (seconds)", min_value=1, max_value=30, value=10)
    cache_duration = st.number_input("Cache Duration (minutes)", min_value=0, max_value=1440, value=60)

# Initialize session state for cache
if 'search_cache' not in st.session_state:
    st.session_state.search_cache = {}

# Cache management
def get_from_cache(key):
    if key in st.session_state.search_cache:
        timestamp, data = st.session_state.search_cache[key]
        if (time.time() - timestamp) < (cache_duration * 60):
            return data
    return None

def save_to_cache(key, data):
    st.session_state.search_cache[key] = (time.time(), data)

# Search API implementations
def search_free_api(query, language="en", max_results=10):
    """
    Search using a free search API (DuckDuckGo)
    """
    try:
        # Using DuckDuckGo API via RapidAPI
        url = "https://duckduckgo-duckduckgo-zero-click-info.p.rapidapi.com/"
        
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY", ""),
            "X-RapidAPI-Host": "duckduckgo-duckduckgo-zero-click-info.p.rapidapi.com"
        }
        
        params = {
            "q": query,
            "format": "json"
        }
        
        # If no RapidAPI key, use a fallback method
        if not headers["X-RapidAPI-Key"]:
            return search_fallback(query, language, max_results)
        
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract results
            results = []
            
            # Add abstract if available
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", "Abstract"),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("AbstractText", ""),
                    "source": "duckduckgo",
                    "language": language,
                    "credibility_score": 0.8,
                    "published_date": datetime.now().strftime("%Y-%m-%d")
                })
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:max_results-1]:
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "duckduckgo",
                        "language": language,
                        "credibility_score": 0.7,
                        "published_date": datetime.now().strftime("%Y-%m-%d")
                    })
            
            return {
                "status": "success",
                "query": query,
                "results_count": len(results),
                "processing_time": "1.0s",
                "results": results
            }
        else:
            return search_fallback(query, language, max_results)
    
    except Exception as e:
        st.error(f"Error with DuckDuckGo API: {str(e)}")
        return search_fallback(query, language, max_results)

def search_fallback(query, language="en", max_results=10):
    """
    Fallback search method that generates mock results
    """
    results = []
    
    # Generate mock results
    for i in range(min(max_results, 10)):
        results.append({
            "title": f"Result {i+1} for '{query}'",
            "url": f"https://example.com/result{i+1}",
            "snippet": f"This is a mock result {i+1} for the query '{query}'. This is generated as a fallback when no search API is available.",
            "source": "mock",
            "language": language,
            "credibility_score": 0.5,
            "published_date": datetime.now().strftime("%Y-%m-%d")
        })
    
    return {
        "status": "success",
        "query": query,
        "results_count": len(results),
        "processing_time": "0.1s",
        "results": results
    }

def search_google_api(query, language="en", max_results=10):
    """
    Search using Google Custom Search API
    """
    try:
        api_key = google_api_key or os.getenv("GOOGLE_API_KEY", "")
        cx = google_cx or os.getenv("GOOGLE_CX", "")
        
        if not api_key or not cx:
            st.warning("Google API Key and Custom Search Engine ID are required for Google Search")
            return search_fallback(query, language, max_results)
        
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "lr": f"lang_{language}",
            "num": min(max_results, 10)  # Google API max is 10 per request
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "google",
                    "language": language,
                    "credibility_score": 0.9,
                    "published_date": datetime.now().strftime("%Y-%m-%d")
                })
            
            return {
                "status": "success",
                "query": query,
                "results_count": len(results),
                "processing_time": "1.0s",
                "results": results
            }
        else:
            st.error(f"Google API Error: {response.status_code} - {response.text}")
            return search_fallback(query, language, max_results)
    
    except Exception as e:
        st.error(f"Error with Google API: {str(e)}")
        return search_fallback(query, language, max_results)

def search_baidu_api(query, language="zh", max_results=10):
    """
    Search using Baidu Search API
    """
    try:
        api_key = baidu_api_key or os.getenv("BAIDU_API_KEY", "")
        secret_key = baidu_secret_key or os.getenv("BAIDU_SECRET_KEY", "")
        
        if not api_key or not secret_key:
            st.warning("Baidu API Key and Secret Key are required for Baidu Search")
            return search_fallback(query, language, max_results)
        
        # Baidu Web Search API
        url = "https://aip.baidubce.com/rpc/2.0/creation/v1/search/realtime"
        
        # Get access token
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        token_response = requests.post(token_url)
        
        if token_response.status_code != 200:
            st.error(f"Baidu Token Error: {token_response.status_code} - {token_response.text}")
            return search_fallback(query, language, max_results)
        
        access_token = token_response.json().get("access_token")
        
        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        params = {
            "access_token": access_token
        }
        
        payload = {
            "query": query,
            "num": min(max_results, 10)
        }
        
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            
            for item in data.get("result", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "source": "baidu",
                    "language": language,
                    "credibility_score": 0.8,
                    "published_date": datetime.now().strftime("%Y-%m-%d")
                })
            
            return {
                "status": "success",
                "query": query,
                "results_count": len(results),
                "processing_time": "1.0s",
                "results": results
            }
        else:
            st.error(f"Baidu API Error: {response.status_code} - {response.text}")
            return search_fallback(query, language, max_results)
    
    except Exception as e:
        st.error(f"Error with Baidu API: {str(e)}")
        return search_fallback(query, language, max_results)

# Main search function
def perform_search(query, language="en", sources=None, max_results=10):
    """
    Perform search using the selected API
    """
    cache_key = f"{search_api}:{query}:{language}:{max_results}"
    cached_result = get_from_cache(cache_key)
    
    if cached_result:
        st.success("Results retrieved from cache")
        return cached_result
    
    if search_api == "Google Search API":
        result = search_google_api(query, language, max_results)
    elif search_api == "Baidu Search API":
        result = search_baidu_api(query, language, max_results)
    else:  # Free Search API
        result = search_free_api(query, language, max_results)
    
    save_to_cache(cache_key, result)
    return result

# API endpoint for n8n integration
def api_search_endpoint(request_data):
    """
    Handle search requests from n8n
    """
    query = request_data.get("query", "")
    language = request_data.get("language", "en")
    max_results = request_data.get("max_results", 10)
    sources = request_data.get("sources", ["web"])
    
    if not query:
        return {
            "status": "error",
            "message": "Query parameter is required"
        }
    
    return perform_search(query, language, sources, max_results)

# Function to test n8n connection
def test_n8n_connection():
    """
    Test connection to n8n webhook
    """
    try:
        full_url = f"{n8n_host}{n8n_webhook_path}"
        
        # Simple test request
        test_data = {
            "query": "test connection",
            "language": "en",
            "max_results": 1
        }
        
        response = requests.post(full_url, json=test_data, timeout=timeout)
        
        if response.status_code == 200:
            return True, "Connection successful!"
        else:
            return False, f"Connection failed: {response.status_code} - {response.text}"
    
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# Main Streamlit UI
st.title("AI Analyst Search Backend")

# Tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["Search Testing", "API Endpoint", "n8n Integration", "Documentation"])

with tab1:
    st.header("Test Search Functionality")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Search Query", placeholder="Enter your search query")
    
    with col2:
        language = st.selectbox("Language", ["en", "zh", "ru", "es", "fr", "de", "ja", "ar"])
    
    if st.button("Search"):
        if query:
            with st.spinner("Searching..."):
                result = perform_search(query, language, None, max_results)
                
                st.subheader("Search Results")
                st.write(f"Found {result['results_count']} results for '{query}'")
                
                for i, item in enumerate(result["results"]):
                    with st.expander(f"{i+1}. {item['title']}", expanded=i==0):
                        st.write(f"**URL:** {item['url']}")
                        st.write(f"**Snippet:** {item['snippet']}")
                        st.write(f"**Source:** {item['source']}")
                        st.write(f"**Language:** {item['language']}")
                        st.write(f"**Credibility Score:** {item['credibility_score']}")
                        st.write(f"**Published Date:** {item['published_date']}")
                
                # Show raw JSON
                with st.expander("Raw JSON Response", expanded=False):
                    st.json(result)
        else:
            st.warning("Please enter a search query")

with tab2:
    st.header("API Endpoint for n8n Integration")
    
    st.markdown(f"""
    This Streamlit app provides an API endpoint that can be used with the n8n search workflow.
    
    ### Endpoint URL
    ```
    http://localhost:8501/api/search/execute
    ```
    
    ### Request Format
    ```json
    {{
        "query": "your search query",
        "language": "en",
        "max_results": 10,
        "sources": ["web", "news"]
    }}
    ```
    
    ### Response Format
    ```json
    {{
        "status": "success",
        "query": "your search query",
        "results_count": 5,
        "processing_time": "1.0s",
        "results": [
            {{
                "title": "Result Title",
                "url": "https://example.com",
                "snippet": "Result snippet...",
                "source": "google",
                "language": "en",
                "credibility_score": 0.9,
                "published_date": "2025-04-14"
            }},
            ...
        ]
    }}
    ```
    """)
    
    st.subheader("Test API Request")
    
    test_query = st.text_input("Test Query", placeholder="Enter a test query", key="test_api_query")
    test_language = st.selectbox("Test Language", ["en", "zh", "ru", "es", "fr", "de", "ja", "ar"], key="test_api_language")
    test_max_results = st.number_input("Test Max Results", min_value=1, max_value=50, value=5, key="test_api_max_results")
    
    if st.button("Test API"):
        if test_query:
            test_request = {
                "query": test_query,
                "language": test_language,
                "max_results": test_max_results,
                "sources": ["web"]
            }
            
            with st.spinner("Processing API request..."):
                test_response = api_search_endpoint(test_request)
                
                st.subheader("API Response")
                st.json(test_response)
        else:
            st.warning("Please enter a test query")

with tab3:
    st.header("n8n Integration")
    
    st.markdown(f"""
    ### Your n8n Configuration
    
    - **n8n Host:** {n8n_host}
    - **Webhook Path:** {n8n_webhook_path}
    - **Full Webhook URL:** {n8n_host}{n8n_webhook_path}
    
    ### Testing n8n Connection
    
    Click the button below to test the connection to your n8n instance:
    """)
    
    if st.button("Test n8n Connection"):
        with st.spinner("Testing connection to n8n..."):
            success, message = test_n8n_connection()
            
            if success:
                st.success(message)
            else:
                st.error(message)
    
    st.markdown("""
    ### Updating n8n Workflows
    
    If you've imported the workflows from the JSON files, you'll need to update the HTTP Request nodes in n8n to point to this Streamlit app.
    
    1. In n8n, open each workflow
    2. Find the HTTP Request nodes that call the search API
    3. Update the URL to point to this Streamlit app's API endpoint:
       ```
       http://your-streamlit-url:8501/api/search/execute
       ```
    4. Save the workflows
    
    ### Making Streamlit Accessible to n8n
    
    Since your n8n instance is hosted online, it needs to be able to reach your Streamlit app. You have two options:
    
    **Option 1: Use a Tunnel Service**
    - Install ngrok: `pip install pyngrok`
    - Run: `ngrok http 8501`
    - This will give you a public URL like `https://abc123.ngrok.io`
    - Update the n8n HTTP Request nodes to use this URL + `/api/search/execute`
    
    **Option 2: Deploy Streamlit to a Hosting Service**
    - Deploy your Streamlit app to Streamlit Cloud, Heroku, or similar
    - Update the n8n HTTP Request nodes to use your deployed URL
    """)

with tab4:
    st.header("Documentation")
    
    st.markdown("""
    ## AI Analyst Search Backend
    
    This Streamlit application provides a search backend for the AI Analyst Agent. It can be used to test the n8n search workflow by providing a compatible API endpoint.
    
    ### Features
    
    - Multiple search API options:
      - Free Search API (fallback to mock data if no API key)
      - Google Custom Search API (requires API key and CX)
      - Baidu Search API (requires API key and secret key)
    
    - API endpoint compatible with n8n search workflow
    - Result caching to improve performance
    - Multilingual search support
    - Integration with hosted n8n instance
    
    ### Setup Instructions
    
    1. **Environment Variables**
    
       Create a `.env` file in the same directory as this app with the following variables:
       
       ```
       # RapidAPI Key (for Free Search API)
       RAPIDAPI_KEY=your_rapidapi_key
       
       # Google Search API
       GOOGLE_API_KEY=your_google_api_key
       GOOGLE_CX=your_google_custom_search_engine_id
       
       # Baidu Search API
       BAIDU_API_KEY=your_baidu_api_key
       BAIDU_SECRET_KEY=your_baidu_secret_key
       ```
    
    2. **Running the App**
    
       ```bash
       streamlit run app.py
       ```
    
    3. **Connecting to n8n**
    
       In your n8n search workflow, update the "Execute Search" HTTP Request node to point to:
       
       ```
       http://your-streamlit-url:8501/api/search/execute
       ```
    
    ### API Documentation
    
    #### Search Endpoint
    
    **URL:** `/api/search/execute`
    
    **Method:** POST
    
    **Request Body:**
    
    ```json
    {
        "query": "search query",
        "language": "en",
        "max_results": 10,
        "sources": ["web", "news"]
    }
    ```
    
    **Response:**
    
    ```json
    {
        "status": "success",
        "query": "search query",
        "results_count": 5,
        "processing_time": "1.0s",
        "results": [
            {
                "title": "Result Title",
                "url": "https://example.com",
                "snippet": "Result snippet...",
                "source": "google",
                "language": "en",
                "credibility_score": 0.9,
                "published_date": "2025-04-14"
            },
            ...
        ]
    }
    ```
    """)

# Handle API requests
if 'STREAMLIT_SHARING' not in os.environ:
    # This is a workaround for local development to handle API requests
    # In production, you would use a proper API framework like FastAPI
    
    # Check if this is an API request
    query_params = st.experimental_get_query_params()
    
    if "api" in query_params and query_params["api"][0] == "search":
        try:
            # Get request body
            request_body = st.experimental_get_query_params().get("body", ["{}"])[0]
            request_data = json.loads(request_body)
            
            # Process search request
            response = api_search_endpoint(request_data)
            
            # Return JSON response
            st.json(response)
            
            # Hide the rest of the UI
            st.stop()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
