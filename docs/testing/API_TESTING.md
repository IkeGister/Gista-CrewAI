# API Testing Guide for Gista-CrewAI

This guide provides instructions on how to test the Gista-CrewAI API with actual HTTP calls to verify that the GistStatus interface is working correctly in a live environment.

## Testing Options

There are several ways to test the API:

1. **Unit Tests**: Run the existing unit tests to verify the API functionality.
2. **Flask Development Server**: Run a local Flask development server and test the API with actual HTTP calls.
3. **Firebase Emulators**: Run the Firebase emulators for a more complete testing environment.

## Prerequisites

- Python 3.7 or higher
- Firebase CLI (for Firebase emulators)
- Required Python packages: `flask`, `firebase-admin`, `requests`, `python-dotenv`

## Running Unit Tests

To run the existing unit tests:

```bash
# Run the Firebase config tests
python -m Firebase.config.test_firebase

# Run the API tests
python -m Firebase.APIs.testAPIs
```

## Running the Flask Development Server

To run the Flask development server:

```bash
# Start the Flask development server
python run_dev_server.py
```

The server will be available at http://localhost:5001.

## Testing with Actual HTTP Calls

Once the Flask development server is running, you can test the API with actual HTTP calls using the provided test script:

```bash
# Run the API test script
python test_api_live.py
```

This script will:

1. Create a test user
2. Create a test link with `auto_create_gist=true` (default)
3. Verify that a gist was created and the link's status was updated
4. Update the gist's status using the updated GistStatus interface
5. Create another test link with `auto_create_gist=false`
6. Verify that no gist was created for the second link
7. Delete the test gist
8. Delete the test user

The test script generates unique IDs for each test run to ensure isolation between test runs. It verifies that the enhanced `/api/links/store` endpoint correctly handles the `auto_create_gist` parameter and returns the expected ultra-minimal response format.

### Running the Auto-Create Gist Test Script

In addition to the general API test script, there's a dedicated script for testing the auto-create gist functionality:

```bash
# Run the auto-create gist test script
python test_auto_create_gist.py
```

This script focuses specifically on testing the auto-create gist functionality with more detailed verification steps.

## Running Firebase Emulators

For a more complete testing environment, you can run the Firebase emulators:

```bash
# Start the Firebase emulators
python run_firebase_emulators.py
```

This will start the Firestore, Authentication, and Storage emulators.

## Manual Testing with Postman or cURL

You can also test the API manually using Postman or cURL:

### Create a User

```bash
curl -X POST http://localhost:5001/api/auth/create_user \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "email": "test_user_123@example.com",
    "username": "TestUser"
  }'
```

### Create a Link

```bash
curl -X POST http://localhost:5001/api/links/store \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "link": {
      "title": "Test Link",
      "url": "https://example.com/test-article",
      "imageUrl": "https://example.com/test-image.jpg",
      "linkType": "weblink",
      "categoryId": "category123",
      "categoryName": "Technology"
    }
  }'
```

### Create a Gist

```bash
curl -X POST http://localhost:5001/api/gists/add/test_user_123 \
  -H "Content-Type: application/json" \
  -d '{
    "gistId": "gist_123",
    "title": "Test Gist",
    "image_url": "https://example.com/test-image.jpg",
    "link": "https://example.com/test-article",
    "category": "Technology",
    "link_id": "link_123",
    "isFinished": false,
    "playbackDuration": 180,
    "playbackTime": 0,
    "segments": [
      {
        "title": "Test Segment",
        "audioUrl": "https://example.com/test-audio.mp3",
        "duration": "60",
        "index": 0
      }
    ],
    "status": {
      "production_status": "Reviewing Content",
      "inProduction": false
    }
  }'
```

Note: The `gistId` field is optional. If not provided, the API will generate a unique ID for the gist. However, for testing purposes, it's recommended to provide a specific `gistId` so you can reference it in subsequent API calls.

### Get User Gists

```bash
curl -X GET http://localhost:5001/api/gists/test_user_123 \
  -H "Content-Type: application/json"
```

### Update Gist Status

```bash
curl -X PUT http://localhost:5001/api/gists/update/test_user_123/gist_123 \
  -H "Content-Type: application/json" \
  -d '{
    "status": {
      "production_status": "In Production",
      "inProduction": true
    }
  }'
```

### Delete Gist

```bash
curl -X DELETE http://localhost:5001/api/gists/delete/test_user_123/gist_123 \
  -H "Content-Type: application/json"
```

### Delete User

```bash
curl -X DELETE http://localhost:5001/api/auth/delete_user/test_user_123 \
  -H "Content-Type: application/json"
```

