from flask import Flask, request, jsonify
from Firebase.APIs.auth import auth_bp
from Firebase.APIs.links import links_bp
from Firebase.APIs.GistaAPIs import GistaAPIs
from Firebase.config.firebase_config import FirebaseConfig  # Import your config

# Initialize Firebase using your existing config
firebase_config = FirebaseConfig()

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

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001) 