#!/usr/bin/env python3
"""
Test script to check if a user exists in the CrewAI service by listing their gists.
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

def test_get_user_gists(user_id, verbose=False):
    """
    Test the get_user_gists call to the CrewAI service.
    
    Args:
        user_id: The user ID
        verbose: Whether to print verbose output
    
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
        
        # Call the CrewAI service to get user gists
        logger.info(f"Getting gists for user_id={user_id}")
        response = crew_ai_service.get_user_gists(user_id)
        
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
    parser = argparse.ArgumentParser(description='Test the get_user_gists call to the CrewAI service.')
    parser.add_argument('--user-id', type=str, default="test_user_postman", help='The user ID')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    # Test the get_user_gists call
    success = test_get_user_gists(args.user_id, args.verbose)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 