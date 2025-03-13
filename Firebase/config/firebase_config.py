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
        # Try to get service account path from environment variable
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
        
        # If not set, use the default path
        if not service_account_path:
            service_account_path = os.path.join(os.path.dirname(__file__), "../../functions/src/service-account.json")
            # Check if the file exists at the default path
            if not os.path.exists(service_account_path):
                raise FileNotFoundError(
                    f"Firebase service account file not found at {service_account_path}. "
                    f"Please either place the file at this location or set the FIREBASE_SERVICE_ACCOUNT environment variable."
                )
        
        cred = credentials.Certificate(service_account_path)
        
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
