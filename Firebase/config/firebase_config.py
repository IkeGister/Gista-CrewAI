import os
from firebase_admin import credentials, initialize_app, storage

class FirebaseConfig:
    """
    Firebase Configuration Handler
    Manages Firebase initialization and provides access to Firebase services
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConfig, cls).__new__(cls)
            cls._instance._initialize_firebase()
        return cls._instance

    def _initialize_firebase(self):
        """Initialize Firebase with service account file"""
        cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "../../functions/src/service-account.json"))
        
        self.app = initialize_app(cred, {
            'storageBucket': "dof-ai.firebasestorage.app"
        })

        # Initialize Firebase services
        self.bucket = storage.bucket()

    @property
    def storage_bucket(self):
        """Get Firebase storage bucket instance"""
        return self.bucket

    def upload_file(self, file_path, destination_blob_name):
        """Uploads a file to the bucket."""
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {destination_blob_name}.")

    def download_file(self, source_blob_name, destination_file_path):
        """Downloads a file from the bucket."""
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_path)
        print(f"File {source_blob_name} downloaded to {destination_file_path}.")
