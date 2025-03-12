import firebase_admin
from firebase_admin import auth
import pyrebase  # Import pyrebase
from Firebase.config.firebase_config import FirebaseConfig  # Import FirebaseConfig

# Initialize Firebase using the FirebaseConfig class
firebase_config = FirebaseConfig()

# Initialize Firebase client with config from FirebaseConfig
config = firebase_config.get_pyrebase_config()

firebase = pyrebase.initialize_app(config)

def sign_in_with_custom_token(custom_token):
    auth = firebase.auth()
    user = auth.sign_in_with_custom_token(custom_token)
    return user['idToken']

if __name__ == "__main__":
    custom_token = "YOUR_CUSTOM_TOKEN"
    id_token = sign_in_with_custom_token(custom_token)
    print(f"ID Token: {id_token}")