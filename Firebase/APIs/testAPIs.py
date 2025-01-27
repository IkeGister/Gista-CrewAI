import unittest
from flask import Flask
from Firebase.APIs.auth import auth_bp
from Firebase.APIs.links import links_bp
import requests
import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv
from firebase_admin import firestore

class FirebaseAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up once for all tests"""
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment
        cls.test_email = "nlemadimTony@gmail.com"
        cls.test_password = os.getenv("FIREBASE_TEST_USER_PASSWORD")  # Add this to your .env file
        cls.api_key = os.getenv("FIREBASE_API_KEY")
        
        # Initialize Firebase Admin SDK using environment variables
        cred = credentials.Certificate({
            "type": os.getenv("FIREBASE_TYPE", "service_account"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
        })

        try:
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
                'apiKey': cls.api_key  # Add API key to the config
            })
        except ValueError:
            # App already initialized
            pass

        # Get test user token
        cls.test_user = auth.get_user_by_email(cls.test_email)
        cls.custom_token = auth.create_custom_token(cls.test_user.uid)
        cls.test_user_id = cls.test_user.uid

        # Pre-initialize test data
        cls.test_user_ref = firestore.client().collection('users').document(cls.test_user_id)
        if not cls.test_user_ref.get().exists:
            cls.test_user_ref.set({
                'email': cls.test_email,
                'username': "TonyNlemadim",
                'gists': [],
                'links': []
            })

    def setUp(self):
        """Set up Flask test client before each test"""
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(links_bp)
        self.client = self.app.test_client()
        
        # Store the base URL for API requests
        self.base_url = "http://localhost:5001/api"
        
        # Add headers with API key for requests
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def test_sign_in(self):
        """Test user sign-in functionality with real credentials"""
        try:
            # First get an ID token by signing in with email/password
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
            auth_response = requests.post(
                auth_url,
                json={
                    "email": self.test_email,
                    "password": self.test_password,
                    "returnSecureToken": True
                },
                timeout=30  # Increased timeout
            )
            auth_response.raise_for_status()
            id_token = auth_response.json()['idToken']
            
            # Now use this ID token to sign in to your app
            response = requests.post(
                f"{self.base_url}/auth/signin",
                json={"id_token": id_token},
                headers=self.headers,
                timeout=30  # Increased timeout
            )
            
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertIn("email", response_data)
            self.assertIn("user_id", response_data)
            self.assertEqual(response_data["email"], self.test_email)
        except Exception as e:
            self.fail(f"Sign-in test failed: {str(e)}")

    def test_create_user(self):
        """Test user creation endpoint"""
        response = self.client.post('/api/auth/create_user', 
            json={
                "user_id": self.test_user_id,
                "email": self.test_email,
                "username": "TonyNlemadim"
            },
            headers=self.headers
        )
        # Accept both 201 (created) and 400 (already exists) as valid responses
        self.assertIn(response.status_code, [201, 400])
        if response.status_code == 400:
            self.assertIn("User already exists", response.get_data(as_text=True))
        else:
            self.assertIn("User created successfully", response.get_data(as_text=True))

    def test_link_operations(self):
        """Test link-related operations"""
        # Test storing a new link
        link_data = {
            "user_id": self.test_user_id,
            "link": "https://example.com/new-link"
        }
        store_response = requests.post(
            f"{self.base_url}/links/store", 
            json=link_data,
            headers=self.headers  # Add headers here
        )
        self.assertEqual(store_response.status_code, 200)
        self.assertEqual(store_response.json()["message"], "Link stored successfully")

        # Test updating a link
        update_data = {
            "title": "Example Article",
            "url": "https://example.com/article",
            "imageUrl": "https://example.com/image.jpg",
            "linkType": "weblink",
            "categoryId": "categoryDocId",
            "categoryName": "Tech"
        }
        update_response = self.client.post(
            f'/api/links/update/{self.test_user_id}', 
            json=update_data,
            headers=self.headers  # Add headers here
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertIn("Link updated successfully", update_response.get_data(as_text=True))

    def test_gist_operations(self):
        """Test gist-related operations"""
        # First, ensure the user document exists
        user_doc_ref = firestore.client().collection('users').document(self.test_user_id)
        if not user_doc_ref.get().exists:
            user_doc_ref.set({
                'gists': [],
                'email': self.test_email,
                'username': "TonyNlemadim"
            })

        # Test adding a new gist
        gist_data = {
            "title": "Audio Gist Title",
            "imageUrl": "https://example.com/gist-image.jpg",
            "isFinished": True,
            "playbackDuration": 300,
            "playbackTime": 120,
            "segments": [
                {
                    "segmentId": "segmentDocId",
                    "audioUrl": "https://example.com/audio.mp3",
                    "title": "Segment Title",
                    "duration": 60,
                    "segmentIndex": 0
                }
            ]
        }
        
        add_response = self.client.post(
            f'/api/gists/add/{self.test_user_id}', 
            json=gist_data,
            headers=self.headers
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertIn("Gist added successfully", add_response.get_data(as_text=True))

        # Test updating a gist
        update_gist_data = {
            "title": "Updated Gist Title",
            "imageUrl": "https://example.com/gist-image.jpg",
            "isFinished": False,
            "playbackDuration": 120,
            "playbackTime": 30,
            "segments": []
        }
        
        update_response = requests.post(
            f"{self.base_url}/gists/add/{self.test_user_id}", 
            json=update_gist_data,
            headers=self.headers  # Add headers here
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["message"], "Gist added successfully")

    def tearDown(self):
        """Clean up after each test"""
        try:
            # Clean up test data
            user_doc_ref = firestore.client().collection('users').document(self.test_user_id)
            user_doc_ref.update({
                'gists': [],
                'links': []
            })
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main()

  