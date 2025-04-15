import os

# Create .env file with placeholder values
env_content = """# RapidAPI Key (for Free Search API)
RAPIDAPI_KEY=your_rapidapi_key

# Google Search API
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_google_custom_search_engine_id

# Baidu Search API
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
"""

# Write .env file
with open(".env", "w") as f:
    f.write(env_content)

print("Created .env file with placeholder values")

# Create requirements.txt
requirements = """streamlit==1.32.0
requests==2.31.0
python-dotenv==1.0.0
"""

# Write requirements.txt
with open("requirements.txt", "w") as f:
    f.write(requirements)

print("Created requirements.txt file")

# Create README.md
readme = """# AI Analyst Search Backend

This Streamlit application provides a search backend for the AI Analyst Agent. It can be used to test the n8n search workflow by providing a compatible API endpoint.

## Features

- Multiple search API options:
  - Free Search API (fallback to mock data if no API key)
  - Google Custom Search API (requires API key and CX)
  - Baidu Search API (requires API key and secret key)

- API endpoint compatible with n8n search workflow
- Result caching to improve performance
- Multilingual search support

## Setup Instructions

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**

   Update the `.env` file with your API keys:
   
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

3. **Running the App**

   ```bash
   streamlit run app.py
   ```

4. **Connecting to n8n**

   In your n8n search workflow, update the "Execute Search" HTTP Request node to point to:
   
   ```
   http://localhost:8501/api/search/execute
   ```
   
   Or if you're running this on a different machine:
   
   ```
   http://<your-ip-address>:8501/api/search/execute
   ```

## API Documentation

### Search Endpoint

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

## Getting API Keys

### RapidAPI Key (for Free Search API)
1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to the [DuckDuckGo API](https://rapidapi.com/apigeek/api/duckduckgo-zero-click-info)
3. Copy your API key from the dashboard

### Google Custom Search API
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Custom Search API
3. Create API credentials
4. Create a Custom Search Engine at [cse.google.com](https://cse.google.com/cse/all)
5. Get your Search Engine ID (cx)

### Baidu Search API
1. Register at [Baidu AI Cloud](https://cloud.baidu.com/)
2. Create a new application
3. Enable the Search API
4. Get your API key and Secret key

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Verify your API keys are correctly entered in the `.env` file
   - Check if you've reached API usage limits

2. **Connection Issues**
   - Ensure your internet connection is working
   - Check if the API service is available

3. **n8n Integration Issues**
   - Verify the URL in n8n is correct
   - Check that the request format matches what the endpoint expects
"""

# Write README.md
with open("README.md", "w") as f:
    f.write(readme)

print("Created README.md file")

# Create a simple script to test the API endpoint
test_script = """import requests
import json

def test_search_api():
    url = "http://localhost:8501/api/search/execute"
    
    payload = {
        "query": "AI Analyst financial regulations",
        "language": "en",
        "max_results": 5,
        "sources": ["web"]
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("API test successful!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    print("Testing search API endpoint...")
    test_search_api()
"""

# Write test_api.py
with open("test_api.py", "w") as f:
    f.write(test_script)

print("Created test_api.py file")
