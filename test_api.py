# Test Script for Local Development

"""
Bu script API'yi lokal olarak test etmek için kullanılabilir.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Health check testi"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_sentiment_analysis():
    """Duygu analizi testi"""
    print("🔍 Testing sentiment analysis...")
    data = {
        "text": "This product is absolutely amazing! I love it!",
        "language": "en"
    }
    response = requests.post(f"{BASE_URL}/api/v1/sentiment", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_text_classification():
    """Metin sınıflandırma testi"""
    print("🔍 Testing text classification...")
    data = {
        "text": "Apple announced new AI features in their latest iPhone model with advanced machine learning capabilities."
    }
    response = requests.post(f"{BASE_URL}/api/v1/classify", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_chat():
    """Chat completion testi"""
    print("🔍 Testing chat completion...")
    data = {
        "prompt": "What is cloud computing?",
        "max_tokens": 100,
        "temperature": 0.7
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Azure AI FastAPI Demo - API Tests")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_sentiment_analysis()
        test_text_classification()
        test_chat()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API.")
        print("Make sure the API is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
