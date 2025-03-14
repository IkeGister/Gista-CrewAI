"""
CrewAI Service Client - Updated for Subcollections

This module provides a client for interacting with the CrewAI backend service
using the subcollection-based database structure.
It handles all service-to-service communication with the CrewAI backend.
"""

import os
import time
import requests
import logging
from typing import Dict, List, Optional, Union, Any
from Firebase.services.env_utils import find_and_load_env_file, get_env_with_fallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
find_and_load_env_file()

class CrewAIService:
    """
    Client for interacting with the CrewAI backend service using subcollections.
    
    This class provides methods for retrieving and updating user gists.
    It handles authentication, request retries, and error handling.
    """
    
    def __init__(self):
        """
        Initialize the CrewAI service client.
        
        Loads configuration from environment variables:
        - CREW_AI_API_BASE_URL: Base URL for the CrewAI API
        - SERVICE_API_KEY: API key for service-to-service authentication
        - API_MAX_RETRIES: Maximum number of retries for failed requests (default: 3)
        - API_RETRY_DELAY: Delay between retries in seconds (default: 1)
        """
        # Get configuration from environment variables
        default_url = "https://api-yufqiolzaa-uc.a.run.app"  # Base URL without /api
        self.base_url = get_env_with_fallback('CREW_AI_API_BASE_URL', 'API_BASE_URL', default_url)
        
        # Remove trailing /api from base_url if present
        if self.base_url.endswith('/api'):
            self.base_url = self.base_url[:-4]
            logger.info(f"Removed trailing /api from base URL: {self.base_url}")
            
        self.api_key = os.getenv('SERVICE_API_KEY')
        if not self.api_key:
            logger.error("SERVICE_API_KEY environment variable is not set")
            
        self.max_retries = int(os.getenv('API_MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('API_RETRY_DELAY', '1'))
        
        # Set up headers for authentication
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key  # Updated to match documentation
        }
        
        logger.info(f"CrewAI service client initialized with base URL: {self.base_url}")
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None, timeout: int = 30) -> Dict:
        """
        Make an HTTP request to the CrewAI API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path
            data: Request body data (for POST/PUT requests)
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: If the request fails after all retries
        """
        if not self.api_key:
            raise ValueError("SERVICE_API_KEY environment variable is not set")
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=timeout
                )
                
                # Raise an exception for 4xx/5xx status codes
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Wait before retrying
                    time.sleep(self.retry_delay)
                else:
                    # Last attempt failed, re-raise the exception
                    raise Exception(f"Request to {url} failed after {self.max_retries} attempts: {str(e)}")
    
    def get_user_gists(self, user_id: str) -> Dict:
        """
        Get all gists for a user from the gists subcollection.
        
        Args:
            user_id: The user ID to get gists for
            
        Returns:
            Dictionary containing user gists data
        """
        logger.info(f"Getting gists for user: {user_id}")
        # Using the subcollection endpoint
        return self._make_request('GET', f'/api/gists/{user_id}')
    
    def get_user_gist(self, user_id: str, gist_id: str) -> Dict:
        """
        Get a specific gist by ID from the gists subcollection.
        
        Args:
            user_id: The user ID
            gist_id: The gist ID to retrieve
            
        Returns:
            Dictionary containing gist data
        """
        logger.info(f"Getting gist with ID: {gist_id} for user: {user_id}")
        # Using the subcollection endpoint
        return self._make_request('GET', f'/api/gists/{user_id}/{gist_id}')
    
    def update_gist_status(self, user_id: str, gist_id: str, 
                          inProduction: bool = None, production_status: str = None) -> Dict:
        """
        Update the status of a gist using the signal-based API.
        
        This is a signal-based endpoint where:
        1. No request body is required - simply making the PUT request triggers the status update
        2. The server handles setting `inProduction: true` and `production_status: "Reviewing Content"` internally
        3. When successful, the response includes the link URL string in the response body
        
        Args:
            user_id: The user ID
            gist_id: The gist ID to update
            inProduction: Ignored (kept for backward compatibility)
            production_status: Ignored (kept for backward compatibility)
            
        Returns:
            Dictionary containing the updated gist data or error information
        """
        logger.info(f"Triggering status update for gist {gist_id} of user {user_id}")
        
        try:
            # Signal-based approach - empty JSON object
            return self._make_request('PUT', f'/api/gists/{user_id}/{gist_id}/status', data={})
        except Exception as e:
            logger.error(f"Error updating gist status: {str(e)}")
            return {"error": str(e)}
        
    def batch_update_gists(self, user_id: str, gist_ids: List[str],
                          inProduction: bool = True, production_status: str = "review") -> Dict:
        """
        Update the status of multiple gists in the gists subcollection.
        
        Args:
            user_id: The user ID
            gist_ids: List of gist IDs to update
            inProduction: Whether the gists are in production
            production_status: Current production status (must be one of: draft, review, published)
            
        Returns:
            Dictionary containing the updated gists data
        """
        logger.info(f"Batch updating {len(gist_ids)} gists for user {user_id}")
        
        # Ensure production_status is one of the valid values
        valid_statuses = ['draft', 'review', 'published']
        if production_status not in valid_statuses:
            production_status = 'review'  # Default to 'review' if invalid
        
        data = {
            "gistIds": gist_ids,
            "inProduction": inProduction,
            "production_status": production_status
        }
        
        try:
            return self._make_request('PUT', f'/api/gists/{user_id}/batch/status', data=data)
        except Exception as e:
            logger.error(f"Error batch updating gists: {str(e)}")
            return {"error": str(e)}
    
    def update_gist_with_links(self, user_id: str, gist_id: str, links: List[Dict],
                              inProduction: bool = True, production_status: str = "review") -> Dict:
        """
        Update a gist with links and status in the subcollection structure.
        
        Args:
            user_id: The user ID
            gist_id: The gist ID to update
            links: List of link objects to add to the gist
            inProduction: Whether the gist is in production
            production_status: Current production status (must be one of: draft, review, published)
            
        Returns:
            Dictionary containing the updated gist data
        """
        logger.info(f"Updating gist {gist_id} with {len(links)} links for user {user_id}")
        
        # Ensure production_status is one of the valid values
        valid_statuses = ['draft', 'review', 'published']
        if production_status not in valid_statuses:
            production_status = 'review'  # Default to 'review' if invalid
        
        data = {
            "links": links,
            "inProduction": inProduction,
            "production_status": production_status
        }
        
        try:
            return self._make_request('PUT', f'/api/gists/{user_id}/{gist_id}/with-links', data=data)
        except Exception as e:
            logger.error(f"Error updating gist with links: {str(e)}")
            return {"error": str(e)}
    
    def get_user_links(self, user_id: str) -> Dict:
        """
        Get all links for a user from the links subcollection.
        
        Args:
            user_id: The user ID to get links for
            
        Returns:
            Dictionary containing user links data
        """
        logger.info(f"Getting links for user: {user_id}")
        return self._make_request('GET', f'/api/links/{user_id}')
    
    def get_gist_links(self, user_id: str, gist_id: str) -> Dict:
        """
        Get all links for a specific gist from the gist's links subcollection.
        
        Args:
            user_id: The user ID
            gist_id: The gist ID to get links for
            
        Returns:
            Dictionary containing links data for the gist
        """
        logger.info(f"Getting links for gist {gist_id} of user {user_id}")
        return self._make_request('GET', f'/api/gists/{user_id}/{gist_id}/links')
    
    def add_link_to_gist(self, user_id: str, gist_id: str, link_data: Dict) -> Dict:
        """
        Add a link to a specific gist in the gist's links subcollection.
        
        Args:
            user_id: The user ID
            gist_id: The gist ID to add the link to
            link_data: Link data to add
            
        Returns:
            Dictionary containing the added link data
        """
        logger.info(f"Adding link to gist {gist_id} for user {user_id}")
        return self._make_request('POST', f'/api/gists/{user_id}/{gist_id}/links', data=link_data)
    
    def add_general_link(self, user_id: str, link_data: Dict) -> Dict:
        """
        Add a general link to the user's links subcollection.
        
        Args:
            user_id: The user ID
            link_data: Link data to add
            
        Returns:
            Dictionary containing the added link data
        """
        logger.info(f"Adding general link for user {user_id}")
        return self._make_request('POST', f'/api/links/{user_id}', data=link_data) 