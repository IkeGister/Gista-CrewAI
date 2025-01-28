import os
import unittest
from flask import jsonify
from Firebase.config.firebase_config import FirebaseConfig
from firebase_admin import firestore, exceptions

class TestFirebaseFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the FirebaseConfig instance for all tests."""
        cls.firebase_config = FirebaseConfig()
        cls.db = firestore.client()

    def test_config_initialization(self):
        """Test if FirebaseConfig initializes correctly."""
        self.assertIsNotNone(self.firebase_config.app, "Firebase app should be initialized.")
        self.assertIsNotNone(self.firebase_config.storage_bucket, "Storage bucket should be accessible.")
        self.assertEqual(self.firebase_config.storage_bucket.name, "dof-ai.firebasestorage.app")

    def test_firestore_initialization(self):
        """Test if Firestore client initializes correctly."""
        self.assertIsNotNone(self.db, "Firestore client should be initialized.")

    def setUp(self):
        """Set up a known document for testing."""
        user_id = 'gister12346'  # Unique user ID
        user_ref = self.db.collection('users').document(user_id)

        # Check if the document already exists
        if not user_ref.get().exists:
            user_data = {
                "email": "gista12346@gmail.com",
                "username": "theSecondGista",
                "user_id": user_id,  # Store the user_id as a field
                "gists": [],  # Initialize as an empty array
                "links": []   # Initialize as an empty array
            }
            # Add the user document to the users collection
            self.user_doc_ref = user_ref.set(user_data)
            print(f"Document created with ID: {user_id}")
        else:
            print(f"Document with ID {user_id} already exists.")

    def test_upload_and_download_file(self):
        """Test uploading and then downloading a file from Firebase Storage."""
        file_path = '/Users/tonynlemadim/Documents/5DOF Projects/Gista-CrewAI/README.md'  # Path to the README.md file
        destination_blob_name = 'README.md'  # Name in the bucket
        self.firebase_config.upload_file(file_path, destination_blob_name)

        # Now download the file
        destination_file_path = '/Users/tonynlemadim/Documents/5DOF Projects/Gista-CrewAI/README_downloaded.md'  # Path to save the downloaded file
        self.firebase_config.download_file(destination_blob_name, destination_file_path)

        # Optionally, verify the downloaded file exists
        self.assertTrue(os.path.exists(destination_file_path), "Downloaded file should exist.")

    def test_list_files(self):
        """Test listing files in the Firebase Storage bucket."""
        bucket = self.firebase_config.storage_bucket
        blobs = bucket.list_blobs()
        print("Files in the bucket:")
        for blob in blobs:
            print(blob.name)

    def test_database_access(self):
        """Test accessing the newly created document in Firestore."""
        doc_id = 'gister12346'  # The document ID you want to access

        # Access the document in the users collection
        doc = self.db.collection('users').document(doc_id).get()

        self.assertTrue(doc.exists, "Document should exist in Firestore.")
        self.assertEqual(doc.get('username'), "theSecondGista", "Document should have the correct username.")
        self.assertEqual(doc.get('email'), "gista12346@gmail.com", "Document should have the correct email.")

    def test_create_hardcoded_user(self):
        # Hard-coded user data
        new_user_data = {
            "email": "newuser@example.com",
            "gists": [
                {
                    "category": "Technology",
                    "date_created": "2025-01-25T08:30:00Z",
                    "image_url": "https://example.com/tech-article-image.jpg",
                    "is_played": False,
                    "is_published": True,
                    "link": "https://example.com/tech-article",
                    "playback_duration": 180,
                    "publisher": "theNewGista",
                    "ratings": 4,
                    "segments": [
                        {
                            "segment_duration": 90,
                            "segment_index": 0,
                            "segment_title": "Latest Gadgets"
                        }
                    ],
                    "status": {
                        "is_done_playing": False,
                        "is_now_playing": True,
                        "playback_time": 45
                    },
                    "title": "Tech Trends Gist",
                    "users": 42
                }
            ],
            "links": [
                {
                    "category": "Technology",
                    "date_added": "2025-01-25T09:00:00Z",
                    "gist_created": {
                        "gist_created": True,
                        "gist_id": "someNewGist_jdhf98fasd7a",
                        "image_url": "https://example.com/storage-resource.jpg",
                        "link_id": "uniqueLinkID123",
                        "link_title": "Tech Resource",
                        "link_type": "Web",
                        "url": "https://example.com/full-tech-resource"
                    },
                    "user_id": "newUserID123",
                    "username": "theNewGista"
                }
            ]
        }

        # Check if a document with this email already exists
        existing_user_docs = self.db.collection('users') \
                               .where('email', '==', new_user_data['email']) \
                               .get()
        if existing_user_docs:
            print("User already exists")
            return

        # Create new document in users collection
        doc_ref = self.db.collection('users').add(new_user_data)[0]
        
        # Verify the document was created
        created_doc = doc_ref.get()
        self.assertTrue(created_doc.exists)
        self.assertEqual(created_doc.get('email'), new_user_data['email'])
        self.assertEqual(len(created_doc.get('gists')), 1)
        self.assertEqual(len(created_doc.get('links')), 1)

    def tearDown(self):
        """Clean up test data after each test."""
        # Delete test user if it exists
        test_users = [
            'gister12346',
            'newuser@example.com'  # Email from test_create_hardcoded_user
        ]
        
        for user in test_users:
            # Try by ID
            self.db.collection('users').document(user).delete()
            # Try by email
            docs = self.db.collection('users').where('email', '==', user).get()
            for doc in docs:
                doc.reference.delete()

if __name__ == "__main__":
    unittest.main() 