## Testing the Auto-Create Gist Functionality

The enhanced `/api/links/store` endpoint now supports automatically creating a gist when a link is stored. This can be tested using the following methods:

### Using the Test Script

```bash
# Run the auto-create gist test script
python test_auto_create_gist.py
```

This script will:
1. Create a test user
2. Test storing a link with `auto_create_gist=true` (default)
3. Verify that a gist was created and the link's status was updated
4. Test storing a link with `auto_create_gist=false`
5. Verify that no gist was created
6. Clean up by deleting the test user

### Using cURL Commands

#### Test with auto_create_gist=true (default)

```bash
# Create a test user
curl -X POST http://localhost:5001/api/auth/create_user \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "email": "test_user_123@example.com",
    "username": "TestUser123"
  }'

# Store a link with auto_create_gist=true (default)
curl -X POST http://localhost:5001/api/links/store \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "link": {
      "category": "Technology",
      "gist_created": {
        "link_title": "Test Link",
        "url": "https://example.com/test-article",
        "image_url": "https://example.com/test-image.jpg"
      }
    }
  }'

# Get the user's gists to verify the gist was created
curl -X GET http://localhost:5001/api/gists/test_user_123 \
  -H "Content-Type: application/json"

# Get the user's links to verify the link's gist_created status was updated
curl -X GET http://localhost:5001/api/links/test_user_123 \
  -H "Content-Type: application/json"
```

#### Test with auto_create_gist=false

```bash
# Store a link with auto_create_gist=false
curl -X POST http://localhost:5001/api/links/store \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "link": {
      "category": "Technology",
      "gist_created": {
        "link_title": "Test Link No Gist",
        "url": "https://example.com/test-article-no-gist",
        "image_url": "https://example.com/test-image-no-gist.jpg"
      }
    },
    "auto_create_gist": false
  }'

# Get the user's gists to verify no gist was created
curl -X GET http://localhost:5001/api/gists/test_user_123 \
  -H "Content-Type: application/json"

# Clean up by deleting the test user
curl -X DELETE http://localhost:5001/api/auth/delete_user/test_user_123 \
  -H "Content-Type: application/json"
```

### Expected Responses

#### When auto_create_gist is true (default)

```json
{
  "gistId": "gist_xyz789"
}
```

#### When auto_create_gist is false

```json
{
  "message": "Link stored successfully"
}
```

#### Error Responses

Missing required fields:
```json
{
  "error": "user_id and link are required"
}
```

Error storing link:
```json
{
  "error": "Failed to store link"
}
```

Error creating gist:
```json
{
  "error": "Link stored but failed to create gist"
}
```

## Testing the CrewAI Service Integration

The enhanced `/api/links/store` endpoint automatically notifies the CrewAI service when a gist is created. To verify this integration:

### Checking Service Logs

1. Enable debug logging in your application:
   ```bash
   export LOG_LEVEL=DEBUG
   python run_dev_server.py
   ```

2. Monitor the logs for CrewAI service calls:
   ```bash
   # Store a link with auto_create_gist=true
   curl -X POST http://localhost:5001/api/links/store \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user_123",
       "link": {
         "category": "Technology",
         "gist_created": {
           "link_title": "Test Link",
           "url": "https://example.com/test-article",
           "image_url": "https://example.com/test-image.jpg"
         }
       }
     }'
   ```

3. Look for log entries like:
   ```
   INFO:root:CrewAI service notified about new gist: gist_xyz789
   ```

### Using a Mock CrewAI Service

For testing without making actual API calls to the CrewAI service:

1. Create a mock service by setting the environment variable:
   ```bash
   export USE_MOCK_CREW_AI=true
   python run_dev_server.py
   ```

2. The mock service will log all calls but not make actual HTTP requests.

### Testing with the CrewAI Service Test Script

The Firebase/services directory includes a test script specifically for testing the CrewAI service integration:

```bash
cd Firebase/services
python test_gist_integration.py
```

This script:
1. Creates a test user
2. Creates a test link with auto_create_gist=true
3. Verifies that the CrewAI service is called with the correct parameters
4. Verifies that the gist status is updated correctly
5. Cleans up by deleting the test resources

### Verifying End-to-End Integration

To verify the complete end-to-end integration between Gista and the CrewAI service:

1. **Set up environment variables**:
   ```bash
   export CREW_AI_API_BASE_URL=https://api-yufqiolzaa-uc.a.run.app/api
   export SERVICE_API_KEY=your_api_key
   ```

2. **Run the integration test**:
   ```bash
   python test_e2e_integration.py
   ```

