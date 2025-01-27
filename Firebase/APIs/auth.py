from flask import Blueprint, request, jsonify
from firebase_admin import firestore, auth
from Firebase.config.firebase_config import FirebaseConfig

# Initialize Firebase
firebase_config = FirebaseConfig()
db = firestore.client()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/signin', methods=['POST'])
def sign_in():
    data = request.json
    token = data.get('id_token')
    print(f"\nAuth Blueprint: Received token: {bool(token)}")

    try:
        # If it's a custom token, exchange it for an ID token
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        # Get user from token
        decoded_claims = auth.verify_id_token(token)
        print(f"Token decoded successfully for UID: {decoded_claims['uid']}")
        user = auth.get_user(decoded_claims['uid'])
        print(f"User retrieved: {user.email}")
        
        return jsonify({
            "email": user.email,
            "user_id": user.uid
        }), 200
    except Exception as e:
        print(f"Auth error: {str(e)}")
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/api/auth/create_user', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    
    # Check if the user already exists
    existing_user = db.collection('users').where('email', '==', email).get()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    # Initialize user_doc with mandatory fields
    user_doc = {
        "email": email,
        "username": username,
        "gists": [],  # Initialize empty arrays
        "links": []
    }

    # Add the user document to the users collection
    db.collection('users').document(data.get('user_id')).set(user_doc)

    return jsonify({"message": "User created successfully"}), 201 