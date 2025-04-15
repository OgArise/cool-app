import requests
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
