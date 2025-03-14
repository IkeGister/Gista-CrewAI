# Firebase API Documentation

## Project Structure
Gista-CrewAI/
│
├── functions/
│   │   ├── src/
│   │   │   ├── auth/
│   │   │   │   └── userManagement.js
│   │   ├── categories/
│   │   │   └── categoriesManagement.js
│   │   ├── gists/
│   │   │   └── gistManagement.js
│   │   ├── links/
│   │   │   └── linkManagement.js
│   │   ├── index.js
│   │   └── service-account.json
│   ├── utilities/
│   │   ├── defaultCategories.js
│   │   └── initCategories.js
│   ├── package.json
│   └── .eslintrc.js
│
├── Firebase/
│   ├── APIs/
│   │   └── API-Documentation.md
│   └── config/
│       ├── firebase_config.py
│       └── test_firebase.py
│
├── .env
├── .gitignore
└── firebase.json

## Overview
This document outlines the APIs for the Gista application, including authentication, gist management, link management, and Firebase services integration. The APIs are built using Firebase Cloud Functions and follow RESTful principles.

## Base URL

The API is available at the following endpoints:

- **Production API**: `https://us-central1-dof-ai.cloudfunctions.net/api`
- **Subcollection API**: `https://us-central1-dof-ai.cloudfunctions.net/apiSubcollections`

Both endpoints provide identical functionality using the subcollection-based database structure. The API endpoints maintain backward compatibility with client applications.

## Authentication

All API endpoints require an API key to be included in the request headers:

```
X-API-Key: YOUR_API_KEY
```

## Endpoints

### Store Link

Stores a link in the database, optionally creating a gist.

**URL:** `/api/links/store`  
**Method:** `POST`  
**Auth Required:** Yes (API Key)

**Request Body:**
```json
{
  "user_id": "string",
  "link": {
    "title": "Example Link",
    "url": "https://example.com",
    "imageUrl": "https://example.com/image.jpg",
    "linkType": "weblink",
    "categoryId": "category123",
    "categoryName": "Technology"
  },
  "auto_create_gist": true
}
```

**Important Notes:**
- Use camelCase for properties: `imageUrl`, `linkType`, `categoryName`
- The `link` object properties should be directly under `link`, not nested
- The `user_id` must be an existing user in the system
- When `auto_create_gist` is `true`, a gist will be automatically created and the signal-based status update will be triggered

**Success Response:**
```json
{
  "message": "Link stored successfully"
}
```

Or if a gistId is returned:
```json
{
  "message": "Link stored successfully",
  "gistId": "string"
}
```

### Get User Links

Retrieves all links for a specific user.

**URL:** `/api/links/{userId}`  
**Method:** `GET`  
**Auth Required:** Yes (API Key)

**Success Response:**
```json
{
  "links": [
    {
      "id": "string",
      "url": "string",
      "title": "string",
      "description": "string",
      "imageUrl": "string",
      "tags": ["string"],
      "createdAt": "timestamp",
      "updatedAt": "timestamp"
    }
  ]
}
```

### Update Link

Updates an existing link.

**URL:** `/api/links/update/{userId}`  
**Method:** `POST`  
**Auth Required:** Yes (API Key)

**Request Body:**
```json
{
  "linkId": "string",
  "title": "string",
  "description": "string",
  "imageUrl": "string",
  "tags": ["string"]
}
```

**Success Response:**
```json
{
  "success": true,
  "linkId": "string",
  "updatedLink": "link object"
}
```

### Add Gist

Creates a new gist and associates links with it.

**URL:** `/api/gists/add`  
**Method:** `POST`  
**Auth Required:** Yes (API Key)

**Request Body:**
```json
{
  "userId": "string",
  "gistTitle": "string",
  "gistDescription": "string",
  "gistStatus": "string",
  "linkIds": ["string"]
}
```

**Success Response:**
```json
{
  "success": true,
  "gistId": "string",
  "gist": "gist object"
}
```

