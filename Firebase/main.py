import functions_framework
from core.auth.controllers import AuthController
from core.storage.controllers import StorageController
from core.notifications.controllers import NotificationController
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger()

# Initialize controllers
auth_controller = AuthController()
storage_controller = StorageController()
notification_controller = NotificationController()

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
            return auth_controller.handle_request(request)
        elif path.startswith('storage/'):
            return storage_controller.handle_request(request)
        elif path.startswith('notifications/'):
            return notification_controller.handle_request(request)
        else:
            return {'error': 'Invalid endpoint'}, 404
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {'error': 'Internal server error'}, 500 