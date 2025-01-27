import firebase_admin
from firebase_admin import firestore
from flask import Blueprint, request, jsonify
from Firebase.config.firebase_config import FirebaseConfig
import uuid
from datetime import datetime

# Initialize Firebase Admin SDK
firebase_config = FirebaseConfig()  # This should initialize Firebase
db = firestore.client()  # Firestore client should be created after initialization

links_bp = Blueprint('links', __name__)

@links_bp.route('/api/links/store', methods=['POST'])
def store_link():
    data = request.json
    user_id = data.get('user_id')
    link = data.get('link')

    if not user_id or not link:
        return jsonify({"error": "user_id and link are required"}), 400

    # Store the link in Firestore
    db.collection('users').document(user_id).update({
        'links': firestore.ArrayUnion([link])
    })

    return jsonify({"message": "Link stored successfully"}), 200

@links_bp.route('/api/links/<user_id>', methods=['GET'])
def get_links(user_id):
    doc = db.collection('users').document(user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    return jsonify(doc.to_dict()), 200

@links_bp.route('/api/links/update/<user_id>', methods=['POST'])
def update_link(user_id):
    data = request.json
    link = {
        "linkId": str(uuid.uuid4()),  # Generate unique ID
        "dateAdded": datetime.utcnow().isoformat(),
        "title": data.get('title'),
        "url": data.get('url'),
        "imageUrl": data.get('imageUrl'),  # Optional
        "linkType": data.get('linkType'),  # "weblink" or "pdf"
        "category": {
            "categoryId": data.get('categoryId'),  # Firestore document ID for the category
            "name": data.get('categoryName')  # Name of the category
        }
    }

    # Update the user's links array in Firestore
    db.collection('users').document(user_id).update({
        "links": firestore.ArrayUnion([link])
    })

    return jsonify({"message": "Link updated successfully"}), 200

@links_bp.route('/api/gists/add/<user_id>', methods=['POST'])
def add_gist(user_id):
    try:
        # Get the document reference
        doc_ref = db.collection('users').document(user_id)
        
        # Check if document exists
        doc = doc_ref.get()
        
        if not doc.exists:
            # Create the document if it doesn't exist
            doc_ref.set({
                'gists': []  # Initialize with empty gists array
            })
        
        # Now update the document
        gist_data = request.json
        doc_ref.update({
            'gists': firestore.ArrayUnion([gist_data])
        })
        
        return jsonify({"message": "Gist added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 