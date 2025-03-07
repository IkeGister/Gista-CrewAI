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
2. Create a test link
3. Create a test gist with the updated GistStatus interface
4. Get the user's gists
5. Update the gist's status using the updated GistStatus interface
6. Delete the test gist
7. Delete the test user

The test script generates unique IDs for each test run to ensure isolation between test runs. It explicitly sets a `gistId` in the request payload when creating a gist, which is important for tracking the gist throughout the test.

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

## Troubleshooting

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