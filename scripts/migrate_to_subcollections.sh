#!/bin/bash
# Migrate to Subcollections
# This script executes the steps needed to migrate the database from the
# flat structure to the subcollection-based structure

set -e  # Exit on error

# Print header
echo "========================================="
echo "  Migrating to Subcollection Structure"
echo "========================================="
echo "This migration will implement:"
echo "1. Subcollection-based database structure"
echo "2. Signal-based API for updating gist status"
echo "3. Backend service changes for fetching data"
echo "========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js and try again."
    exit 1
fi

# Step 1: Create test data
echo "Step 1: Creating test data with subcollection structure..."
node tests/create_subcollection_test_data.js
echo "✅ Test data created successfully"

# Step 2: Verify test data structure in Firebase Console
echo "Step 2: Please verify the test data structure in Firebase Console"
echo "     Open: https://console.firebase.google.com/project/YOUR_PROJECT_ID/firestore/data"
echo "     Check: /users/crewAI-backend-tester/gists and /users/crewAI-backend-tester/links"
read -p "Press Enter once verified (or Ctrl+C to abort)..."

# Step 3: Migrate specific user (example)
echo "Step 3: Migrating a specific user..."
read -p "Enter user ID to migrate (default: crewAI-backend-tester): " USER_ID
USER_ID=${USER_ID:-crewAI-backend-tester}
node tests/update_user_structure.js "$USER_ID"
echo "✅ User migration completed"

# Step 4: Test the API with subcollections
echo "Step 4: Testing the API with subcollections..."
# Set the API base URL for testing
read -p "Enter API base URL (default: http://localhost:5001/your-project/us-central1/apiSubcollections): " API_BASE_URL
API_BASE_URL=${API_BASE_URL:-http://localhost:5001/your-project/us-central1/apiSubcollections}
API_BASE_URL="$API_BASE_URL" node tests/test_subcollection_api.js
echo "✅ API tests completed"

# Step 5: Test signal-based status update
echo "Step 5: Testing signal-based status update API..."
read -p "Do you want to test the signal-based status update API? (y/n, default: y): " TEST_SIGNAL
TEST_SIGNAL=${TEST_SIGNAL:-y}
if [[ "$TEST_SIGNAL" == "y" || "$TEST_SIGNAL" == "Y" ]]; then
    echo "Testing signal-based API with empty JSON body..."
    # Test with curl
    read -p "Enter test user ID (default: crewAI-backend-tester): " TEST_USER
    TEST_USER=${TEST_USER:-crewAI-backend-tester}
    read -p "Enter test gist ID (you can find this in Firebase Console): " TEST_GIST
    
    if [ -z "$TEST_GIST" ]; then
        echo "❌ No gist ID provided, skipping test"
    else
        echo "Sending signal-based request to update gist status..."
        curl -X PUT \
             -H "Content-Type: application/json" \
             -H "X-API-Key: test-api-key" \
             -d "{}" \
             "${API_BASE_URL}/api/gists/${TEST_USER}/${TEST_GIST}/status"
        echo ""
        echo "✅ Signal-based test completed"
    fi
else
    echo "Skipping signal-based test"
fi

# Step 6: Migrate all users (optional)
read -p "Do you want to migrate all users? (y/n, default: n): " MIGRATE_ALL
MIGRATE_ALL=${MIGRATE_ALL:-n}
if [[ "$MIGRATE_ALL" == "y" || "$MIGRATE_ALL" == "Y" ]]; then
    echo "Step 6: Migrating all users..."
    node tests/update_user_structure.js --all
    echo "✅ All users migrated successfully"
else
    echo "Step 6: Skipping migration of all users"
fi

# Step 7: Generate API documentation
echo "Step 7: Generating API documentation..."
# Check if docs directory exists
if [ ! -d "docs/api" ]; then
    mkdir -p docs/api
fi
cp docs/api/SUBCOLLECTION_API_GUIDE.md docs/api/API-Documentation.md
echo "✅ API documentation generated"

# Step 8: Deploy with subcollection structure (optional)
read -p "Do you want to deploy the API with subcollection structure? (y/n, default: n): " DEPLOY
DEPLOY=${DEPLOY:-n}
if [[ "$DEPLOY" == "y" || "$DEPLOY" == "Y" ]]; then
    echo "Step 8: Deploying Firebase Functions with subcollection structure..."
    firebase deploy --only functions:apiSubcollections,functions:notificationsSubcollections --config firebase.subcollections.json
    echo "✅ Deployment completed"
else
    echo "Step 8: Skipping deployment"
fi

# Step 9: Switch to subcollection structure in production (optional)
read -p "Do you want to switch the production environment to use subcollections? (y/n, default: n): " SWITCH
SWITCH=${SWITCH:-n}
if [[ "$SWITCH" == "y" || "$SWITCH" == "Y" ]]; then
    echo "Step 9: Switching to subcollection structure in production..."
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
    echo "Step 9: Skipping switch to subcollection structure in production"
fi

echo "========================================="
echo "  Migration Process Completed"
echo "========================================="
echo "The migration to subcollection-based structure has been completed."
echo "This implementation includes:"
echo "- Subcollection-based data structure for better scalability and performance"
echo "- Signal-based API for updating gist status (empty JSON body)"
echo "- Backend service changes for fetching gists and links"
echo "For more details, see docs/api/SUBCOLLECTION_API_GUIDE.md"
echo "=========================================" 