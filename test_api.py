import requests
import json
import sys

def test_api(base_url):
    """
    Test the API endpoints to verify they are working correctly.
    """
    print(f"Testing API at {base_url}...")
    
    # Test the register endpoint
    test_register(base_url)
    
    # Test the login endpoint
    test_login(base_url)
    
    print("All tests completed.")

def test_register(base_url):
    """
    Test the register endpoint.
    """
    print("\nTesting /api/auth/register endpoint...")
    
    # First, try a GET request to get endpoint info
    try:
        response = requests.get(f"{base_url}/api/auth/register")
        print(f"GET /api/auth/register status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing register endpoint (GET): {str(e)}")
    
    # Then, try a POST request with test data
    try:
        test_data = {
            "phone_number": f"+1234567890",
            "name": "Test User",
            "email": f"test{int(time.time())}@example.com",  # Use timestamp to avoid duplicate emails
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"POST /api/auth/register status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing register endpoint (POST): {str(e)}")

def test_login(base_url):
    """
    Test the login endpoint.
    """
    print("\nTesting /api/auth/login endpoint...")
    
    # First, try a GET request to get endpoint info
    try:
        response = requests.get(f"{base_url}/api/auth/login")
        print(f"GET /api/auth/login status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing login endpoint (GET): {str(e)}")
    
    # Then, try a POST request with test data
    try:
        test_data = {
            "phone_number": "+1234567890",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"POST /api/auth/login status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing login endpoint (POST): {str(e)}")

if __name__ == "__main__":
    import time
    
    # Use command line argument for base URL if provided, otherwise use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    test_api(base_url)
