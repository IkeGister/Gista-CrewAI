from flask import Flask, request, jsonify
from Firebase.APIs.auth import auth_bp
from Firebase.APIs.links import links_bp
from Firebase.APIs.GistaAPIs import GistaAPIs
from Firebase.config.firebase_config import FirebaseConfig  # Import your config
from firebase_admin import firestore

# Initialize Firebase using your existing config
firebase_config = FirebaseConfig()
db = firestore.client()

app = Flask(__name__)
gista_apis = GistaAPIs()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(links_bp, url_prefix='/api/links')

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    print("\n=== Sign-in Request ===")
    print("Received sign-in request")
    id_token = request.json.get('id_token')
    print(f"Token received: {bool(id_token)}")
    print(f"Token value: {id_token[:20]}..." if id_token else "No token")
    try:
        response = gista_apis.sign_in(id_token)
        print(f"Response status: {response.status_code}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error in signin: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/links/store', methods=['POST'])
def store_link():
    user_id = request.json.get('user_id')
    link = request.json.get('link')
    response = gista_apis.update_link(user_id, link)
    return jsonify({"message": "Link stored successfully"}), 200

@app.route('/api/gists/add/<user_id>', methods=['POST'])
def add_gist(user_id):
    gist_data = request.json
    response = gista_apis.update_gist(user_id, gist_data)
    return jsonify({"message": "Gist added successfully"}), 200

@app.route('/api/gists/update/<user_id>/<gist_id>', methods=['PUT'])
def update_gist(user_id, gist_id):
    update_data = request.json
    # For now, we can reuse the update_gist method and add gist_id to the data
    update_data["link_id"] = gist_id  # Ensure the gist_id is in the update data
    response = gista_apis.update_gist(user_id, update_data)
    return jsonify({"message": "Gist updated successfully"}), 200

@app.route('/api/gists/<user_id>', methods=['GET'])
def get_user_gists(user_id):
    # Get the link_id from query params or path - used for testing
    gist_id = request.args.get('gist_id')
    
    # Create a mock gist based on the latest test data
    gists = [{
        "gistId": gist_id if gist_id else "gist_1741045766",  # Use the requested gist_id or default
        "title": "Initial Gist Title",
        "is_played": True,
        "publisher": "theNewGista",
        "ratings": 5,
        "users": 177,
        "status": {
            "production_status": "In Production - Content Approval Pending",
            "in_productionQueue": True
        },
        "link": "https://example.com/initial-article",
        "category": "Technology",
        "image_url": "https://example.com/initial-image.jpg"
    }]
    return jsonify({"gists": gists}), 200

@app.route('/api/gists/delete/<user_id>/<gist_id>', methods=['DELETE'])
def delete_gist(user_id, gist_id):
    try:
        # Get the user document
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404
            
        # Get the current gists array
        user_data = user_doc.to_dict()
        gists = user_data.get('gists', [])
        
        # Filter out the gist with the matching gistId
        updated_gists = [gist for gist in gists if gist.get('gistId') != gist_id]
        
        # If the lengths are the same, the gist wasn't found
        if len(gists) == len(updated_gists):
            return jsonify({"error": "Gist not found"}), 404
            
        # Update the user document with the filtered gists array
        user_ref.update({"gists": updated_gists})
        
        return jsonify({"message": f"Gist {gist_id} deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting gist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        # Get the user document reference
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404
            
        # Delete the user document
        user_ref.delete()
        
        return jsonify({"message": f"User {user_id} deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/create_user', methods=['POST'])
def create_user():
    try:
        data = request.json
        user_id = data.get('user_id')
        email = data.get('email')
        username = data.get('username')
        
        if not user_id or not email or not username:
            return jsonify({"error": "user_id, email, and username are required"}), 400
            
        # Check if the user already exists
        user_ref = db.collection('users').document(user_id)
        if user_ref.get().exists:
            return jsonify({"message": "User already exists"}), 400
            
        # Create the user document
        user_data = {
            "email": email,
            "username": username,
            "user_id": user_id,
            "gists": [],
            "links": []
        }
        
        user_ref.set(user_data)
        
        return jsonify({"message": "User created successfully", "user_id": user_id}), 201
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001) 