3. **Monitor both systems**:
   - Check the Gista logs for successful API calls
   - Check the CrewAI service logs for received notifications
   - Verify that the gist status changes as it moves through the production pipeline

### Debugging Integration Issues

If the integration is not working as expected:

1. **Check network connectivity**:
   ```bash
   curl -v $CREW_AI_API_BASE_URL/health
   ```

2. **Verify API key**:
   ```bash
   curl -v -H "Authorization: Bearer $SERVICE_API_KEY" $CREW_AI_API_BASE_URL/auth/verify
   ```

3. **Test with a minimal payload**:
   ```bash
   curl -v -H "Authorization: Bearer $SERVICE_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_user", "gist_id": "test_gist"}' \
     $CREW_AI_API_BASE_URL/gists/notify
   ```

4. **Enable verbose logging in the CrewAI service client**:
   ```bash
   export CREW_AI_LOG_LEVEL=DEBUG
   python run_dev_server.py
   ```

## Comprehensive Testing Flow

Here's a complete testing flow for the auto-create gist functionality:

1. **Start the development server**:
   ```bash
   python run_dev_server.py
   ```

2. **Create a test user**:
   ```bash
   curl -X POST http://localhost:5001/api/auth/create_user \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user_flow",
       "email": "test_user_flow@example.com",
       "username": "TestUserFlow"
     }'
   ```

3. **Store a link with auto_create_gist=true**:
   ```bash
   curl -X POST http://localhost:5001/api/links/store \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user_flow",
       "link": {
         "category": "Technology",
         "gist_created": {
           "link_title": "Test Link Flow",
           "url": "https://example.com/test-article-flow",
           "image_url": "https://example.com/test-image-flow.jpg"
         }
       }
     }'
   ```
   Save the returned `gistId` for later steps.

4. **Get the user's gists**:
   ```bash
   curl -X GET http://localhost:5001/api/gists/test_user_flow \
     -H "Content-Type: application/json"
   ```
   Verify that the gist with the saved `gistId` exists.

5. **Get the user's links**:
   ```bash
   curl -X GET http://localhost:5001/api/links/test_user_flow \
     -H "Content-Type: application/json"
   ```
   Verify that the link's `gist_created` status is updated.

6. **Update the gist's status**:
   ```bash
   curl -X PUT http://localhost:5001/api/gists/update/test_user_flow/GIST_ID \
     -H "Content-Type: application/json" \
     -d '{
       "status": {
         "production_status": "In Production",
         "inProduction": true
       }
     }'
   ```
   Replace `GIST_ID` with the saved `gistId`.

7. **Delete the gist**:
   ```bash
   curl -X DELETE http://localhost:5001/api/gists/delete/test_user_flow/GIST_ID \
     -H "Content-Type: application/json"
   ```
   Replace `GIST_ID` with the saved `gistId`.

8. **Delete the test user**:
   ```bash
   curl -X DELETE http://localhost:5001/api/auth/delete_user/test_user_flow \
     -H "Content-Type: application/json"
   ```

## Expanded Troubleshooting

In addition to the general troubleshooting tips, here are some specific issues related to the auto-create gist functionality:

1. **Gist not created but link stored**:
   - Check if `auto_create_gist` was explicitly set to `false`
   - Look for error logs related to gist creation
   - Verify that the link data contains all required fields for gist creation

2. **CrewAI service not notified**:
   - Check if the environment variables for the CrewAI service are correctly set
   - Look for error logs related to the CrewAI service notification
   - Verify that the network connection to the CrewAI service is working

3. **Link's gist_created status not updated**:
   - Check if the link has a valid `link_id` in its `gist_created` object
   - Look for error logs related to updating the link
   - Verify that the Firestore transaction completed successfully

4. **Incorrect response format**:
   - Ensure you're using the latest version of the API
   - Check if the response matches the expected ultra-minimal format
   - Verify that the content type is set to `application/json`

5. **Performance issues**:
   - The enhanced endpoint performs more operations and may take longer to respond
   - Consider increasing request timeouts if necessary
   - Monitor server performance during high load

Remember to check the server logs for detailed error messages, as they often provide the most accurate information about what went wrong.

## General Troubleshooting

If you encounter any issues while testing the API, check the following:

1. Make sure the Flask development server is running.
2. Check the server logs for any error messages.
3. Verify that the Firebase emulators are running (if using them).
4. Ensure that the request payloads match the expected format.
5. Check that the GistStatus interface is correctly implemented in the API.
6. When creating a gist, consider providing a specific `gistId` to make it easier to track in subsequent API calls.
7. If the port 5001 is already in use, you may need to stop the existing process or use a different port.

