import firebase_admin
from Firebase.config.firebase_config import FirebaseCredentials

def initialize_firebase():
    cred = FirebaseCredentials().get_credentials()  # Assuming this method returns the credentials
    firebase_admin.initialize_app(cred) 