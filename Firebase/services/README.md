# Service Clients

This directory contains service client modules for interacting with external APIs.

## Overview

This project, Gista-CrewAI, consists of two main components:

1. **Gista**: The client application built on Firebase that manages user gists (content snippets created from links)
2. **CrewAI Service**: An external service that processes gists created in Gista

The integration between these components follows a simple workflow:
- Gista creates and stores gists in Firebase
- Gista notifies CrewAI Service about new gists via the `update_gist_status` API call
- CrewAI Service then accesses the gist and performs its processing workflow

This directory contains the client modules needed for Gista to communicate with the CrewAI Service.

## Module Structure

- `crew_ai_service.py`: Client for the CrewAI service API
- `env_utils.py`: Utilities for environment variable handling
- `test_crew_ai_service.py`: Test script for the CrewAI service client
- `run_test.py`: Helper script for running tests with environment setup
- `test_runner.py`: Improved test runner with proper import handling

## CrewAI Service Client

The `crew_ai_service.py` module provides a client for interacting with the CrewAI service API. It handles all service-to-service communication with the CrewAI backend.

### Features

- Automatic retry with exponential backoff
- Comprehensive error handling and logging
- Environment-based configuration
- Clean, modular API for all CrewAI endpoints

### Usage

```python
from Firebase.services import CrewAIService

# Initialize the service client
crew_ai_service = CrewAIService()

# Get a specific gist for a user
gist = crew_ai_service.get_user_gist(user_id, gist_id)

# Update a gist's production status
updated_gist = crew_ai_service.update_gist_status(
    user_id, 
    gist_id, 
    inProduction=True, 
    production_status="In Production"
)

# Batch update multiple gists
result = crew_ai_service.batch_update_gists(
    user_id, 
    gist_ids=["gist1", "gist2"], 
    inProduction=True, 
    production_status="Completed"
)

# Update a gist with links
updated_gist = crew_ai_service.update_gist_with_links(
    user_id, 
    gist_id, 
    links=[{"url": "https://example.com", "title": "Example"}],
    inProduction=True, 
    production_status="Completed"
)
```

## Environment Utilities

The `env_utils.py` module provides utilities for loading and checking environment variables. It centralizes the environment configuration logic used across service modules.

### Features

- Consistent environment variable loading
- Path resolution for finding the root `.env` file
- Validation of required environment variables
- Fallback mechanisms for missing variables

### Usage

```python
from Firebase.services.env_utils import find_and_load_env_file, check_required_vars, get_env_with_fallback

# Load environment variables from the root .env file
env_path = find_and_load_env_file()

# Check if required variables are set
required_vars = ['CREW_AI_API_BASE_URL', 'SERVICE_API_KEY']
results = check_required_vars(required_vars)
if results['all_set']:
    print("All required variables are set")
else:
    print("Some required variables are missing")

# Get a variable with fallback options
api_url = get_env_with_fallback(
    'CREW_AI_API_BASE_URL',
    'API_BASE_URL',
    'https://default-api-url.com'
)
```

## Configuration

The service clients are configured using environment variables:

- `CREW_AI_API_BASE_URL`: Base URL for the CrewAI API (default: https://api-yufqiolzaa-uc.a.run.app/api)
- `SERVICE_API_KEY`: API key for authenticating with the CrewAI service
- `API_MAX_RETRIES`: Maximum number of retry attempts for failed requests (default: 3)
- `API_RETRY_DELAY`: Base delay in seconds between retry attempts (default: 1)

## Testing

To test the service client, run:

```bash
cd Firebase/services
python test_runner.py
```

The `test_runner.py` script will:
1. Set up the Python path to ensure modules can be imported correctly
2. Load environment variables from the root `.env` file
3. Set default values for optional variables
4. Run the test script with the configured environment

Alternatively, you can use the `run_test.py` script which provides an interactive prompt for missing environment variables:

```bash
cd Firebase/services
python run_test.py
```

## Integration Points

The CrewAI service client is integrated at the following points:

1. **Gist Creation**: When a new gist is created in Gista (Firebase), the `add_gist` function in `Firebase/APIs/links.py` calls the CrewAI service to notify it about the new gist. The workflow is as follows:
   - A link is added to a user's profile using the `/links/store` endpoint
   - A gist is created from that link using the `/gists/add/:user_id` endpoint
   - The `add_gist` function calls `update_gist_status` to notify CrewAI about the new gist with initial production values
   - This notification triggers CrewAI's workflow to access and process the gist
   - The link's `gist_created` status is updated to reflect that a gist has been created

## Testing the Integration

The integration between Firebase and the CrewAI service can be tested using the following methods:

### Using the Firebase Cloud Functions

1. **Add a Link**:
   ```bash
   curl -X POST "http://localhost:5001/api/links/store" \
     -H "Content-Type: application/json" \
     -d '{"user_id":"USER_ID","link":{"category":"Category","title":"Link Title","url":"https://example.com/article"}}'
   ```

2. **Create a Gist from the Link**:
   ```bash
   curl -X POST "http://localhost:5001/api/gists/add/USER_ID" \
     -H "Content-Type: application/json" \
     -d '{"gistId":"gist_123","title":"Gist Title","category":"Category","link":"https://example.com/article","image_url":"https://example.com/image.jpg","link_id":"LINK_ID","segments":[{"title":"Segment Title","audioUrl":"","duration":"90","index":0}],"status":{"production_status":"Reviewing Content","inProduction":false}}'
   ```

3. **Verify the Gist Creation**:
   ```bash
   curl -X GET "http://localhost:5001/api/gists/USER_ID" \
     -H "Content-Type: application/json"
   ```

4. **Verify the Link Update**:
   ```bash
   curl -X GET "http://localhost:5001/api/links/USER_ID" \
     -H "Content-Type: application/json"
   ```

### Using the Test Scripts

The `test_gist_integration.py` script can be used to test the integration between Firebase and the CrewAI service:

```bash
cd Firebase/services
python test_gist_integration.py
```

This script tests the following:
- Creating a gist in Firebase
- Verifying that the CrewAI service is called to register the gist
- Checking that the gist status is updated correctly

## Verifying CrewAI Service Calls

To verify that the CrewAI service is being notified after a gist is created, you can:

1. **Check the logs**: The `crew_ai_service.py` module logs all API calls. You can check these logs to see if the service is being called.

2. **Add debug logging**: Add additional logging to the `add_gist` function to track when the CrewAI service is called.

3. **Use a test user**: Create a test user and monitor all API calls made for that user.

4. **Monitor network traffic**: Use a tool like Wireshark or the browser's network inspector to monitor API calls.

## Error Handling

The service client includes robust error handling:

- Failed requests are automatically retried with exponential backoff
- Errors are logged but don't cause the main API call to fail
- All exceptions are properly caught and handled

## Future Enhancements

Potential future enhancements for the service client:

1. Add a message queue for failed requests to ensure eventual consistency
2. Implement a circuit breaker pattern to prevent cascading failures
3. Add more comprehensive metrics and monitoring
4. Implement caching for frequently accessed data 