#!/usr/bin/env python3
"""
Test script to verify the frontend is fetching queries from the backend correctly.
"""
import requests
import json

def test_api_endpoint():
    """Test the /api/example-queries endpoint"""
    try:
        response = requests.get('http://localhost:5004/api/example-queries')
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working!")
            print(f"✅ Success: {data.get('success', False)}")
            print(f"✅ Number of queries returned: {len(data.get('example_queries', []))}")
            print("\n📝 Sample queries:")
            for i, query in enumerate(data.get('example_queries', [])[:5]):
                print(f"  {i+1}. {query}")
            return True
        else:
            print(f"❌ API endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing API endpoint: {e}")
        return False

def test_frontend_accessibility():
    """Test that the frontend is accessible"""
    try:
        response = requests.get('http://localhost:5004')
        if response.status_code == 200:
            print("✅ Frontend is accessible!")
            # Check if the page contains the expected elements
            content = response.text
            if 'recommendedTestQuestions' in content:
                print("✅ Frontend contains the recommended queries container!")
            if 'fetchRecommendedQueries' in content:
                print("✅ Frontend contains the fetch queries function!")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing IntelliPart Frontend Integration")
    print("=" * 50)
    
    api_working = test_api_endpoint()
    print()
    frontend_working = test_frontend_accessibility()
    
    print("\n📋 Summary:")
    print("=" * 50)
    if api_working and frontend_working:
        print("✅ All tests passed! The frontend should now display dataset-specific queries.")
        print("🌐 Visit http://localhost:5004 to see the updated recommended queries.")
    else:
        print("❌ Some tests failed. Please check the issues above.")
