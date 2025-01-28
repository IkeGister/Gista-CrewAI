import requests
import os
from dotenv import load_dotenv

load_dotenv()

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
