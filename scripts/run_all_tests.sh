#!/bin/bash

# Run all tests for the Gista-CrewAI API

# Check if the Firebase service account file exists
SERVICE_ACCOUNT_PATH="functions/src/service-account.json"
if [ ! -f "$SERVICE_ACCOUNT_PATH" ] && [ -z "$FIREBASE_SERVICE_ACCOUNT" ]; then
    echo "ERROR: Firebase service account file not found at $SERVICE_ACCOUNT_PATH"
    echo "Please either:"
    echo "1. Place your service account JSON file at $SERVICE_ACCOUNT_PATH, or"
    echo "2. Set the FIREBASE_SERVICE_ACCOUNT environment variable to the path of your service account JSON file:"
    echo "   export FIREBASE_SERVICE_ACCOUNT=/path/to/your/service-account.json"
    exit 1
fi

echo "===== Running Tests That Don't Require the Server ====="
echo "Running Firebase Config Tests..."
python -m Firebase.config.test_firebase

echo "Running API Tests..."
python -m Firebase.APIs.testAPIs

echo "===== Running Tests That Require the Server ====="
echo "IMPORTANT: Make sure the Flask development server is running (python run_dev_server.py)"
echo "Press Enter to continue or Ctrl+C to cancel..."
read

echo "Running Live API Tests..."
python test_api_live.py

echo "Running Auto-Create Gist Tests..."
python test_auto_create_gist.py

echo "===== All Tests Completed =====" 