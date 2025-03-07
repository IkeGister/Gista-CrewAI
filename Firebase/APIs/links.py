import firebase_admin
from firebase_admin import firestore
from flask import Blueprint, request, jsonify
from Firebase.config.firebase_config import FirebaseConfig
import uuid
from datetime import datetime
import logging

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
    """
    Add a gist for a user and notify the CrewAI service.
    
    Args:
        user_id: The user ID
        
    Returns:
        A JSON response with the result
    """
    try:
        # Get the user document
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        # Check if the user exists
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404
            
        # Get the gist data from the request
        gist_data = request.json
        
        # Generate a gist ID if not provided
        if 'gistId' not in gist_data:
            gist_data['gistId'] = f"gist_{uuid.uuid4().hex}"
        
        # Ensure all required fields are present with default values if needed
        if 'title' not in gist_data:
            gist_data['title'] = "Untitled Gist"
            
        if 'category' not in gist_data:
            gist_data['category'] = "Uncategorized"
            
        if 'is_published' not in gist_data:
            gist_data['is_published'] = True
            
        if 'link' not in gist_data:
            gist_data['link'] = ""
            
        if 'image_url' not in gist_data:
            gist_data['image_url'] = ""
            
        if 'ratings' not in gist_data:
            gist_data['ratings'] = 0
            
        if 'users' not in gist_data:
            gist_data['users'] = 0
            
        if 'is_played' not in gist_data:
            gist_data['is_played'] = False
            
        if 'playback_duration' not in gist_data:
            gist_data['playback_duration'] = 0
            
        if 'date_created' not in gist_data:
            gist_data['date_created'] = datetime.now().isoformat() + 'Z'
            
        if 'publisher' not in gist_data:
            gist_data['publisher'] = "theNewGista"
            
        # Set initial status if not provided
        if 'status' not in gist_data:
            gist_data['status'] = {
                'inProduction': False,
                'production_status': 'Reviewing Content',
            }
        else:
            # Ensure all status fields are present
            if 'inProduction' not in gist_data['status']:
                gist_data['status']['inProduction'] = False
                
            if 'production_status' not in gist_data['status']:
                gist_data['status']['production_status'] = 'Reviewing Content'
                
            # Remove deprecated fields if they exist
            if 'in_productionQueue' in gist_data['status']:
                gist_data['status']['inProduction'] = gist_data['status'].pop('in_productionQueue')
                
            if 'is_done_playing' in gist_data['status']:
                gist_data['status'].pop('is_done_playing')
                
            if 'playback_time' in gist_data['status']:
                gist_data['status'].pop('playback_time')
                
            if 'is_now_playing' in gist_data['status']:
                gist_data['status'].pop('is_now_playing')
        
        # Ensure segments are properly formatted
        if 'segments' not in gist_data:
            gist_data['segments'] = []
        
        # Add the gist to Firebase
        doc_ref.update({
            'gists': firestore.ArrayUnion([gist_data])
        })
        
        # Get the gist ID for notifying the CrewAI service
        gist_id = gist_data['gistId']
        
        # Notify the CrewAI service about the new gist
        try:
            # Import here to avoid circular imports
            from Firebase.services import CrewAIService
            
            # Initialize the CrewAI service client
            crew_ai_service = CrewAIService()
            
            # Call the CrewAI service to update the gist status using signal-based approach
            status_response = crew_ai_service.update_gist_status(user_id, gist_id)
            
            # Log the notification
            logger.info(f"CrewAI service notified about new gist: {status_response}")
            
            # Include notification status in the response
            return jsonify({
                "message": "Gist added successfully and CrewAI service notified", 
                "gist": gist_data,
                "notification": status_response
            }), 201
            
        except Exception as e:
            # Log the error but don't fail the gist creation
            logger.error(f"Error notifying CrewAI service: {str(e)}")
            
            # Return success response with notification error
            return jsonify({
                "message": "Gist added successfully but failed to notify CrewAI service", 
                "gist": gist_data,
                "notification_error": str(e)
            }), 201
        
    except Exception as e:
        logger.error(f"Error adding gist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@links_bp.route('/api/gists/notify-crew-ai/<user_id>/<gist_id>', methods=['POST'])
def notify_crew_ai(user_id, gist_id):
    """
    Notify the CrewAI service about a gist update using the signal-based API.
    
    This endpoint is specifically for notifying the CrewAI service about gist updates.
    It will fail if the CrewAI service is unavailable, unlike the add_gist endpoint
    which continues even if notification fails.
    
    Args:
        user_id: The user ID
        gist_id: The gist ID
        
    Returns:
        A JSON response with the result
    """
    try:
        # First, check if the gist exists
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404
            
        user_data = doc.to_dict()
        gist_exists = False
        
        if 'gists' in user_data:
            for gist in user_data['gists']:
                if gist.get('gistId') == gist_id:
                    gist_exists = True
                    break
                    
        if not gist_exists:
            return jsonify({"error": "Gist not found"}), 404
        
        # Import here to avoid circular imports
        from Firebase.services import CrewAIService
        
        # Initialize the CrewAI service client
        crew_ai_service = CrewAIService()
        
        # Call the CrewAI service to update the gist status using signal-based approach
        status_response = crew_ai_service.update_gist_status(user_id, gist_id)
        
        # Log the notification
        logger.info(f"CrewAI service notified about gist update: {status_response}")
        
        # Check if the response indicates success
        if isinstance(status_response, dict) and status_response.get('success') is False:
            error_message = status_response.get('message', 'Unknown error')
            raise Exception(error_message)
        
        return jsonify({
            "message": "CrewAI service notified successfully", 
            "response": status_response
        }), 200
        
    except Exception as e:
        logger.error(f"Error notifying CrewAI service: {str(e)}")
        return jsonify({
            "error": f"Service unavailable: {str(e)}"
        }), 503  # Service Unavailable 