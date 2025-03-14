import firebase_admin
from firebase_admin import firestore
from flask import Blueprint, request, jsonify
from Firebase.config.firebase_config import FirebaseConfig
import uuid
from datetime import datetime
import logging
import os
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
firebase_config = FirebaseConfig()  # This should initialize Firebase
db = firestore.client()  # Firestore client should be created after initialization

links_bp = Blueprint('links', __name__)

def handle_notification_request(request):
    """
    Handle notification-related requests
    Routes to the appropriate endpoint based on the path
    """
    path = request.path.strip('/').replace('notifications/', '')
    method = request.method
    
    if path == 'links/store' and method == 'POST':
        return store_link()
    elif path.startswith('links/') and method == 'GET':
        user_id = path.replace('links/', '')
        return get_links(user_id)
    elif path.startswith('links/update/') and method == 'POST':
        user_id = path.replace('links/update/', '')
        return update_link(user_id)
    elif path.startswith('gists/add/') and method == 'POST':
        user_id = path.replace('gists/add/', '')
        return add_gist(user_id)
    else:
        return jsonify({'error': 'Invalid notification endpoint'}), 404

@links_bp.route('/api/links/store', methods=['POST'])
def store_link():
    """
    Store a link in the user's links subcollection
    """
    data = request.json
    user_id = data.get('user_id')
    link = data.get('link')
    auto_create_gist = data.get('auto_create_gist', True)  # Default to true

    if not user_id or not link:
        return jsonify({"error": "user_id and link are required"}), 400

    # Generate a unique link_id if not provided
    if 'gist_created' not in link:
        link['gist_created'] = {}
    
    link_id = link.get('gist_created', {}).get('link_id', f"link_{uuid.uuid4().hex}")

    try:
        # Convert the link data to the new format for subcollection
        subcollection_link = {
            'id': link_id,
            'url': link.get('gist_created', {}).get('url', ''),
            'title': link.get('gist_created', {}).get('link_title', ''),
            'description': link.get('description', ''),
            'category': link.get('category', 'Uncategorized'),
            'date_added': datetime.now().isoformat() + 'Z',
            'inProduction': False,
            'production_status': 'draft',
            'updatedAt': datetime.now().isoformat() + 'Z'
        }
        
        # Store the link in the links subcollection
        db.collection('users').document(user_id).collection('links').document(link_id).set(subcollection_link)
        logger.info(f"Stored link {link_id} in subcollection for user {user_id}")

    except Exception as e:
        logger.error(f"Error storing link: {str(e)}")
        return jsonify({"error": "Failed to store link"}), 500

    # If auto_create_gist is enabled, create a gist from the link
    gist_id = None
    
    if auto_create_gist:
        try:
            # Prepare gist data from the link
            gist_id = f"gist_{uuid.uuid4().hex}"
            gist_data = {
                'id': gist_id,
                'title': link.get('gist_created', {}).get('link_title', "Untitled Gist"),
                'image_url': link.get('gist_created', {}).get('image_url', ""),
                'link': link.get('gist_created', {}).get('url', ""),
                'category': link.get('category', "Uncategorized"),
                'is_published': True,
                'is_played': False,
                'playback_duration': 0,
                'publisher': "theNewGista",
                'ratings': 0,
                'segments': [],  # Empty segments to be filled by CrewAI
                'status': {
                    'inProduction': False,
                    'production_status': 'Reviewing Content',
                },
                'createdAt': datetime.now().isoformat() + 'Z',
                'updatedAt': datetime.now().isoformat() + 'Z'
            }
            
            # Add the gist to the gists subcollection
            db.collection('users').document(user_id).collection('gists').document(gist_id).set(gist_data)
            logger.info(f"Created gist {gist_id} in subcollection for user {user_id}")
            
            # Update the link's gistId field to reference the gist
            subcollection_link['gistId'] = gist_id
            db.collection('users').document(user_id).collection('links').document(link_id).update({
                'gistId': gist_id
            })
            
            # Also add the link to the gist's links subcollection
            db.collection('users').document(user_id).collection('gists').document(gist_id).collection('links').document(link_id).set(subcollection_link)
            logger.info(f"Added link {link_id} to gist {gist_id} subcollection")
            
            # Notify CrewAI about the new gist
            notify_crew_ai(user_id, gist_id)
            
        except Exception as e:
            logger.error(f"Error creating gist from link: {str(e)}")
            return jsonify({"error": "Failed to create gist from link"}), 500

    response = {"message": "Link stored successfully"}
    if gist_id:
        response["gistId"] = gist_id
    
    return jsonify(response), 200

