import os
import unittest
from flask import jsonify
from Firebase.config.firebase_config import FirebaseConfig
from firebase_admin import firestore, exceptions
import time

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
        """Test creating a user with hardcoded data that matches the current gist structure."""
        # Generate unique identifiers for this test run
        timestamp = int(time.time())
        user_id = f"test_user_{timestamp}"
        email = f"newuser_{timestamp}@example.com"
        gist_id = f"gist_{timestamp}"
        
        # Hard-coded user data with updated gist structure
        new_user_data = {
            "email": email,
            "username": "testGistaUser",
            "gists": [
                {
                    "gistId": gist_id,
                    "title": "Tech Trends Gist",
                    "category": "Technology",
                    "date_created": "2025-01-25T08:30:00Z",
                    "is_published": True,
                    "is_played": False,
                    "publisher": "theNewGista",
                    "ratings": 4,
                    "users": 42,
                    "link": "https://example.com/tech-article",
                    "image_url": "https://example.com/tech-article-image.jpg",
                    "playback_duration": 180,
                    "segments": [
                        {
                            "segment_title": "Latest Gadgets",
                            "segment_index": 0,
                            "segment_duration": 90,
                            "segment_audioUrl": "http://someAudioFile.mp3"
                        }
                    ],
                    "status": {
                        "is_now_playing": True,
                        "playback_time": 45,
                        "is_done_playing": False,
                        "production_status": "In Production - Content Approval Pending",
                        "in_productionQueue": False
                    }
                }
            ],
            "links": [
                {
                    "category": "Technology",
                    "date_added": "2025-01-25T09:00:00Z",
                    "gist_created": {
                        "gist_created": True,
                        "gist_id": f"link_gist_{timestamp}",
                        "image_url": "https://example.com/storage-resource.jpg",
                        "link_id": f"link_{timestamp}",
                        "link_title": "Tech Resource",
                        "link_type": "Web",
                        "url": "https://example.com/full-tech-resource"
                    },
                    "user_id": user_id,
                    "username": "testGistaUser"
                }
            ]
        }

        # Create new document in users collection with the generated ID
        doc_ref = self.db.collection('users').document(user_id)
        doc_ref.set(new_user_data)
        print(f"Created test user with ID: {user_id} and email: {email}")
        
        # Verify the document was created
        created_doc = doc_ref.get()
        self.assertTrue(created_doc.exists)
        self.assertEqual(created_doc.get('email'), email)
        self.assertEqual(len(created_doc.get('gists')), 1)
        self.assertEqual(len(created_doc.get('links')), 1)
        
        # Verify the gist structure
        gist = created_doc.get('gists')[0]
        self.assertIn('gistId', gist)
        self.assertEqual(gist['gistId'], gist_id)
        self.assertIn('segment_audioUrl', gist['segments'][0])
        self.assertIn('production_status', gist['status'])
        self.assertIn('in_productionQueue', gist['status'])
        
        print(f"Successfully verified gist structure for user {user_id}")

    def test_create_user_with_empty_arrays(self):
        """Test creating a user with empty gists and links arrays."""
        # Generate unique identifiers for this test run
        timestamp = int(time.time())
        user_id = f"empty_user_{timestamp}"
        email = f"empty_user_{timestamp}@example.com"
        
        # User data with empty gists and links arrays
        new_user_data = {
            "email": email,
            "username": "EmptyArraysUser",
            "user_id": user_id,
            "gists": [],  # Empty gists array
            "links": []   # Empty links array
        }

        # Create new document in users collection with the generated ID
        doc_ref = self.db.collection('users').document(user_id)
        doc_ref.set(new_user_data)
        print(f"Created test user with empty arrays - ID: {user_id}, email: {email}")
        
        # Verify the document was created
        created_doc = doc_ref.get()
        self.assertTrue(created_doc.exists)
        self.assertEqual(created_doc.get('email'), email)
        self.assertEqual(created_doc.get('username'), "EmptyArraysUser")
        
        # Verify the arrays are empty
        self.assertEqual(len(created_doc.get('gists')), 0)
        self.assertEqual(len(created_doc.get('links')), 0)
        
        print(f"Successfully verified empty arrays for user {user_id}")
        
        # Store the user_id as an instance variable if needed in other tests
        self.empty_user_id = user_id

    def test_update_user_link(self):
        """Test updating a user by adding a link to their links array and then removing it."""
        # First, create a user with empty arrays
        timestamp = int(time.time())
        user_id = f"link_test_user_{timestamp}"
        email = f"link_test_{timestamp}@example.com"
        
        # Create the initial user with empty arrays
        initial_user_data = {
            "email": email,
            "username": "LinkTestUser",
            "user_id": user_id,
            "gists": [],
            "links": []
        }
        
        # Create the user document
        user_ref = self.db.collection('users').document(user_id)
        user_ref.set(initial_user_data)
        print(f"Created test user for link update - ID: {user_id}")
        
        # Verify the user was created with empty arrays
        user_doc = user_ref.get()
        self.assertTrue(user_doc.exists)
        self.assertEqual(len(user_doc.get('links')), 0)
        
        # Create a link object to add
        link_id = f"link_{timestamp}"
        new_link = {
            "category": "Technology",
            "date_added": "2025-01-25T09:00:00Z",
            "gist_created": {
                "gist_created": False,  # No gist created yet
                "gist_id": None,
                "image_url": "https://example.com/tech-image.jpg",
                "link_id": link_id,
                "link_title": "Test Technology Article",
                "link_type": "Web",
                "url": "https://example.com/test-article"
            },
            "user_id": user_id,
            "username": "LinkTestUser"
        }
        
        # STEP 1: Update the user by adding the link to their links array
        # Get the current user data
        current_user_data = user_doc.to_dict()
        
        # Add the new link to the links array
        current_links = current_user_data.get('links', [])
        current_links.append(new_link)
        
        # Update the user document with the new links array
        user_ref.update({"links": current_links})
        print(f"Added link {link_id} to user {user_id}")
        
        # STEP 2: Verify the link was added correctly
        updated_user_doc = user_ref.get()
        updated_links = updated_user_doc.get('links')
        
        self.assertEqual(len(updated_links), 1, "User should have exactly one link")
        self.assertEqual(updated_links[0]['gist_created']['link_id'], link_id, "Link ID should match")
        self.assertEqual(updated_links[0]['category'], "Technology", "Link category should match")
        self.assertEqual(updated_links[0]['gist_created']['link_title'], "Test Technology Article", "Link title should match")
        
        print(f"Successfully verified link was added to user {user_id}")
        
        # STEP 3: Clean up by removing the link (restore to empty arrays)
        user_ref.update({"links": []})
        
        # Verify the cleanup was successful
        final_user_doc = user_ref.get()
        final_links = final_user_doc.get('links')
        self.assertEqual(len(final_links), 0, "User should have empty links array after cleanup")
        
        print(f"Successfully cleaned up user {user_id} by removing the added link")

    def test_update_user_gist(self):
        """Test updating a user by adding a gist to their gists array and then removing it."""
        # First, create a user with empty arrays
        timestamp = int(time.time())
        user_id = f"gist_test_user_{timestamp}"
        email = f"gist_test_{timestamp}@example.com"
        gist_id = f"gist_{timestamp}"
        
        # Create the initial user with empty arrays
        initial_user_data = {
            "email": email,
            "username": "GistTestUser",
            "user_id": user_id,
            "gists": [],
            "links": []
        }
        
        # Create the user document
        user_ref = self.db.collection('users').document(user_id)
        user_ref.set(initial_user_data)
        print(f"Created test user for gist update - ID: {user_id}")
        
        # Verify the user was created with empty arrays
        user_doc = user_ref.get()
        self.assertTrue(user_doc.exists)
        self.assertEqual(len(user_doc.get('gists')), 0)
        
        # Create a gist object to add
        new_gist = {
            "gistId": gist_id,
            "title": "Test Gist",
            "category": "Technology",
            "date_created": "2025-01-25T08:30:00Z",
            "is_published": True,
            "is_played": False,
            "publisher": "GistTestUser",
            "ratings": 0,
            "users": 0,
            "link": "https://example.com/test-article",
            "image_url": "https://example.com/test-image.jpg",
            "playback_duration": 120,
            "segments": [
                {
                    "segment_title": "Test Segment",
                    "segment_index": 0,
                    "segment_duration": 60,
                    "segment_audioUrl": "http://example.com/test-audio.mp3"
                }
            ],
            "status": {
                "is_now_playing": False,
                "playback_time": 0,
                "is_done_playing": False,
                "production_status": "In Production",
                "in_productionQueue": True
            }
        }
        
        # STEP 1: Update the user by adding the gist to their gists array
        # Get the current user data
        current_user_data = user_doc.to_dict()
        
        # Add the new gist to the gists array
        current_gists = current_user_data.get('gists', [])
        current_gists.append(new_gist)
        
        # Update the user document with the new gists array
        user_ref.update({"gists": current_gists})
        print(f"Added gist {gist_id} to user {user_id}")
        
        # STEP 2: Verify the gist was added correctly
        updated_user_doc = user_ref.get()
        updated_gists = updated_user_doc.get('gists')
        
        self.assertEqual(len(updated_gists), 1, "User should have exactly one gist")
        self.assertEqual(updated_gists[0]['gistId'], gist_id, "Gist ID should match")
        self.assertEqual(updated_gists[0]['title'], "Test Gist", "Gist title should match")
        self.assertEqual(updated_gists[0]['category'], "Technology", "Gist category should match")
        self.assertEqual(len(updated_gists[0]['segments']), 1, "Gist should have one segment")
        self.assertEqual(updated_gists[0]['segments'][0]['segment_title'], "Test Segment", "Segment title should match")
        self.assertIn('segment_audioUrl', updated_gists[0]['segments'][0], "Segment should have audio URL")
        self.assertIn('production_status', updated_gists[0]['status'], "Status should have production_status")
        self.assertIn('in_productionQueue', updated_gists[0]['status'], "Status should have in_productionQueue")
        
        print(f"Successfully verified gist was added to user {user_id}")
        
        # STEP 3: Clean up by removing the gist (restore to empty arrays)
        user_ref.update({"gists": []})
        
        # Verify the cleanup was successful
        final_user_doc = user_ref.get()
        final_gists = final_user_doc.get('gists')
        self.assertEqual(len(final_gists), 0, "User should have empty gists array after cleanup")
        
        print(f"Successfully cleaned up user {user_id} by removing the added gist")

    def test_link_to_gist_workflow(self):
        """Test the workflow of creating a gist from a link."""
        # First, create a user with empty arrays
        timestamp = int(time.time())
        user_id = f"workflow_user_{timestamp}"
        email = f"workflow_{timestamp}@example.com"
        link_id = f"link_{timestamp}"
        gist_id = f"gist_{timestamp}"
        
        # Create the initial user with empty arrays
        initial_user_data = {
            "email": email,
            "username": "WorkflowTestUser",
            "user_id": user_id,
            "gists": [],
            "links": []
        }
        
        # Create the user document
        user_ref = self.db.collection('users').document(user_id)
        user_ref.set(initial_user_data)
        print(f"Created test user for workflow test - ID: {user_id}")
        
        # STEP 1: Add a link to the user (without a gist)
        initial_link = {
            "category": "Technology",
            "date_added": "2025-01-25T09:00:00Z",
            "gist_created": {
                "gist_created": False,  # No gist created yet
                "gist_id": None,
                "image_url": "https://example.com/workflow-image.jpg",
                "link_id": link_id,
                "link_title": "Workflow Test Article",
                "link_type": "Web",
                "url": "https://example.com/workflow-article"
            },
            "user_id": user_id,
            "username": "WorkflowTestUser"
        }
        
        # Update the user with the initial link
        user_ref.update({"links": [initial_link]})
        print(f"Added initial link {link_id} to user {user_id}")
        
        # Verify the link was added
        user_doc = user_ref.get()
        links = user_doc.get('links')
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['gist_created']['link_id'], link_id)
        self.assertFalse(links[0]['gist_created']['gist_created'])
        
        # STEP 2: Create a gist from the link
        new_gist = {
            "gistId": gist_id,
            "title": "Generated from " + links[0]['gist_created']['link_title'],
            "category": links[0]['category'],
            "date_created": "2025-01-25T10:00:00Z",
            "is_published": True,
            "is_played": False,
            "publisher": "WorkflowTestUser",
            "ratings": 0,
            "users": 0,
            "link": links[0]['gist_created']['url'],
            "image_url": links[0]['gist_created']['image_url'],
            "playback_duration": 120,
            "segments": [
                {
                    "segment_title": "Generated Segment",
                    "segment_index": 0,
                    "segment_duration": 60,
                    "segment_audioUrl": "http://example.com/generated-audio.mp3"
                }
            ],
            "status": {
                "is_now_playing": False,
                "playback_time": 0,
                "is_done_playing": False,
                "production_status": "In Production",
                "in_productionQueue": True
            }
        }
        
        # Update the user with the new gist
        user_data = user_doc.to_dict()
        user_data['gists'] = [new_gist]
        
        # STEP 3: Update the link to indicate a gist was created
        updated_links = user_data['links']
        updated_links[0]['gist_created']['gist_created'] = True
        updated_links[0]['gist_created']['gist_id'] = gist_id
        
        # Update the user document with both changes
        user_ref.set(user_data)
        print(f"Created gist {gist_id} from link {link_id}")
        
        # STEP 4: Verify the workflow was completed correctly
        final_user_doc = user_ref.get()
        final_user_data = final_user_doc.to_dict()
        
        # Check gists
        self.assertEqual(len(final_user_data['gists']), 1)
        self.assertEqual(final_user_data['gists'][0]['gistId'], gist_id)
        self.assertEqual(final_user_data['gists'][0]['link'], links[0]['gist_created']['url'])
        
        # Check links
        self.assertEqual(len(final_user_data['links']), 1)
        self.assertEqual(final_user_data['links'][0]['gist_created']['link_id'], link_id)
        self.assertTrue(final_user_data['links'][0]['gist_created']['gist_created'])
        self.assertEqual(final_user_data['links'][0]['gist_created']['gist_id'], gist_id)
        
        print(f"Successfully verified link-to-gist workflow for user {user_id}")
        
        # STEP 5: Clean up
        user_ref.update({"gists": [], "links": []})
        
        # Verify cleanup
        cleanup_doc = user_ref.get()
        self.assertEqual(len(cleanup_doc.get('gists')), 0)
        self.assertEqual(len(cleanup_doc.get('links')), 0)
        
        print(f"Successfully cleaned up user {user_id}")

    def test_delete_gist(self):
        """Test deleting a gist from a user's gists array."""
        # First, create a user with a gist
        timestamp = int(time.time())
        user_id = f"delete_gist_user_{timestamp}"
        email = f"delete_gist_{timestamp}@example.com"
        gist_id = f"gist_{timestamp}"
        
        # Create the initial user with a gist
        initial_user_data = {
            "email": email,
            "username": "DeleteGistUser",
            "user_id": user_id,
            "gists": [
                {
                    "gistId": gist_id,
                    "title": "Gist To Delete",
                    "category": "Technology",
                    "date_created": "2025-01-25T08:30:00Z",
                    "is_published": True,
                    "is_played": False,
                    "publisher": "DeleteGistUser",
                    "ratings": 0,
                    "users": 0,
                    "link": "https://example.com/delete-test-article",
                    "image_url": "https://example.com/delete-test-image.jpg",
                    "playback_duration": 120,
                    "segments": [
                        {
                            "segment_title": "Delete Test Segment",
                            "segment_index": 0,
                            "segment_duration": 60,
                            "segment_audioUrl": "http://example.com/delete-test-audio.mp3"
                        }
                    ],
                    "status": {
                        "is_now_playing": False,
                        "playback_time": 0,
                        "is_done_playing": False,
                        "production_status": "In Production",
                        "in_productionQueue": True
                    }
                }
            ],
            "links": []
        }
        
        # Create the user document
        user_ref = self.db.collection('users').document(user_id)
        user_ref.set(initial_user_data)
        print(f"Created test user with gist for deletion test - ID: {user_id}")
        
        # Verify the user was created with the gist
        user_doc = user_ref.get()
        self.assertTrue(user_doc.exists)
        self.assertEqual(len(user_doc.get('gists')), 1)
        self.assertEqual(user_doc.get('gists')[0]['gistId'], gist_id)
        
        # STEP 1: Delete the gist by removing it from the gists array
        user_data = user_doc.to_dict()
        
        # Filter out the gist with the matching gistId
        updated_gists = [gist for gist in user_data['gists'] if gist['gistId'] != gist_id]
        
        # Update the user document with the filtered gists array
        user_ref.update({"gists": updated_gists})
        print(f"Deleted gist {gist_id} from user {user_id}")
        
        # STEP 2: Verify the gist was deleted
        updated_user_doc = user_ref.get()
        updated_gists = updated_user_doc.get('gists')
        
        self.assertEqual(len(updated_gists), 0, "User should have no gists after deletion")
        
        print(f"Successfully verified gist deletion for user {user_id}")
        
        # Clean up by deleting the test user document
        user_ref.delete()
        
        # Verify the user document was deleted
        deleted_doc = user_ref.get()
        self.assertFalse(deleted_doc.exists, "User document should be deleted")
        
        print(f"Successfully deleted test user {user_id}")

    def test_delete_user(self):
        """Test creating and then deleting a user document."""
        # Create a user with some data
        timestamp = int(time.time())
        user_id = f"delete_user_{timestamp}"
        email = f"delete_user_{timestamp}@example.com"
        
        # User data with some content
        user_data = {
            "email": email,
            "username": "DeleteTestUser",
            "user_id": user_id,
            "gists": [
                {
                    "gistId": f"gist_{timestamp}",
                    "title": "Test Gist for Deletion",
                    "category": "Technology",
                    "date_created": "2025-01-25T08:30:00Z",
                    "is_published": True,
                    "is_played": False,
                    "publisher": "DeleteTestUser",
                    "ratings": 0,
                    "users": 0,
                    "link": "https://example.com/delete-user-test",
                    "image_url": "https://example.com/delete-user-image.jpg",
                    "playback_duration": 120,
                    "segments": [
                        {
                            "segment_title": "Delete User Test Segment",
                            "segment_index": 0,
                            "segment_duration": 60,
                            "segment_audioUrl": "http://example.com/delete-user-audio.mp3"
                        }
                    ],
                    "status": {
                        "is_now_playing": False,
                        "playback_time": 0,
                        "is_done_playing": False,
                        "production_status": "In Production",
                        "in_productionQueue": True
                    }
                }
            ],
            "links": [
                {
                    "category": "Technology",
                    "date_added": "2025-01-25T09:00:00Z",
                    "gist_created": {
                        "gist_created": True,
                        "gist_id": f"gist_{timestamp}",
                        "image_url": "https://example.com/delete-user-link-image.jpg",
                        "link_id": f"link_{timestamp}",
                        "link_title": "Delete User Test Link",
                        "link_type": "Web",
                        "url": "https://example.com/delete-user-link"
                    },
                    "user_id": user_id,
                    "username": "DeleteTestUser"
                }
            ]
        }
        
        # Create the user document
        user_ref = self.db.collection('users').document(user_id)
        user_ref.set(user_data)
        print(f"Created test user for deletion - ID: {user_id}")
        
        # Verify the user was created
        user_doc = user_ref.get()
        self.assertTrue(user_doc.exists)
        self.assertEqual(user_doc.get('email'), email)
        self.assertEqual(len(user_doc.get('gists')), 1)
        self.assertEqual(len(user_doc.get('links')), 1)
        
        # STEP 1: Delete the user document
        user_ref.delete()
        print(f"Deleted user {user_id}")
        
        # STEP 2: Verify the user was deleted
        deleted_doc = user_ref.get()
        self.assertFalse(deleted_doc.exists, "User document should be deleted")
        
        # STEP 3: Try to query by email to ensure it's really gone
        query_result = self.db.collection('users').where('email', '==', email).get()
        self.assertEqual(len(list(query_result)), 0, "No documents should be found with the deleted user's email")
        
        print(f"Successfully verified user deletion for {user_id}")
        
        # No cleanup needed as the document is already deleted

    def tearDown(self):
        """Clean up test data after each test."""
        # Delete test user if it exists
        test_users = [
            'gister12346'
        ]
        
        for user in test_users:
            try:
                # Try by ID
                self.db.collection('users').document(user).delete()
            except Exception:
                pass
                
        # Clean up any test users created during tests (except the ones we want to keep)
        users_to_keep = ['test_user_1741056183', 'test_user_1741057003']
        timestamp = int(time.time()) - 86400  # Look for users created in the last 24 hours
        
        # Common test user prefixes
        test_prefixes = [
            'test_user_', 
            'empty_user_', 
            'delete_gist_user_', 
            'delete_user_', 
            'workflow_user_', 
            'gist_test_user_', 
            'link_test_user_'
        ]
        
        # Query for test users
        for prefix in test_prefixes:
            try:
                # We can't easily query by prefix in Firestore, so we'll get all users
                # and filter them in code
                users = self.db.collection('users').get()
                for user in users:
                    user_id = user.id
                    if user_id.startswith(prefix) and user_id not in users_to_keep:
                        user.reference.delete()
            except Exception as e:
                print(f"Error cleaning up test users with prefix {prefix}: {e}")

    def test_fetch_all_gists(self):
        """Fetch and display all gists from all users in the database."""
        print("\n=== Fetching all gists from all users ===")
        
        try:
            # Get all users
            users_ref = self.db.collection('users')
            users = users_ref.stream()
            
            # Track total gists and gists per user
            total_gists = 0
            user_gist_counts = {}
            gist_ids = []
            
            # Process each user
            for user in users:
                user_id = user.id
                user_data = user.to_dict()
                
                # Get gists array for the current user
                gists = user_data.get('gists', [])
                user_gist_counts[user_id] = len(gists)
                total_gists += len(gists)
                
                print(f"\nUser ID: {user_id}")
                print(f"  Username: {user_data.get('username', 'N/A')}")
                print(f"  Gists count: {len(gists)}")
                
                # Display details for each gist
                for i, gist in enumerate(gists):
                    print(f"  Gist #{i+1}:")
                    gist_id = gist.get('gistId', 'N/A')
                    gist_ids.append(gist_id)
                    print(f"    Gist ID: {gist_id}")
                    print(f"    Title: {gist.get('title', 'N/A')}")
                    print(f"    Category: {gist.get('category', 'N/A')}")
                    print(f"    Date Created: {gist.get('date_created', 'N/A')}")
                    print(f"    Is Published: {gist.get('is_published', False)}")
                    
                    # Status information
                    status = gist.get('status', {})
                    print(f"    Status:")
                    print(f"      Production Status: {status.get('production_status', 'N/A')}")
                    print(f"      In Production Queue: {status.get('in_productionQueue', False)}")
                    
                    # Segment information
                    segments = gist.get('segments', [])
                    print(f"    Segments: {len(segments)} total")
            
            # Summary
            print(f"\n=== Gist Summary ===")
            print(f"Total gists across all users: {total_gists}")
            for user_id, count in user_gist_counts.items():
                print(f"User {user_id}: {count} gists")
            
            # Print unique gist IDs
            print(f"\nUnique Gist IDs: {len(set(gist_ids))}")
            if len(gist_ids) != len(set(gist_ids)):
                print("WARNING: There are duplicate gist IDs across users!")
            
            # No assertion here - it's okay if there are no gists in the test database
            # This is just an informational test
            
        except Exception as e:
            self.fail(f"Error fetching user gists: {str(e)}")

    def test_fetch_all_links(self):
        """Fetch and display all links from all users in the database."""
        print("\n=== Fetching all links from all users ===")
        
        try:
            # Get all users
            users_ref = self.db.collection('users')
            users = users_ref.stream()
            
            # Track total links and links per user
            total_links = 0
            user_link_counts = {}
            link_ids = []
            
            # Process each user
            for user in users:
                user_id = user.id
                user_data = user.to_dict()
                
                # Get links array for the current user
                links = user_data.get('links', [])
                user_link_counts[user_id] = len(links)
                total_links += len(links)
                
                print(f"\nUser ID: {user_id}")
                print(f"  Username: {user_data.get('username', 'N/A')}")
                print(f"  Links count: {len(links)}")
                
                # Display details for each link
                for i, link in enumerate(links):
                    print(f"  Link #{i+1}:")
                    print(f"    Category: {link.get('category', 'N/A')}")
                    
                    # Access gist_created object
                    gist_created = link.get('gist_created', {})
                    link_id = gist_created.get('link_id', 'N/A')
                    link_ids.append(link_id)
                    print(f"    Link ID: {link_id}")
                    print(f"    URL: {gist_created.get('url', 'N/A')}")
                    print(f"    Title: {gist_created.get('link_title', 'N/A')}")
                    print(f"    Type: {gist_created.get('link_type', 'N/A')}")
                    print(f"    Gist created: {gist_created.get('gist_created', False)}")
                    print(f"    Gist ID: {gist_created.get('gist_id', 'None')}")
            
            # Summary
            print(f"\n=== Link Summary ===")
            print(f"Total links across all users: {total_links}")
            for user_id, count in user_link_counts.items():
                print(f"User {user_id}: {count} links")
            
            # Print unique link IDs
            print(f"\nUnique Link IDs: {len(set(link_ids))}")
            if len(link_ids) != len(set(link_ids)):
                print("WARNING: There are duplicate link IDs across users!")
            
            # No assertion here - it's okay if there are no links in the test database
            # This is just an informational test
            
        except Exception as e:
            self.fail(f"Error fetching user links: {str(e)}")

if __name__ == "__main__":
    unittest.main() 