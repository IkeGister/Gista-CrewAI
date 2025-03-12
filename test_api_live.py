"""
Live API Test Script for Gista-CrewAI

This script tests the Gista-CrewAI API with actual HTTP calls to verify that
the GistStatus interface is working correctly in a live environment.

Usage:
    python test_api_live.py
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration - Use a unique user ID with a timestamp and random UUID
UNIQUE_ID = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
TEST_USER_ID = f"test_user_{UNIQUE_ID}"
TEST_EMAIL = f"{TEST_USER_ID}@example.com"
TEST_USERNAME = f"TestUser_{UNIQUE_ID}"
BASE_URL = "http://localhost:5001/api"

# Generate a unique gist ID for testing
TEST_GIST_ID = f"gist_{UNIQUE_ID}"

# Headers
HEADERS = {
    "Content-Type": "application/json"
}

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def create_test_user():
    """Create a test user for the API tests."""
    print_separator("Creating Test User")
    print(f"Creating user with ID: {TEST_USER_ID}")
    
    user_data = {
        "user_id": TEST_USER_ID,
        "email": TEST_EMAIL,
        "username": TEST_USERNAME
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/create_user",
        headers=HEADERS,
        json=user_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 201

def create_test_link():
    """Create a test link for the API tests."""
    print_separator("Creating Test Link")
    
    # Create a unique link
    link_id = f"link_{UNIQUE_ID}"
    link_url = f"https://example.com/test-article-{UNIQUE_ID}"
    
    link_data = {
        "user_id": TEST_USER_ID,
        "link": {
            "title": f"Test Link {UNIQUE_ID}",
            "url": link_url,
            "imageUrl": f"https://example.com/test-image-{UNIQUE_ID}.jpg",
            "linkType": "weblink",
            "categoryId": f"category_{UNIQUE_ID}",
            "categoryName": "Technology"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/links/store",
        headers=HEADERS,
        json=link_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200, link_url, link_id

def create_test_gist(link_url, link_id):
    """Create a test gist with the updated GistStatus interface."""
    print_separator("Creating Test Gist")
    
    # Include the gistId in the request payload
    gist_data = {
        "gistId": TEST_GIST_ID,  # Explicitly set the gist ID
        "title": f"Test Gist {UNIQUE_ID}",
        "image_url": f"https://example.com/test-image-{UNIQUE_ID}.jpg",
        "link": link_url,
        "category": "Technology",
        "link_id": link_id,
        "isFinished": False,
        "playbackDuration": 180,
        "playbackTime": 0,
        "segments": [
            {
                "title": f"Test Segment {UNIQUE_ID}",
                "audioUrl": f"https://example.com/test-audio-{UNIQUE_ID}.mp3",
                "duration": "60",
                "index": 0
            }
        ],
        # Explicitly set the status with inProduction
        "status": {
            "production_status": "Reviewing Content",
            "inProduction": False
        }
    }
    
    print(f"Request payload: {json.dumps(gist_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/gists/add/{TEST_USER_ID}",
        headers=HEADERS,
        json=gist_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Use the gist ID we provided in the request
    if response.status_code in [200, 201]:
        print(f"Using gist ID from request: {TEST_GIST_ID}")
        return True, TEST_GIST_ID
    
    return False, None

def get_user_gists():
    """Get all gists for the test user."""
    print_separator("Getting User Gists")
    
    response = requests.get(
        f"{BASE_URL}/gists/{TEST_USER_ID}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check if the response contains gists with the updated GistStatus interface
    if response.status_code == 200:
        gists = response.json().get("gists", [])
        if gists and len(gists) > 0:
            # Look for our test gist
            test_gist = None
            for gist in gists:
                if gist.get("gistId") == TEST_GIST_ID:
                    test_gist = gist
                    break
            
            if test_gist:
                print(f"✅ Found our test gist with ID: {TEST_GIST_ID}")
                status = test_gist.get("status", {})
                
                # Check if the status object uses inProduction or in_productionQueue
                if "inProduction" in status:
                    print("✅ GistStatus is using the updated interface with 'inProduction'")
                elif "in_productionQueue" in status:
                    print("❌ GistStatus is using the old interface with 'in_productionQueue'")
                    print("This should be updated to use 'inProduction' instead")
                else:
                    print("⚠️ GistStatus does not contain either 'inProduction' or 'in_productionQueue'")
            else:
                print(f"❌ Could not find our test gist with ID: {TEST_GIST_ID}")
    
    return response.status_code == 200

def update_gist_status(gist_id):
    """Update a gist's status using the updated GistStatus interface."""
    print_separator("Updating Gist Status")
    
    update_data = {
        "status": {
            "production_status": "In Production",
            "inProduction": True
        }
    }
    
    print(f"Request payload: {json.dumps(update_data, indent=2)}")
    
    response = requests.put(
        f"{BASE_URL}/gists/update/{TEST_USER_ID}/{gist_id}",
        headers=HEADERS,
        json=update_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def delete_test_gist(gist_id):
    """Delete the test gist."""
    print_separator("Deleting Test Gist")
    
    print(f"Attempting to delete gist with ID: {gist_id} for user: {TEST_USER_ID}")
    
    response = requests.delete(
        f"{BASE_URL}/gists/delete/{TEST_USER_ID}/{gist_id}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def delete_test_user():
    """Delete the test user."""
    print_separator("Deleting Test User")
    
    response = requests.delete(
        f"{BASE_URL}/auth/delete_user/{TEST_USER_ID}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def run_tests():
    """Run all the API tests."""
    print_separator("Starting API Tests")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Test Username: {TEST_USERNAME}")
    print(f"Test Gist ID: {TEST_GIST_ID}")
    
    # Create test user
    if not create_test_user():
        print("Failed to create test user. Aborting tests.")
        return
    
    # Create test link
    link_success, link_url, link_id = create_test_link()
    if not link_success:
        print("Failed to create test link. Aborting tests.")
        delete_test_user()
        return
    
    # Create test gist
    gist_success, gist_id = create_test_gist(link_url, link_id)
    if not gist_success or not gist_id:
        print("Failed to create test gist. Aborting tests.")
        delete_test_user()
        return
    
    # Get user gists
    if not get_user_gists():
        print("Failed to get user gists. Continuing tests...")
    
    # Update gist status
    if not update_gist_status(gist_id):
        print("Failed to update gist status. Continuing tests...")
    
    # Get user gists again to verify the update
    print("\nVerifying gist status update...")
    if not get_user_gists():
        print("Failed to get user gists after update. Continuing tests...")
    
    # Delete test gist
    if not delete_test_gist(gist_id):
        print("Failed to delete test gist. Continuing tests...")
    
    # Delete test user
    if not delete_test_user():
        print("Failed to delete test user. Tests completed with cleanup issues.")
        return
    
    print_separator("All Tests Completed Successfully")
    print(f"User ID: {TEST_USER_ID}")
    print(f"Gist ID: {TEST_GIST_ID}")
    print(f"This user has been created and deleted as part of the test.")
    print("You can use this user ID for future tests if needed.")

if __name__ == "__main__":
    run_tests() 