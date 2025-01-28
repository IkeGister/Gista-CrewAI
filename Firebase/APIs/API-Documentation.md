Firebase/
│
├── APIs/
│   ├── __init__.py
│   ├── auth.py
│   ├── storage.py
│   ├── analytics.py
│   └── payments.py
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_storage.py
│   ├── test_analytics.py
│   └── test_payments.py
│
└── utils/
    ├── __init__.py
    └── firebase_utils.py

# Firebase API Documentation

## Overview
This document outlines the APIs for the Gista application, including authentication, gist management, link management, and Firebase services integration. The APIs are built using Firebase Cloud Functions and follow RESTful principles.

## Base URL
- **Development**: `http://localhost:5001`
- **Production**: `https://us-central1-dof-ai.cloudfunctions.net/api`

## Current API Endpoints

### 1. Authentication API (`/auth`)

#### POST /auth/create-user
- **Description**: Create a new user in Firebase Authentication and Firestore.
- **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword",
      "username": "username123"
    }
    ```
- **Responses**:
    - **201**: User created successfully
        ```json
        {
          "message": "User created successfully",
          "userId": "user123"
        }
        ```
    - **500**: Error creating user

#### PUT /auth/update-user
- **Description**: Update user information in Firestore.
- **Headers**: 
    - `Authorization: Bearer <token>`
- **Request Body**:
    ```json
    {
      "username": "newUsername",
      "email": "newemail@example.com"
    }
    ```
- **Responses**:
    - **200**: User updated successfully
    - **401**: No token provided
    - **500**: Error updating user

### 2. Links API (`/links`)

#### POST /links/store
- **Description**: Store a new link for processing into a gist.
- **Request Body**:
    ```json
    {
      "user_id": "user123",
      "link": {
        "category": "Technology",
        "url": "https://example.com/article"
      }
    }
    ```
- **Responses**:
    - **200**: Link stored successfully
        ```json
        {
          "message": "Link stored successfully",
          "link": {
            "link_id": "link_123",
            "category": "Technology",
            "date_added": "2024-01-25T09:00:00Z",
            "gist_created": {
              "gist_created": false,
              "gist_id": null,
              "image_url": null,
              "link_id": "link_123",
              "link_title": "",
              "link_type": "Web",
              "url": "https://example.com/article"
            }
          }
        }
        ```
    - **400**: Invalid input data
    - **500**: Error storing link

#### GET /links/:user_id
- **Description**: Retrieve all links for a user.
- **Parameters**:
    - `user_id`: User's unique identifier
- **Responses**:
    - **200**: Returns array of links and count
        ```json
        {
          "links": [{
            "category": "Technology",
            "date_added": "2024-01-25T09:00:00Z",
            "gist_created": {
              "gist_created": false,
              "gist_id": null,
              "image_url": null,
              "link_id": "link_123",
              "link_title": "",
              "link_type": "Web",
              "url": "https://example.com/article"
            }
          }],
          "count": 1
        }
        ```
    - **404**: User not found

### 3. Gists API (`/gists`)

#### POST /gists/add/:user_id
- **Description**: Create a new gist from processed content.
- **Parameters**:
    - `user_id`: User's unique identifier
- **Request Body**:
    ```json
    {
      "title": "Tech Trends Gist",
      "link": "https://example.com/article",
      "image_url": "https://example.com/image.jpg",
      "category": "Technology",
      "segments": [{
        "segment_duration": 90,
        "segment_index": 0,
        "segment_title": "Introduction"
      }],
      "playback_duration": 180
    }
    ```
- **Responses**:
    - **200**: Gist created successfully
    - **400**: Missing required fields
    - **500**: Error creating gist

#### PUT /gists/update/:user_id/:gist_index
- **Description**: Update gist status and metadata.
- **Parameters**:
    - `user_id`: User's unique identifier
    - `gist_index`: Index of the gist in user's gists array
- **Request Body**:
    ```json
    {
      "status": {
        "is_done_playing": true,
        "is_now_playing": false,
        "playback_time": 180
      },
      "is_played": true,
      "ratings": 5
    }
    ```
- **Responses**:
    - **200**: Gist updated successfully
    - **404**: Gist not found
    - **500**: Error updating gist

#### GET /gists/:user_id
- **Description**: Retrieve all gists for a user.
- **Parameters**:
    - `user_id`: User's unique identifier
- **Responses**:
    - **200**: Returns array of gists
        ```json
        {
          "gists": [{
            "title": "Tech Trends Gist",
            "category": "Technology",
            "date_created": "2024-01-25T08:30:00Z",
            "image_url": "https://example.com/image.jpg",
            "is_played": false,
            "is_published": true,
            "link": "https://example.com/article",
            "playback_duration": 180,
            "publisher": "theNewGista",
            "ratings": 0,
            "segments": [{
              "segment_duration": 90,
              "segment_index": 0,
              "segment_title": "Introduction"
            }],
            "status": {
              "is_done_playing": false,
              "is_now_playing": false,
              "playback_time": 0
            }
          }]
        }
        ```
    - **404**: User not found

## Testing
Each API endpoint has corresponding test files. The tests cover:

- Authentication flows
- Link management operations
- Gist creation and updates
- Error handling
- Data validation

### Best Practices
- **Authentication**: All endpoints requiring authentication use Firebase Auth tokens
- **Data Validation**: Input validation on all POST/PUT requests
- **Error Handling**: Consistent error response format
- **Documentation**: Keep API documentation updated with changes
- **Testing**: Maintain comprehensive test coverage

## Security
- Firebase Authentication for user management
- Secure credential storage using service accounts
- Environment variable protection for sensitive data
- CORS enabled for specified origins

## Development Setup
1. Install dependencies: `npm install` in functions directory
2. Set up environment variables
3. Initialize Firebase Admin SDK with service account
4. Run locally: `firebase serve --only functions`

## Deployment
Deploy to Firebase Cloud Functions:
```bash
firebase deploy --only functions
```

The API will be available at: `https://us-central1-dof-ai.cloudfunctions.net/api`
