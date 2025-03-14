# Subcollection API Guide

## Overview

This guide documents the API endpoints for the CrewAI backend using the new subcollection-based data structure. The API maintains the same endpoint URLs for client compatibility while changing the underlying implementation to use subcollections.

## Database Structure

The database has been updated to use a subcollection-based structure:

```
/users/{userId}/                       # User document with basic user information
    /gists/{gistId}/                   # Gist subcollection - individual gists owned by a user
        /links/{linkId}/               # Links subcollection - links associated with a specific gist
    /links/{linkId}/                   # General links subcollection - all links owned by a user
```

This structure provides better scalability, performance, and flexibility compared to the previous flat structure.

## API Endpoints

The API is available at the following endpoints:

- **Standard API**: `https://us-central1-dof-ai.cloudfunctions.net/api`
- **Subcollection API**: `https://us-central1-dof-ai.cloudfunctions.net/apiSubcollections`

Both endpoints implement the same functionality using subcollections under the hood. The separate endpoints allow for a gradual migration.

### Gist Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gists/{userId}` | Get all gists for a user |
| GET | `/api/gists/{userId}/{gistId}` | Get a specific gist by ID |
| PUT | `/api/gists/{userId}/{gistId}/status` | Update gist production status (signal-based) |
| PUT | `/api/gists/{userId}/batch/status` | Update the status of multiple gists |
| PUT | `/api/gists/{userId}/{gistId}/with-links` | Update a gist with links and status |

### Link Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/links/store` | Store a link (and optionally create a gist) |
| GET | `/api/links/{userId}` | Get all links for a user |
| POST | `/api/links/update/{userId}` | Update a link |

## Signal-Based API for Updating Gist Status

The endpoint for updating a gist's status (`PUT /api/gists/{userId}/{gistId}/status`) has been implemented as a signal-based endpoint. This means:

1. No request body is required - simply making the PUT request triggers the status update
2. The server handles setting `inProduction: true` and `production_status: "In Production"` internally
3. The endpoint returns a success response if the gist exists, or failure if the gist doesn't exist
4. When successful, the response includes the link URL string in the response body

### Response Format

```json
{
  "message": "Gist status updated successfully",
  "status": {
    "inProduction": true,
    "production_status": "In Production"
  }
}
```

### Example Usage (Python)

```python
# Python example
response = requests.put(
    f"{BASE_URL}/api/gists/{user_id}/{gist_id}/status", 
    headers=headers,
    json={}  # Empty JSON object - signal-based approach
)

# Check response
if response.status_code == 200:
    # Success - get the link URL from the response
    link_url = response.json().get('link')
    print(f"Gist status updated successfully. Link URL: {link_url}")
else:
    print(f"Failed to update gist status: {response.status_code}")
```

### Example Usage (JavaScript)

```javascript
// JavaScript example
fetch(`${BASE_URL}/api/gists/${userId}/${gistId}/status`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({})  // Empty JSON object - signal-based approach
})
.then(response => response.json())
.then(data => {
  console.log('Gist status updated successfully');
  if (data.link) {
    console.log('Link URL:', data.link);
  }
})
.catch(error => console.error('Error updating gist status:', error));
```

## Internal API Implementation

While the client-facing API endpoints remain the same, the internal implementation has been updated to use the subcollection structure:

1. Direct fetching of gists and links is now handled via the `gistOperations` service rather than HTTP endpoints
2. When a client requests data, the service queries the appropriate subcollections instead of arrays in user documents
3. Response formats remain the same to ensure backward compatibility

## Deployed Endpoints

The API is fully deployed and available at:

1. **Standard API**: `https://us-central1-dof-ai.cloudfunctions.net/api`
   - Implements subcollection-based functionality
   - Maintains backward compatibility for clients

2. **Subcollection API**: `https://us-central1-dof-ai.cloudfunctions.net/apiSubcollections`
   - Specifically named to indicate it uses the subcollection structure
   - Functionally identical to the standard API

## Authentication

All API endpoints require authentication using an API key:

```
X-API-Key: YOUR_API_KEY
```

## Error Handling

The API returns standard HTTP status codes:

- 200: Success
- 400: Bad Request (missing required parameters)
- 401: Unauthorized (missing or invalid API key)
- 404: Not Found (resource not found)
- 500: Internal Server Error 