@links_bp.route('/api/links/<user_id>', methods=['GET'])
def get_links(user_id):
    """
    Get all links for a user from the links subcollection
    """
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        # Query the links subcollection for the user
        links_snapshot = db.collection('users').document(user_id).collection('links').get()
        
        # Convert the links to a list
        links = [doc.to_dict() for doc in links_snapshot]
        
        return jsonify({"links": links}), 200
    
    except Exception as e:
        logger.error(f"Error getting links: {str(e)}")
        return jsonify({"error": "Failed to get links"}), 500

@links_bp.route('/api/links/update/<user_id>', methods=['POST'])
def update_link(user_id):
    """
    Update a link in the links subcollection
    """
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    data = request.json
    link_id = data.get('id')
    
    if not link_id:
        return jsonify({"error": "link ID is required"}), 400
    
    try:
        # Update the link in the links subcollection
        link_ref = db.collection('users').document(user_id).collection('links').document(link_id)
        link_doc = link_ref.get()
        
        if not link_doc.exists:
            return jsonify({"error": f"Link {link_id} not found"}), 404
        
        # Update the link with the new data
        update_data = {
            'title': data.get('title', link_doc.get('title')),
            'url': data.get('url', link_doc.get('url')),
            'description': data.get('description', link_doc.get('description')),
            'category': data.get('category', link_doc.get('category')),
            'updatedAt': datetime.now().isoformat() + 'Z'
        }
        
        link_ref.update(update_data)
        logger.info(f"Updated link {link_id} in subcollection for user {user_id}")
        
        # If the link is associated with a gist, update it there too
        gist_id = link_doc.get('gistId')
        if gist_id:
            gist_link_ref = db.collection('users').document(user_id).collection('gists').document(gist_id).collection('links').document(link_id)
            if gist_link_ref.get().exists:
                gist_link_ref.update(update_data)
                logger.info(f"Updated link {link_id} in gist {gist_id} subcollection")
        
        return jsonify({"message": "Link updated successfully"}), 200
    
    except Exception as e:
        logger.error(f"Error updating link: {str(e)}")
        return jsonify({"error": "Failed to update link"}), 500

@links_bp.route('/api/gists/add/<user_id>', methods=['POST'])
def add_gist(user_id):
    """
    Add a gist to the gists subcollection
    """
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    data = request.json
    
    # Validate required fields
    required_fields = ['title', 'image_url', 'link', 'category', 'segments']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    try:
        # Generate a gist ID if not provided
        gist_id = data.get('gistId', f"gist_{uuid.uuid4().hex}")
        
        # Normalize the gist data
        gist_data = {
            'id': gist_id,
            'title': data.get('title'),
            'image_url': data.get('image_url'),
            'link': data.get('link'),
            'category': data.get('category'),
            'segments': data.get('segments', []),
            'is_played': data.get('is_played', False),
            'is_published': data.get('is_published', True),
            'playback_duration': data.get('playback_duration', 0),
            'playback_time': data.get('playback_time', 0),
            'publisher': data.get('publisher', "theNewGista"),
            'ratings': data.get('ratings', 0),
            'users': data.get('users', 0),
            'status': data.get('status', {
                'inProduction': False,
                'production_status': 'Reviewing Content'
            }),
            'createdAt': data.get('date_created', datetime.now().isoformat() + 'Z'),
            'updatedAt': datetime.now().isoformat() + 'Z'
        }
        
        # Add the gist to the gists subcollection
        db.collection('users').document(user_id).collection('gists').document(gist_id).set(gist_data)
        logger.info(f"Added gist {gist_id} to subcollection for user {user_id}")
        
        # If a link_id is provided, associate it with the gist
        link_id = data.get('link_id')
        if link_id:
            # Check if the link exists in the links subcollection
            link_ref = db.collection('users').document(user_id).collection('links').document(link_id)
            link_doc = link_ref.get()
            
            if link_doc.exists:
                # Update the link with the gistId
                link_ref.update({
                    'gistId': gist_id,
                    'updatedAt': datetime.now().isoformat() + 'Z'
                })
                
                # Copy the link to the gist's links subcollection
                link_data = link_doc.to_dict()
                link_data['gistId'] = gist_id
                db.collection('users').document(user_id).collection('gists').document(gist_id).collection('links').document(link_id).set(link_data)
                logger.info(f"Associated link {link_id} with gist {gist_id}")
        
        # Notify CrewAI about the new gist
        notify_crew_ai(user_id, gist_id)
        
        return jsonify({
            "message": "Gist added successfully",
            "gist": gist_data
        }), 200
    
    except Exception as e:
        logger.error(f"Error adding gist: {str(e)}")
        return jsonify({"error": "Failed to add gist"}), 500

