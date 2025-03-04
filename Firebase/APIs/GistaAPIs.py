import requests
import os
from dotenv import load_dotenv
from flask import jsonify, request

load_dotenv()

def handle_storage_request(request):
    """
    Handle storage-related requests
    Routes to the appropriate endpoint based on the path
    """
    path = request.path.strip('/').replace('storage/', '')
    method = request.method
    
    # Initialize the API client
    api = GistaAPIs()
    
    # Extract user_id from request if available
    data = request.json or {}
    user_id = data.get('user_id')
    
    if path == 'gists' and method == 'GET' and user_id:
        return jsonify(api.get_user_gists(user_id))
    elif path == 'gist/update' and method == 'POST':
        return jsonify(api.update_gist(user_id, data.get('gist_data')))
    elif path == 'gist/delete' and method == 'POST':
        return jsonify(api.delete_gist(user_id, data.get('gist_id')))
    else:
        return jsonify({'error': 'Invalid storage endpoint'}), 404

class GistaAPIs:
    BASE_URL = os.getenv(
        'API_BASE_URL',
        'http://localhost:5001'  # Default to localhost for development
    )

    def sign_in(self, id_token):
        """Sign in a user using the provided ID token."""
        url = f"{self.BASE_URL}/auth/signin"
        try:
            print(f"Making request to {url}")
            response = requests.post(
                url,
                json={"id_token": id_token},
                timeout=30
            )
            response.raise_for_status()
            print(f"Response received: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error in GistaAPIs.sign_in: {str(e)}")
            return type('Response', (), {
                'status_code': 500,
                'json': lambda: {"error": str(e)}
            })()

    def update_link(self, user_id, link):
        """Update a user's links."""
        url = f"{self.BASE_URL}/links/store"
        try:
            response = requests.post(
                url, 
                json={"user_id": user_id, "link": link},
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            return type('Response', (), {'status_code': 500, 'json': lambda: {"error": str(e)}})()

    def update_gist(self, user_id, gist_data):
        """Update a user's gists."""
        url = f"{self.BASE_URL}/gists/add/{user_id}"
        try:
            response = requests.post(
                url, 
                json=gist_data,
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            return type('Response', (), {'status_code': 500, 'json': lambda: {"error": str(e)}})()

    def get_user_gists(self, user_id):
        """Get all gists for a user."""
        url = f"{self.BASE_URL}/gists/{user_id}"
        try:
            response = requests.get(
                url,
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            return type('Response', (), {'status_code': 500, 'json': lambda: {"error": str(e)}})()

    def delete_gist(self, user_id, gist_id):
        """Delete a specific gist for a user."""
        url = f"{self.BASE_URL}/gists/delete/{user_id}/{gist_id}"
        try:
            response = requests.delete(
                url,
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            return type('Response', (), {'status_code': 500, 'json': lambda: {"error": str(e)}})()

    def delete_user(self, user_id):
        """Delete a user and all their data."""
        url = f"{self.BASE_URL}/auth/delete_user/{user_id}"
        try:
            response = requests.delete(
                url,
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            return type('Response', (), {'status_code': 500, 'json': lambda: {"error": str(e)}})()
