#!/usr/bin/env python3
"""
Test script to trigger the update_gist_status call to the CrewAI service.
This script can be used to verify if the endpoint is currently functional.
"""

import os
import sys
import argparse
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the CrewAIService
try:
    from Firebase.services import CrewAIService
    from Firebase.services.env_utils import find_and_load_env_file
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def test_update_gist_status(user_id, gist_id, verbose=False, verify_first=True):
    """
    Test the update_gist_status call to the CrewAI service.
    
    Args:
        user_id: The user ID
        gist_id: The gist ID
        verbose: Whether to print verbose output
        verify_first: Whether to verify the gist exists first
    
    Returns:
        True if the call was successful, False otherwise
    """
    try:
        # Load environment variables
        find_and_load_env_file()
        
        # Initialize the CrewAI service client
        crew_ai_service = CrewAIService()
        
        if verbose:
            logger.info(f"Base URL: {crew_ai_service.base_url}")
            logger.info(f"API Key: {'Set' if crew_ai_service.api_key else 'Not set'}")
        
        # First, verify the gist exists if requested
        if verify_first:
            logger.info(f"Verifying gist exists for user_id={user_id}, gist_id={gist_id}")
            try:
                gist_response = crew_ai_service.get_user_gist(user_id, gist_id)
                logger.info(f"Gist verification response: {json.dumps(gist_response, indent=2)}")
            except Exception as e:
                logger.error(f"Error verifying gist: {str(e)}")
                logger.error("The gist may not exist or there may be an issue with the API.")
                return False
        
        # Call the CrewAI service to update the gist status
        logger.info(f"Calling update_gist_status for user_id={user_id}, gist_id={gist_id}")
        response = crew_ai_service.update_gist_status(user_id, gist_id)
        
        # Print the response
        if verbose:
            logger.info(f"Response: {json.dumps(response, indent=2)}")
        else:
            logger.info(f"Response: {response}")
        
        # Check if the response indicates success
        if isinstance(response, dict) and response.get('error'):
            error_message = response.get('error')
            logger.error(f"Error: {error_message}")
            return False
        
        logger.info("Call was successful!")
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test the update_gist_status call to the CrewAI service.')
    parser.add_argument('--user-id', type=str, default="test_user_postman", help='The user ID')
    parser.add_argument('--gist-id', type=str, default="gist_c84ccdd40a5c4a95ac8afe58fd9750b1", help='The gist ID')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    parser.add_argument('--no-verify', action='store_true', help='Skip gist verification')
    
    args = parser.parse_args()
    
    # Test the update_gist_status call
    success = test_update_gist_status(args.user_id, args.gist_id, args.verbose, not args.no_verify)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 