## GistStatus Interface

The GistStatus interface has been simplified to include only two properties:

- `production_status`: String indicating the current state of the Gist in the production pipeline
  - Valid values: "Reviewing Content", "In Production", "Completed", "Failed"
  - Default: "Reviewing Content"
- `inProduction`: Boolean indicating whether the Gist is currently in production
  - Default: false

The following fields have been deprecated and removed:
- `in_productionQueue` (replaced by `inProduction`)
- `is_done_playing`
- `is_now_playing`
- `playback_time`

When working with gist status, ensure you're using the updated interface.

## Recommendations for Updating Firebase Config Tests

The `Firebase/config/test_firebase.py` file contains a `test_link_to_gist_workflow` method that tests the workflow of creating a link and then separately creating a gist. This method should be updated to test the new workflow where a gist is automatically created when a link is stored.

### Recommended Changes to `test_link_to_gist_workflow`

```python
def test_link_to_gist_workflow(self):
    """
    Test the link-to-gist workflow with auto-create gist functionality
    
    This test verifies that:
    1. A link can be stored with auto_create_gist=true
    2. A gist is automatically created
    3. The link's gist_created status is updated
    4. The CrewAI service is notified
    """
    # Test data
    user_id = "test_user_" + str(uuid.uuid4()).replace("-", "")
    email = f"{user_id}@example.com"
    username = "TestUser"
    
    # Create a test user
    user_ref = self.db.collection('users').document(user_id)
    user_ref.set({
        'email': email,
        'username': username,
        'gists': [],
        'links': []
    })
    
    # Create a link with auto_create_gist=true
    link = {
        "category": "Technology",
        "gist_created": {
            "link_title": "Test Link",
            "url": "https://example.com/test-article",
            "image_url": "https://example.com/test-image.jpg"
        }
    }
    
    # Mock the CrewAI service
    with patch('Firebase.services.CrewAIService') as mock_crew_ai_service:
        # Set up the mock
        mock_instance = mock_crew_ai_service.return_value
        mock_instance.update_gist_status.return_value = {"success": True}
        
        # Store the link with auto_create_gist=true
        response = self.client.post(
            "/api/links/store",
            json={"user_id": user_id, "link": link, "auto_create_gist": True}
        )
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("gistId", data)
        gist_id = data["gistId"]
        
        # Verify that the gist was created
        user_data = user_ref.get().to_dict()
        gists = user_data.get('gists', [])
        self.assertTrue(any(gist.get('gistId') == gist_id for gist in gists))
        
        # Verify that the link's gist_created status was updated
        links = user_data.get('links', [])
        link_updated = False
        for link in links:
            if link.get('gist_created', {}).get('gist_id') == gist_id:
                link_updated = True
                self.assertTrue(link.get('gist_created', {}).get('gist_created'))
                break
        self.assertTrue(link_updated)
        
        # Verify that the CrewAI service was called
        mock_instance.update_gist_status.assert_called_once()
        args, kwargs = mock_instance.update_gist_status.call_args
        self.assertEqual(args[0], user_id)
        self.assertEqual(args[1], gist_id)
    
    # Clean up
    user_ref.delete()
```

### Adding a Test for auto_create_gist=false

```python
def test_link_without_auto_create_gist(self):
    """
    Test storing a link with auto_create_gist=false
    
    This test verifies that:
    1. A link can be stored with auto_create_gist=false
    2. No gist is created
    3. The link's gist_created status is not updated
    """
    # Test data
    user_id = "test_user_" + str(uuid.uuid4()).replace("-", "")
    email = f"{user_id}@example.com"
    username = "TestUser"
    
    # Create a test user
    user_ref = self.db.collection('users').document(user_id)
    user_ref.set({
        'email': email,
        'username': username,
        'gists': [],
        'links': []
    })
    
    # Create a link with auto_create_gist=false
    link = {
        "category": "Technology",
        "gist_created": {
            "link_title": "Test Link",
            "url": "https://example.com/test-article",
            "image_url": "https://example.com/test-image.jpg"
        }
    }
    
    # Store the link with auto_create_gist=false
    response = self.client.post(
        "/api/links/store",
        json={"user_id": user_id, "link": link, "auto_create_gist": False}
    )
    
    # Verify the response
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["message"], "Link stored successfully")
    self.assertNotIn("gistId", data)
    
    # Verify that no gist was created
    user_data = user_ref.get().to_dict()
    gists = user_data.get('gists', [])
    self.assertEqual(len(gists), 0)
    
    # Clean up
    user_ref.delete()
```

These updates will ensure that the Firebase config tests properly verify the auto-create gist functionality. 