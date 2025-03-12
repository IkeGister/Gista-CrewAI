from Firebase.config.firebase_config import FirebaseConfig
from firebase_admin import auth

# Initialize the Firebase Admin SDK using FirebaseConfig
firebase_config = FirebaseConfig()

def generate_custom_token(uid):
    """Generate a custom token for the user."""
    custom_token = auth.create_custom_token(uid)
    return custom_token

if __name__ == "__main__":
    user_id = "test_user_id"  # Replace with a unique user ID
    token = generate_custom_token(user_id)
    print(f"Custom Token for {user_id}: {token}") 