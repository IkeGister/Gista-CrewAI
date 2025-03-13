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

def create_test_link_with_auto_gist():
    """Create a test link with auto_create_gist=true."""
    print_separator("Creating Test Link with Auto-Create Gist")
    
    # Create a unique link
    link_id = f"link_{UNIQUE_ID}"
    link_url = f"https://example.com/test-article-{UNIQUE_ID}"
    
    link_data = {
        "user_id": TEST_USER_ID,
        "link": {
            "category": "Technology",
            "gist_created": {
                "link_title": f"Test Link {UNIQUE_ID}",
                "url": link_url,
                "image_url": f"https://example.com/test-image-{UNIQUE_ID}.jpg",
                "link_id": link_id
            }
        },
        "auto_create_gist": True  # Explicitly set to true
    }
    
    response = requests.post(
        f"{BASE_URL}/links/store",
        headers=HEADERS,
        json=link_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check for the ultra-minimal response format
    if response.status_code == 200:
        data = response.json()
        if "gistId" in data:
            print("✅ Response contains gistId as expected")
            gist_id = data["gistId"]
            return True, link_url, link_id, gist_id
        else:
            print("❌ Response does not contain gistId")
    
    return False, None, None, None

def create_test_link_without_auto_gist():
    """Create a test link with auto_create_gist=false."""
    print_separator("Creating Test Link without Auto-Create Gist")
    
    # Create a unique link
    link_id = f"link_no_gist_{UNIQUE_ID}"
    link_url = f"https://example.com/test-article-no-gist-{UNIQUE_ID}"
    
    link_data = {
        "user_id": TEST_USER_ID,
        "link": {
            "category": "Technology",
            "gist_created": {
                "link_title": f"Test Link No Gist {UNIQUE_ID}",
                "url": link_url,
                "image_url": f"https://example.com/test-image-no-gist-{UNIQUE_ID}.jpg",
                "link_id": link_id
            }
        },
        "auto_create_gist": False  # Explicitly set to false
    }
    
    response = requests.post(
        f"{BASE_URL}/links/store",
        headers=HEADERS,
        json=link_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check for the ultra-minimal response format
    if response.status_code == 200:
        data = response.json()
        if "message" in data and data["message"] == "Link stored successfully":
            print("✅ Response contains success message as expected")
            return True, link_url, link_id
        else:
            print("❌ Response does not contain expected success message")
    
    return False, None, None

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
            print(f"✅ Found {len(gists)} gists for user {TEST_USER_ID}")
            
            # Check each gist for the updated GistStatus interface
            for gist in gists:
                status = gist.get("status", {})
                
                # Check if the status object uses inProduction or in_productionQueue
                if "inProduction" in status:
                    print(f"✅ Gist {gist.get('gistId')} is using the updated interface with 'inProduction'")
                elif "in_productionQueue" in status:
                    print(f"❌ Gist {gist.get('gistId')} is using the old interface with 'in_productionQueue'")
                    print("This should be updated to use 'inProduction' instead")
                else:
                    print(f"⚠️ Gist {gist.get('gistId')} does not contain either 'inProduction' or 'in_productionQueue'")
        else:
            print(f"ℹ️ No gists found for user {TEST_USER_ID}")
    
    return response.status_code == 200, response.json().get("gists", [])

def get_user_links():
    """Get all links for the test user."""
    print_separator("Getting User Links")
    
    response = requests.get(
        f"{BASE_URL}/links/{TEST_USER_ID}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200, response.json().get("links", [])

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

def verify_gist_created(gist_id, gists):
    """Verify that a gist with the given ID exists in the list of gists."""
    for gist in gists:
        if gist.get("gistId") == gist_id:
            print(f"✅ Found gist with ID: {gist_id}")
            return True
    
    print(f"❌ Could not find gist with ID: {gist_id}")
    return False

def verify_link_updated(link_id, gist_id, links):
    """Verify that a link with the given ID has been updated with the gist ID."""
    for link in links:
        if link.get("gist_created", {}).get("link_id") == link_id:
            if link.get("gist_created", {}).get("gist_id") == gist_id:
                print(f"✅ Link {link_id} has been updated with gist ID: {gist_id}")
                return True
            else:
                print(f"❌ Link {link_id} has not been updated with gist ID: {gist_id}")
                return False
    
    print(f"❌ Could not find link with ID: {link_id}")
    return False

def run_tests():
    """Run all the API tests."""
    print_separator("Starting API Tests")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Test Username: {TEST_USERNAME}")
    
    # Create test user
    if not create_test_user():
        print("Failed to create test user. Aborting tests.")
        return
    
    # Test 1: Create a link with auto_create_gist=true
    link_success, link_url, link_id, gist_id = create_test_link_with_auto_gist()
    if not link_success:
        print("Failed to create test link with auto-create gist. Aborting tests.")
        delete_test_user()
        return
    
    # Get user gists to verify the gist was created
    gists_success, gists = get_user_gists()
    if not gists_success:
        print("Failed to get user gists. Continuing tests...")
    else:
        # Verify the gist was created
        if not verify_gist_created(gist_id, gists):
            print("Failed to verify gist creation. Continuing tests...")
    
    # Get user links to verify the link was updated
    links_success, links = get_user_links()
    if not links_success:
        print("Failed to get user links. Continuing tests...")
    else:
        # Verify the link was updated
        if not verify_link_updated(link_id, gist_id, links):
            print("Failed to verify link update. Continuing tests...")
    
    # Update gist status
    if not update_gist_status(gist_id):
        print("Failed to update gist status. Continuing tests...")
    
    # Get user gists again to verify the update
    print("\nVerifying gist status update...")
    gists_success, gists = get_user_gists()
    if not gists_success:
        print("Failed to get user gists after update. Continuing tests...")
    
    # Test 2: Create a link with auto_create_gist=false
    link_success, link_url, link_id = create_test_link_without_auto_gist()
    if not link_success:
        print("Failed to create test link without auto-create gist. Continuing tests...")
    
    # Get user gists again to verify no new gist was created
    print("\nVerifying no new gist was created...")
    gists_success, gists = get_user_gists()
    if not gists_success:
        print("Failed to get user gists after creating link without auto-create gist. Continuing tests...")
    else:
        # Count the number of gists (should still be 1)
        if len(gists) == 1:
            print("✅ No new gist was created as expected")
        else:
            print(f"❌ Expected 1 gist, but found {len(gists)} gists")
    
    # Delete test gist
    if not delete_test_gist(gist_id):
        print("Failed to delete test gist. Continuing tests...")
    
    # Delete test user
    if not delete_test_user():
        print("Failed to delete test user. Tests completed with cleanup issues.")
        return
    
    print_separator("All Tests Completed Successfully")
    print(f"User ID: {TEST_USER_ID}")
    print(f"This user has been created and deleted as part of the test.")

if __name__ == "__main__":
    run_tests() 