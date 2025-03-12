"""
Development Server for Gista-CrewAI API

This script runs a Flask development server for testing the API with actual HTTP calls.
It sets up the necessary environment and runs the app.py Flask application.

Usage:
    python run_dev_server.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app
from app import app

if __name__ == "__main__":
    print("Starting Gista-CrewAI API development server...")
    print("API will be available at http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(debug=True, port=5001, host='0.0.0.0') 