import functions_framework
from Firebase.APIs.auth import handle_auth_request
from Firebase.APIs.GistaAPIs import handle_storage_request
from Firebase.APIs.links import handle_notification_request
from Firebase.utils.logger import setup_logger

# Initialize logger
logger = setup_logger()

# No need to initialize controllers as we'll directly use the handler functions

@functions_framework.http
def handle_request(request):
    """
    Main entry point for Cloud Functions
    Routes requests to appropriate controllers based on path and method
    """
    try:
        # Extract path and method
        path = request.path.strip('/')
        method = request.method
        
        # Route to appropriate controller
        if path.startswith('auth/'):
            return handle_auth_request(request)
        elif path.startswith('storage/'):
            return handle_storage_request(request)
        elif path.startswith('notifications/'):
            return handle_notification_request(request)
        else:
            return {'error': 'Invalid endpoint'}, 404
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {'error': 'Internal server error'}, 500 