### Get User Gists

Retrieves all gists for a specific user.

**URL:** `/api/gists/{userId}`  
**Method:** `GET`  
**Auth Required:** Yes (API Key)

**Success Response:**
```json
{
  "gists": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "status": "string",
      "inProduction": boolean,
      "production_status": "string",
      "createdAt": "timestamp",
      "updatedAt": "timestamp",
      "links": ["link objects"]
    }
  ]
}
```

### Get Specific Gist

Retrieves a specific gist by ID.

**URL:** `/api/gists/{userId}/{gistId}`  
**Method:** `GET`  
**Auth Required:** Yes (API Key)

**Success Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "status": "string",
  "inProduction": boolean,
  "production_status": "string",
  "createdAt": "timestamp",
  "updatedAt": "timestamp",
  "links": ["link objects"]
}
```

### Update Gist Status (Signal-Based)

Updates the production status of a gist using a signal-based approach.

**URL:** `/api/gists/{userId}/{gistId}/status`  
**Method:** `PUT`  
**Auth Required:** Yes (API Key)
**Request Body:** Empty JSON object `{}`

**Success Response:**
```json
{
  "message": "Gist status updated successfully",
  "status": {
    "inProduction": true,
    "production_status": "In Production"
  },
  "link": "string" (if available)
}
```

### Update Multiple Gist Statuses

Updates the status of multiple gists at once.

**URL:** `/api/gists/{userId}/batch/status`  
**Method:** `PUT`  
**Auth Required:** Yes (API Key)

**Request Body:**
```json
{
  "gistIds": ["string"],
  "status": "string",
  "inProduction": boolean,
  "production_status": "string"
}
```

**Success Response:**
```json
{
  "success": true,
  "updatedGists": ["gist IDs"]
}
```

### Update Gist with Links

Updates a gist with links and status.

**URL:** `/api/gists/{userId}/{gistId}/with-links`  
**Method:** `PUT`  
**Auth Required:** Yes (API Key)

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "status": "string",
  "linkIds": ["string"]
}
```

**Success Response:**
```json
{
  "success": true,
  "gistId": "string",
  "updatedGist": "gist object"
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad Request (missing required parameters)
- 401: Unauthorized (missing or invalid API key)
- 404: Not Found (resource not found)
- 500: Internal Server Error

Error responses include a message:

```json
{
  "error": "Error message"
}
```

## Database Structure

The API now uses a subcollection-based structure:

```
/users/{userId}/                       # User document
    /gists/{gistId}/                   # Gist subcollection
        /links/{linkId}/               # Links subcollection
    /links/{linkId}/                   # User's links subcollection
```

This structure improves scalability and query performance while maintaining the same API interface.

## Recommended Testing Flow in Hopscotch

1. Test the API connectivity with `GET /test`
2. Create a test user with `POST /auth/create_user`
3. Store a link and automatically create a gist with `POST /links/store` (with `auto_create_gist=true`)
4. Retrieve the user's gists with `GET /gists/:user_id`
5. Retrieve the user's links with `GET /links/:user_id`
6. Store another link without creating a gist with `POST /links/store` (with `auto_create_gist=false`)
7. Update the gist status using the signal-based approach with `PUT /gists/:user_id/:gist_id/status`
8. Delete the gist with `DELETE /gists/delete/:user_id/:gist_id`
9. Delete the user with `DELETE /auth/delete_user/:user_id`

## Security
- Firebase Authentication for user management
- Secure credential storage using service account
- Environment variable protection for sensitive data
- CORS enabled for specified origins

## Development Setup
1. Install dependencies: `npm install` in functions directory
2. Set up service account JSON file in `functions/src/`
3. Initialize Firebase Admin SDK with service account
4. Run locally: `firebase serve --only functions`

## Deployment
Deploy to Firebase Cloud Functions:
```bash
firebase deploy --only functions
```

The API will be available at: `https://us-central1-dof-ai.cloudfunctions.net/api`
