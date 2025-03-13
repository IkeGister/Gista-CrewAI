"""
Auto-Create Gist Integration Test Script for Gista-CrewAI

This script tests the enhanced `/api/links/store` endpoint that automatically
creates a gist when a link is stored.

Usage:
    python test_auto_create_gist.py
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001/api"
HEADERS = {
    "Content-Type": "application/json"
}

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def create_test_user(test_id):
    """Create a test user for the API tests."""
    user_id = f"test_user_{test_id}"
    print_separator(f"Creating Test User: {user_id}")
    
    user_data = {
        "user_id": user_id,
        "email": f"{user_id}@example.com",
        "username": f"TestUser_{test_id}"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/create_user",
        headers=HEADERS,
        json=user_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code in [200, 201, 400], user_id

def test_with_auto_create_gist(user_id, test_id):
    """Test storing a link with auto_create_gist=true."""
    print_separator("Testing with auto_create_gist=true")
    
    link = {
        "category": "Technology",
        "gist_created": {
            "link_title": f"Test Link {test_id}",
            "url": f"https://example.com/test-article-{test_id}",
            "image_url": f"https://example.com/test-image-{test_id}.jpg"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/links/store",
        headers=HEADERS,
        json={
            "user_id": user_id,
            "link": link,
            "auto_create_gist": True
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Verify the response format
    if response.status_code == 200:
        data = response.json()
        if "gistId" in data:
            print("✅ Response contains gistId as expected")
            gist_id = data["gistId"]
            
            # Verify the gist was created
            time.sleep(1)  # Wait for the gist to be created
            verify_gist_created(user_id, gist_id)
            
            # Verify the link's gist_created status was updated
            verify_link_updated(user_id, gist_id)
            
            return True, gist_id
        else:
            print("❌ Response does not contain gistId")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
    
    return False, None

def test_without_auto_create_gist(user_id, test_id):
    """Test storing a link with auto_create_gist=false."""
    print_separator("Testing with auto_create_gist=false")
    
    link = {
        "category": "Technology",
        "gist_created": {
            "link_title": f"Test Link No Gist {test_id}",
            "url": f"https://example.com/test-article-no-gist-{test_id}",
            "image_url": f"https://example.com/test-image-no-gist-{test_id}.jpg"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/links/store",
        headers=HEADERS,
        json={
            "user_id": user_id,
            "link": link,
            "auto_create_gist": False
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Verify the response format
    if response.status_code == 200:
        data = response.json()
        if "message" in data and data["message"] == "Link stored successfully":
            print("✅ Response contains success message as expected")
            if "gistId" not in data:
                print("✅ Response does not contain gistId as expected")
                
                # Verify no gist was created for this link
                verify_no_gist_created(user_id, link)
                
                return True
            else:
                print("❌ Response contains gistId when it shouldn't")
        else:
            print("❌ Response does not contain expected success message")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
    
    return False

def verify_gist_created(user_id, gist_id):
    """Verify that a gist was created for the user."""
    print_separator(f"Verifying Gist Creation: {gist_id}")
    
    response = requests.get(
        f"{BASE_URL}/gists/{user_id}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if "gists" in data:
            gists = data["gists"]
            for gist in gists:
                if gist.get("gistId") == gist_id:
                    print(f"✅ Found gist with ID: {gist_id}")
                    
                    # Check if the gist has the correct status
                    status = gist.get("status", {})
                    if "inProduction" in status:
                        print("✅ Gist has inProduction field")
                    else:
                        print("❌ Gist is missing inProduction field")
                    
                    if "production_status" in status:
                        print(f"✅ Gist has production_status: {status['production_status']}")
                    else:
                        print("❌ Gist is missing production_status field")
                    
                    return True
            
            print(f"❌ Could not find gist with ID: {gist_id}")
        else:
            print("❌ Response does not contain gists array")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
    
    return False

def verify_link_updated(user_id, gist_id):
    """Verify that the link's gist_created status was updated."""
    print_separator("Verifying Link Update")
    
    response = requests.get(
        f"{BASE_URL}/links/{user_id}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if "links" in data:
            links = data["links"]
            for link in links:
                if link.get("gist_created", {}).get("gist_id") == gist_id:
                    print(f"✅ Found link with gist_id: {gist_id}")
                    
                    # Check if the link's gist_created status was updated
                    if link.get("gist_created", {}).get("gist_created") == True:
                        print("✅ Link's gist_created status is True")
                        return True
                    else:
                        print("❌ Link's gist_created status is not True")
            
            print(f"❌ Could not find link with gist_id: {gist_id}")
        else:
            print("❌ Response does not contain links array")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
    
    return False

def verify_no_gist_created(user_id, link):
    """Verify that no gist was created for the link."""
    print_separator("Verifying No Gist Created")
    
    # Get the user's gists
    response = requests.get(
        f"{BASE_URL}/gists/{user_id}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if "gists" in data:
            gists = data["gists"]
            link_url = link.get("gist_created", {}).get("url")
            
            for gist in gists:
                if gist.get("link") == link_url:
                    print(f"❌ Found gist with link URL: {link_url}")
                    return False
            
            print(f"✅ No gist found with link URL: {link_url}")
            return True
        else:
            print("✅ Response does not contain gists array")
            return True
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
    
    return False

def delete_test_user(user_id):
    """Delete the test user."""
    print_separator(f"Deleting Test User: {user_id}")
    
    response = requests.delete(
        f"{BASE_URL}/auth/delete_user/{user_id}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def run_tests():
    """Run all the tests."""
    # Generate a unique test ID
    test_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    print_separator(f"Starting Tests with ID: {test_id}")
    
    # Create a test user
    user_created, user_id = create_test_user(test_id)
    if not user_created:
        print("❌ Failed to create test user. Aborting tests.")
        return
    
    try:
        # Test with auto_create_gist=true
        success_with_gist, gist_id = test_with_auto_create_gist(user_id, test_id)
        if not success_with_gist:
            print("❌ Test with auto_create_gist=true failed.")
        
        # Test with auto_create_gist=false
        success_without_gist = test_without_auto_create_gist(user_id, test_id)
        if not success_without_gist:
            print("❌ Test with auto_create_gist=false failed.")
        
        # Print overall test results
        print_separator("Test Results")
        if success_with_gist and success_without_gist:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed.")
            if not success_with_gist:
                print("  - Test with auto_create_gist=true failed")
            if not success_without_gist:
                print("  - Test with auto_create_gist=false failed")
    
    finally:
        # Clean up: Delete the test user
        if delete_test_user(user_id):
            print(f"✅ Test user {user_id} deleted successfully")
        else:
            print(f"❌ Failed to delete test user {user_id}")

if __name__ == "__main__":
    run_tests() 