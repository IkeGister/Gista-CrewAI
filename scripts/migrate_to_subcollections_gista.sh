#!/bin/bash
# Migrate to Subcollections - Gista Test Version
# This script executes the steps needed to migrate the database from the
# flat structure to the subcollection-based structure using the Gista-crewAI-Tester ID

set -e  # Exit on error

# Print header
echo "========================================="
echo "  Gista CrewAI - Subcollection Migration"
echo "========================================="
echo "This migration will implement:"
echo "1. Subcollection-based database structure"
echo "2. Signal-based API for updating gist status"
echo "3. Backend service changes for fetching data"
echo "Using test user ID: Gista-crewAI-Tester"
echo "========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js and try again."
    exit 1
fi

# Step 1: Create test data with Gista-crewAI-Tester ID
echo "Step 1: Creating test data with subcollection structure for Gista-crewAI-Tester..."
node tests/create_gista_crewai_test_data.js
echo "✅ Gista test data created successfully"

# Step 2: Verify test data structure in Firebase Console
echo "Step 2: Please verify the test data structure in Firebase Console"
echo "     Open: https://console.firebase.google.com/project/YOUR_PROJECT_ID/firestore/data"
echo "     Check: /users/Gista-crewAI-Tester/gists and /users/Gista-crewAI-Tester/links"
read -p "Press Enter once verified (or Ctrl+C to abort)..."

# Step 3: Test the API with subcollections
echo "Step 3: Testing the API with Gista subcollections..."
# Set the API base URL for testing
read -p "Enter API base URL (default: http://localhost:5001/your-project/us-central1/apiSubcollections): " API_BASE_URL
API_BASE_URL=${API_BASE_URL:-http://localhost:5001/your-project/us-central1/apiSubcollections}
API_BASE_URL="$API_BASE_URL" node tests/test_gista_subcollection_api.js
echo "✅ Gista API tests completed"

# Step 4: Test signal-based status update
echo "Step 4: Testing signal-based status update API for Gista..."
read -p "Do you want to test the signal-based status update API? (y/n, default: y): " TEST_SIGNAL
TEST_SIGNAL=${TEST_SIGNAL:-y}
if [[ "$TEST_SIGNAL" == "y" || "$TEST_SIGNAL" == "Y" ]]; then
    echo "Testing signal-based API with empty JSON body..."
    # Get the first gist ID from the test data
    echo "Enter a gist ID for the test (you can find this in Firebase Console),"
    echo "or leave blank to use one from your previous test run:"
    read -p "Gist ID: " TEST_GIST
    
    if [ -z "$TEST_GIST" ]; then
        echo "❌ No gist ID provided, skipping test"
    else
        echo "Sending signal-based request to update gist status..."
        curl -X PUT \
             -H "Content-Type: application/json" \
             -H "X-API-Key: test-api-key" \
             -d "{}" \
             "${API_BASE_URL}/api/gists/Gista-crewAI-Tester/${TEST_GIST}/status"
        echo ""
        echo "✅ Signal-based test completed"
    fi
else
    echo "Skipping signal-based test"
fi

# Step 5: Deploy with subcollection structure (optional)
read -p "Do you want to deploy the API with subcollection structure? (y/n, default: n): " DEPLOY
DEPLOY=${DEPLOY:-n}
if [[ "$DEPLOY" == "y" || "$DEPLOY" == "Y" ]]; then
    echo "Step 5: Deploying Firebase Functions with subcollection structure..."
    firebase deploy --only functions:apiSubcollections,functions:notificationsSubcollections --config firebase.subcollections.json
    echo "✅ Deployment completed"
else
    echo "Step 5: Skipping deployment"
fi

# Step 6: Switch to subcollection structure in production (optional)
read -p "Do you want to switch the production environment to use subcollections? (y/n, default: n): " SWITCH
SWITCH=${SWITCH:-n}
if [[ "$SWITCH" == "y" || "$SWITCH" == "Y" ]]; then
    echo "Step 6: Switching to subcollection structure in production..."
    # Copy subcollection files to their final locations
    cp functions/src/index_subcollections.js functions/src/index.js
    cp Firebase/services/crew_ai_service_subcollections.py Firebase/services/crew_ai_service.py
    cp Firebase/APIs/links_subcollections.py Firebase/APIs/links.py
    cp firebase.subcollections.json firebase.json
    cp firestore.subcollections.rules firestore.rules
    echo "✅ Switched to subcollection structure"
    
    # Deploy the updated configuration
    read -p "Do you want to deploy the updated configuration? (y/n, default: n): " DEPLOY_UPDATED
    DEPLOY_UPDATED=${DEPLOY_UPDATED:-n}
    if [[ "$DEPLOY_UPDATED" == "y" || "$DEPLOY_UPDATED" == "Y" ]]; then
        echo "Deploying updated configuration..."
        firebase deploy
        echo "✅ Deployment completed"
    fi
else
    echo "Step 6: Skipping switch to subcollection structure in production"
fi

echo "========================================="
echo "  Gista Migration Process Completed"
echo "========================================="
echo "The migration to subcollection-based structure has been completed using the Gista-crewAI-Tester user ID."
echo "This implementation includes:"
echo "- Subcollection-based data structure for better scalability and performance"
echo "- Signal-based API for updating gist status (empty JSON body)"
echo "- Backend service changes for fetching gists and links"
echo "For more details, see docs/api/SUBCOLLECTION_API_GUIDE.md"
echo "=========================================" 