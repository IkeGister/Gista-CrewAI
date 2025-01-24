import os
import unittest
from Firebase.config.firebase_config import FirebaseConfig

class TestFirebaseFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the FirebaseConfig instance for all tests."""
        cls.firebase_config = FirebaseConfig()

    def test_config_initialization(self):
        """Test if FirebaseConfig initializes correctly."""
        self.assertIsNotNone(self.firebase_config.app, "Firebase app should be initialized.")
        self.assertIsNotNone(self.firebase_config.storage_bucket, "Storage bucket should be accessible.")

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

if __name__ == "__main__":
    unittest.main() 