import logging

def setup_logger():
    """
    Set up and configure a logger for the application
    """
    logger = logging.getLogger('firebase_api')
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger 