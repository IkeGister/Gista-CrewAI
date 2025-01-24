import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, storage

# Load environment variables from .env file
load_dotenv()

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
        """Initialize Firebase with credentials from environment variables"""
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

        self.app = initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
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
