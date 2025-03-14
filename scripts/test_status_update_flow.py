#!/usr/bin/env python3
"""
Test script for the complete gist status update flow:
1. Create a test user using the client-facing Gista-CrewAI server
2. Add an article with auto_create_gist=true using the client-facing server to get a gistId
3. Update the status of the created gist using the server-facing CrewAI-Backend service
"""

import os
import sys
import logging
import json
import requests
import time
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the env_utils and CrewAIService
try:
    from Firebase.services import CrewAIService
    from Firebase.services.env_utils import find_and_load_env_file
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def generate_test_id():
    """Generate a unique test ID"""
    return str(int(time.time())) + "_" + str(uuid.uuid4())[:8]

def main():
    """Main function"""
    # Load environment variables
    find_and_load_env_file()
    
    # Use the local Flask server URL for client-facing operations
    client_api_url = "http://localhost:5001/api"
    
    # Print configuration
    logger.info(f"Client API URL: {client_api_url}")
    
    # Set up headers for client API
    client_headers = {
        'Content-Type': 'application/json'
    }
    
    # Generate a test ID for this run
    test_id = generate_test_id()
    logger.info(f"Test ID: {test_id}")
    
    # Step 1: Create a test user using the client-facing server
    user_id = f"test_user_{test_id}"
    logger.info(f"Step 1: Creating test user with ID: {user_id} using client-facing server")
    
    user_data = {
        "user_id": user_id,
        "email": f"{user_id}@example.com",
        "username": f"Test User {test_id}"
    }
    
    try:
        user_response = requests.post(
            f"{client_api_url}/auth/create_user",
            headers=client_headers,
            json=user_data
        )
        
        if user_response.status_code not in [200, 201]:
            logger.error(f"Failed to create test user: {user_response.text}")
            return 1
        
        logger.info(f"Test user created: {user_response.text}")
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        return 1
    
    # Step 2: Create a link with auto_create_gist=true using the client-facing server
    logger.info(f"Step 2: Creating a link with auto_create_gist=true for user: {user_id} using client-facing server")
    
    link_data = {
        "user_id": user_id,
        "link": {
            "url": f"https://example.com/test-article-{test_id}",
            "title": f"Test Article {test_id}",
            "gist_created": {
                "url": f"https://example.com/test-article-{test_id}",
                "link_title": f"Test Article {test_id}",
                "image_url": "https://example.com/image.jpg"
            },
            "category": "Test"
        },
        "auto_create_gist": True
    }
    
    try:
        link_response = requests.post(
            f"{client_api_url}/links/store",
            headers=client_headers,
            json=link_data
        )
        
        if link_response.status_code != 200:
            logger.error(f"Failed to create link with auto_create_gist: {link_response.text}")
            # Clean up: Delete the test user
            delete_user(client_api_url, client_headers, user_id)
            return 1
        
        # Extract the gist ID from the response
        try:
            response_data = link_response.json()
            gist_id = response_data.get("gistId")
            logger.info(f"Link response: {json.dumps(response_data, indent=2)}")
        except:
            logger.info(f"Link response text: {link_response.text}")
            try:
                # Try to extract gistId from text response
                if "gistId" in link_response.text:
                    import re
                    match = re.search(r'"gistId"\s*:\s*"([^"]+)"', link_response.text)
                    if match:
                        gist_id = match.group(1)
                    else:
                        gist_id = None
                else:
                    gist_id = None
            except:
                gist_id = None
        
        if not gist_id:
            logger.error("No gistId returned in the response")
            # Clean up: Delete the test user
            delete_user(client_api_url, client_headers, user_id)
            return 1
        
        logger.info(f"Link created with auto-created gist ID: {gist_id}")
    except Exception as e:
        logger.error(f"Error creating link: {str(e)}")
        # Clean up: Delete the test user
        delete_user(client_api_url, client_headers, user_id)
        return 1
    
    # Step 3: Update the gist status using the CrewAI service (server-facing)
    logger.info(f"Step 3: Updating gist status for user_id={user_id}, gist_id={gist_id} using CrewAI service")
    
    success = False
    try:
        # Initialize the CrewAI service client
        crew_ai_service = CrewAIService()
        
        logger.info(f"CrewAI service base URL: {crew_ai_service.base_url}")
        logger.info(f"CrewAI service API Key: {'Set' if crew_ai_service.api_key else 'Not set'}")
        
        # Call the update_gist_status method
        response = crew_ai_service.update_gist_status(user_id, gist_id)
        
        # Print the response
        logger.info(f"Response: {json.dumps(response, indent=2)}")
        
        # Check if the response indicates success
        if isinstance(response, dict) and response.get('error'):
            logger.error(f"Error updating gist status: {response.get('error')}")
            success = False
        else:
            logger.info("Gist status update was successful!")
            success = True
    except Exception as e:
        logger.error(f"Error updating gist status: {str(e)}")
        success = False
    
    # Only clean up AFTER the status update is complete
    logger.info("Status update process complete, now cleaning up")
    delete_user(client_api_url, client_headers, user_id)
    
    return 0 if success else 1

def delete_user(api_url, headers, user_id):
    """Delete a test user"""
    logger.info(f"Cleaning up: Deleting test user: {user_id}")
    
    try:
        delete_response = requests.delete(
            f"{api_url}/auth/delete_user/{user_id}",
            headers=headers
        )
        
        if delete_response.status_code != 200:
            logger.warning(f"Failed to delete test user: {delete_response.text}")
        else:
            logger.info("Test user deleted successfully")
    except Exception as e:
        logger.warning(f"Error deleting test user: {str(e)}")

if __name__ == "__main__":
    sys.exit(main()) 