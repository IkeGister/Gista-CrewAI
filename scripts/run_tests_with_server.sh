#!/bin/bash

# Script to start the server, run the tests, and then stop the server

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

# Check if the server is already running
if lsof -i:5001 > /dev/null; then
    echo "Server is already running on port 5001"
    SERVER_ALREADY_RUNNING=true
else
    echo "Starting Flask development server..."
    # Start the server in the background
    python run_dev_server.py &
    SERVER_PID=$!
    SERVER_ALREADY_RUNNING=false
    
    # Wait for the server to start
    echo "Waiting for server to start..."
    sleep 5
fi

# Run the tests
echo "===== Running Tests That Don't Require the Server ====="
echo "Running Firebase Config Tests..."
python -m Firebase.config.test_firebase

echo "Running API Tests..."
python -m Firebase.APIs.testAPIs

echo "===== Running Tests That Require the Server ====="
echo "Running Live API Tests..."
python test_api_live.py

echo "Running Auto-Create Gist Tests..."
python test_auto_create_gist.py

echo "===== All Tests Completed ====="

# Stop the server if we started it
if [ "$SERVER_ALREADY_RUNNING" = false ]; then
    echo "Stopping Flask development server..."
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null
    echo "Server stopped"
fi 