@links_bp.route('/api/gists/<user_id>', methods=['GET'])
def get_gists(user_id):
    """
    Get all gists for a user from the gists subcollection
    """
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        # Query the gists subcollection for the user
        gists_snapshot = db.collection('users').document(user_id).collection('gists').get()
        
        # Convert the gists to a list
        gists = [doc.to_dict() for doc in gists_snapshot]
        
        return jsonify({"gists": gists}), 200
    
    except Exception as e:
        logger.error(f"Error getting gists: {str(e)}")
        return jsonify({"error": "Failed to get gists"}), 500

@links_bp.route('/api/gists/<user_id>/<gist_id>', methods=['GET'])
def get_gist(user_id, gist_id):
    """
    Get a specific gist from the gists subcollection
    """
    if not user_id or not gist_id:
        return jsonify({"error": "user_id and gist_id are required"}), 400
    
    try:
        # Get the gist from the gists subcollection
        gist_doc = db.collection('users').document(user_id).collection('gists').document(gist_id).get()
        
        if not gist_doc.exists:
            return jsonify({"error": f"Gist {gist_id} not found"}), 404
        
        gist = gist_doc.to_dict()
        
        return jsonify(gist), 200
    
    except Exception as e:
        logger.error(f"Error getting gist: {str(e)}")
        return jsonify({"error": "Failed to get gist"}), 500

@links_bp.route('/api/gists/<user_id>/<gist_id>/status', methods=['PUT'])
def update_gist_status(user_id, gist_id):
    """
    Update the status of a gist using the signal-based approach
    
    This is a signal-based endpoint where:
    1. No request body is required - simply making the PUT request triggers the status update
    2. The server handles setting `inProduction: true` and `production_status: "In Production"` internally
    3. When successful, the response includes the link URL string
    """
    if not user_id or not gist_id:
        return jsonify({"error": "user_id and gist_id are required"}), 400
    
    try:
        # Get the gist from the gists subcollection
        gist_ref = db.collection('users').document(user_id).collection('gists').document(gist_id)
        gist_doc = gist_ref.get()
        
        if not gist_doc.exists:
            return jsonify({"error": f"Gist {gist_id} not found"}), 404
        
        # Update the gist status (signal-based approach)
        gist_ref.update({
            'status.inProduction': True,
            'status.production_status': 'In Production',
            'updatedAt': datetime.now().isoformat() + 'Z'
        })
        
        logger.info(f"Updated status for gist {gist_id} of user {user_id} using signal-based approach")
        
        # Return the link URL in the response (required for signal-based approach)
        gist = gist_doc.to_dict()
        return jsonify({"link": gist.get('link')}), 200
    
    except Exception as e:
        logger.error(f"Error updating gist status: {str(e)}")
        return jsonify({"error": "Failed to update gist status"}), 500

def notify_crew_ai(user_id, gist_id):
    """
    Notify CrewAI about a new gist using the signal-based API approach.
    
    This uses the signal-based endpoint where:
    1. No request body is required - simply making the PUT request triggers the status update
    2. The server handles setting status values internally
    3. When successful, the response includes the link URL string
    
    Args:
        user_id: The user ID
        gist_id: The gist ID to update
    """
    try:
        # First, update the gist status in Firestore to indicate it's in production
        db.collection('users').document(user_id).collection('gists').document(gist_id).update({
            'status.inProduction': True,
            'status.production_status': 'In Production',
            'updatedAt': datetime.now().isoformat() + 'Z'
        })
        
        logger.info(f"Updated gist {gist_id} status to In Production")
        
        # Now, trigger the signal-based API endpoint
        try:
            # Get API base URL and API key from environment
            api_base_url = os.getenv('CREW_AI_API_BASE_URL', 'https://api-yufqiolzaa-uc.a.run.app')
            api_key = os.getenv('SERVICE_API_KEY')
            
            if not api_key:
                logger.error("SERVICE_API_KEY environment variable is not set")
                return
            
            # Set up headers
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': api_key
            }
            
            # Signal-based approach - empty JSON object
            url = f"{api_base_url}/api/gists/{user_id}/{gist_id}/status"
            response = requests.put(url, headers=headers, json={})
            
            if response.status_code == 200:
                logger.info(f"Successfully notified CrewAI for gist {gist_id}")
                # If response includes link URL, log it
                response_data = response.json()
                if 'link' in response_data:
                    logger.info(f"CrewAI returned link: {response_data['link']}")
            else:
                logger.error(f"Failed to notify CrewAI: status code {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error calling CrewAI API: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error notifying CrewAI: {str(e)}")

# Register the blueprint
def register_links_blueprint(app):
    app.register_blueprint(links_bp) 