# Gista-CrewAI Backend API

## Overview
This project provides a backend API implementation using Google Cloud Functions and Firebase, designed to support iOS applications with features including user authentication, gist management, link operations, and seamless AI-powered content processing.

## Features
- User Authentication (Google Sign-In, Email/Password)
- Gist Management (Create, Read, Update, Delete)
- Link Operations (Store, Retrieve, Update)
- Automatic AI Content Processing
- Push Notifications
- Robust Error Handling and Graceful Degradation

## Project Structure
```
Gista-CrewAI/
├── Firebase/                  # Firebase Cloud Functions
│   ├── APIs/                  # API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── links.py           # Link and gist operations
│   │   └── testAPIs.py        # Unit tests for APIs
│   ├── config/                # Configuration files
│   ├── services/              # Service clients
│   │   ├── crew_ai_service.py # CrewAI service client
│   │   └── env_utils.py       # Environment utilities
│   └── .env.example           # Example environment variables
├── functions/                 # Test scripts and utilities
│   └── test_crewai-backend_endpoints.py # API endpoint tests
├── docs/                      # Documentation
│   ├── api/                   # API documentation
│   │   ├── API-Documentation.md # API endpoints documentation
│   │   ├── SERVICE_INTEGRATION.md # Service integration documentation
│   │   └── SERVICE_CLIENTS.md # Service client modules documentation
│   ├── deployment/            # Deployment guides
│   ├── testing/               # Testing documentation
│   ├── development/           # Development notes
│   │   └── debug/             # Debug-related documentation
│   └── security/              # Security documentation
├── scripts/                   # Utility scripts
│   ├── prepare_for_deployment.sh # Deployment preparation script
│   ├── run_all_tests.sh       # Script to run all tests
│   └── run_tests_with_server.sh # Script to run tests with server
├── tests/                     # Organized test suite
│   ├── unit/                  # Unit tests
│   │   ├── test_firebase.py   # Firebase configuration tests
│   │   └── test_apis.py       # API endpoint tests
│   ├── integration/           # Integration tests
│   │   ├── test_api_live.py   # Live API tests
│   │   └── test_auto_create_gist.py # Auto-create gist tests
│   ├── e2e/                   # End-to-end tests
│   │   └── test_crewai-backend_endpoints.py # Backend endpoint tests
│   ├── run_all_tests.py       # Test runner script
│   └── run_tests_with_server.py # Test runner with server script
└── Service-Service-README.md  # Legacy service integration documentation
```

## Setup
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   # Firebase Configuration
   FIREBASE_TYPE=service_account
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   FIREBASE_PRIVATE_KEY=your-private-key
   FIREBASE_CLIENT_EMAIL=your-client-email
   FIREBASE_CLIENT_ID=your-client-id
   FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
   FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
   FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
   FIREBASE_CLIENT_CERT_URL=your-client-cert-url
   
   # API Configuration
   SERVICE_API_KEY=your-service-api-key
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Deploy to Google Cloud Functions: `firebase deploy --only functions`

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **API Documentation**: Detailed documentation of the API endpoints and their usage
- **Deployment Guides**: Step-by-step guides for deploying the API
- **Testing Documentation**: Guides for testing the API endpoints
- **Development Notes**: Notes from development sessions
- **Security Documentation**: Security-related documentation and scripts

See the [Documentation Index](docs/README.md) for a complete list of available documentation.

## Scripts

Utility scripts are available in the `scripts/` directory:

- **prepare_for_deployment.sh**: Script for preparing the codebase for deployment
- **run_all_tests.sh**: Script for running all tests
- **run_tests_with_server.sh**: Script for running tests that require the server

See the [Scripts README](scripts/README.md) for more information.

## API Documentation

### Authentication Endpoints

#### Sign In
```
POST /api/auth/signin
```
Request body:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Create User
```
POST /api/auth/create
```
Request body:
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "display_name": "New User"
}
```

### Link Operations

#### Store Link
```
POST /api/links/store
```
Request body:
```json
{
  "user_id": "user123",
  "link": {
    "title": "Example Link",
    "url": "https://example.com",
    "imageUrl": "https://example.com/image.jpg",
    "linkType": "weblink",
    "categoryId": "category123",
    "categoryName": "Technology"
  },
  "auto_create_gist": true  // Optional, defaults to true
}
```

**Note**: The enhanced `/api/links/store` endpoint now supports automatically creating a gist when a link is stored. When `auto_create_gist` is set to `true` (default), the endpoint will:
1. Store the link in the user's profile
2. Create a gist from the link with default values
3. Update the link's `gist_created` status
4. Notify the CrewAI service about the new gist
5. Return the gistId in the response

Response when `auto_create_gist` is true:
```json
{
  "gistId": "gist_9876543210"
}
```

Response when `auto_create_gist` is false:
```json
{
  "message": "Link stored successfully"
}
```

#### Get Links
```
GET /api/links/{user_id}
```

#### Update Link
```
POST /api/links/update/{user_id}
```
Request body:
```json
{
  "title": "Updated Link",
  "url": "https://example.com/updated",
  "imageUrl": "https://example.com/updated-image.jpg",
  "linkType": "weblink",
  "categoryId": "category123",
  "categoryName": "Technology"
}
```

### Gist Operations

#### Gist Type Definition

```typescript
// Segment interface - represents a segment within a gist
interface Segment {
  // Required fields
  title: string;                // Title of the segment
  audioUrl: string;             // URL to the audio file
  duration: string;             // Duration of the segment in seconds (as a string)
  index: number;                // Position of the segment (integer)
}

// GistStatus interface - represents the status of a gist
interface GistStatus {
  production_status: string;    // Status of production (default: "Reviewing Content")
  inProduction: boolean;        // Whether the gist is in production (default: false)
}

// Gist interface - represents a complete gist object
interface Gist {
  // Required fields
  title: string;                // Title of the gist
  image_url: string;            // URL to the image associated with the gist
  link: string;                 // URL of the content that the gist is based on
  category: string;             // Category of the gist
  link_id: string;              // ID of the link that this gist is associated with
  segments: Segment[];          // Array of segments (must contain at least one segment)
  
  // Optional fields with defaults
  gistId?: string;              // Unique identifier (generated if not provided)
  isFinished: boolean;          // Whether the gist is finished (default: false)
  is_played: boolean;           // Whether the gist has been played (default: false)
  is_published: boolean;        // Whether the gist is published (default: true)
  playbackDuration: number;     // Duration of the gist in seconds (default: 0)
  playbackTime: number;         // Current playback time (default: 0)
  publisher: string;            // Publisher of the gist (default: "theNewGista")
  ratings: number;              // Ratings for the gist (default: 0)
  users: number;                // Number of users who have interacted with the gist (default: 0)
  date_created?: string;        // Creation date (ISO format, generated if not provided)
  status: GistStatus;           // Status object
}
```

##### GistStatus Details

The `GistStatus` interface represents the production and playback status of a Gist:

###### production_status

The `production_status` property indicates the current state of the Gist in the production pipeline. It must be one of the following values:

- **"Reviewing Content"**: The initial state when a Gist is created. The system is reviewing the content before processing.
- **"In Production"**: The Gist is currently being processed by the production system.
- **"Completed"**: The Gist has been successfully processed and is ready for playback.
- **"Failed"**: The production process encountered an error and could not complete successfully.

Default value: `"Reviewing Content"`

###### inProduction

The `inProduction` property is a boolean flag that indicates whether the Gist is currently in production.

- `true`: The Gist is in production and being processed.
- `false`: The Gist is not in production.

Default value: `false`

##### Status Transitions

The typical lifecycle of a Gist's status is:

1. **"Reviewing Content"** (initial state)
   - `inProduction`: false
   
2. **"In Production"** (when processing begins)
   - `inProduction`: true
   
3. **"Completed"** (when processing is successful)
   - `inProduction`: false
   
OR

3. **"Failed"** (when processing encounters an error)
   - `inProduction`: false

##### Updating a Gist's Status

To update a Gist's status, use the `/api/gists/update/{user_id}/{gist_id}` endpoint with a PUT request:

```typescript
const updateStatus = {
  status: {
    production_status: "In Production",
    inProduction: true
  }
};

fetch(`http://localhost:5001/api/gists/update/${userId}/${gistId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify(updateStatus)
});
```

##### Best Practices for Status Management

1. Always check if a Gist exists before attempting to update its status.
2. Implement retry logic with exponential backoff for transient errors.
3. Handle server errors gracefully in your client application.
4. Validate the `production_status` value before sending it to the API.
5. Consider implementing a state machine to manage Gist status transitions.

#### Add Gist
```
POST /api/gists/add/{user_id}
```
Request body:
```json
{
  "title": "Example Gist",
  "image_url": "https://example.com/image.jpg",
  "link": "https://example.com/article",
  "category": "Technology",
  "link_id": "link_123456",
  "segments": [
    {
      "title": "Introduction",
      "audioUrl": "https://example.com/audio1.mp3",
      "duration": "60",
      "index": 0
    },
    {
      "title": "Main Content",
      "audioUrl": "https://example.com/audio2.mp3",
      "duration": "120",
      "index": 1
    }
  ],
  "isFinished": false,
  "playbackDuration": 180,
  "playbackTime": 0
}
```

**Required Fields:**
- `title`: Title of the gist
- `image_url`: URL to the image associated with the gist (note the underscore)
- `link`: URL of the content that the gist is based on
- `category`: Category of the gist
- `link_id`: ID of the link that this gist is associated with (must be a link previously stored with the `/api/links/store` endpoint)
- `segments`: Array of segments (must be a non-empty array)
  - Each segment must have:
    - `title`: Title of the segment
    - `audioUrl`: URL to the audio file
    - `duration`: Duration of the segment in seconds (as a string)
    - `index`: Position of the segment (integer)

**Optional Fields:**
- `gistId`: Unique identifier for the gist (if not provided, one will be generated). For testing and tracking purposes, it's recommended to provide a specific gistId.
- `isFinished`: Boolean indicating if the gist is finished (default: false)
- `playbackDuration`: Duration of the gist in seconds (default: 0)
- `playbackTime`: Current playback time (default: 0)
- `publisher`: Publisher of the gist (default: "theNewGista")
- `ratings`: Ratings for the gist (default: 0)
- `users`: Number of users who have interacted with the gist (default: 0)
- `is_published`: Boolean indicating if the gist is published (default: true)
- `status`: Object containing status information (default: `{ production_status: "Reviewing Content", inProduction: false }`)
  - `production_status`: Status of production
    - Valid values: "Reviewing Content", "In Production", "Completed", "Failed"
  - `inProduction`: Boolean indicating if the gist is in production

Response:
```json
{
  "message": "Gist added successfully",
  "gist": {
    "gistId": "gist_123456",
    "title": "Example Gist",
    "image_url": "https://example.com/image.jpg",
    "link": "https://example.com/article",
    "category": "Technology",
    "date_created": "2023-06-15T10:30:00.000Z",
    "is_played": false,
    "is_published": true,
    "playback_duration": 180,
    "publisher": "theNewGista",
    "ratings": 0,
    "segments": [
      {
        "segment_title": "Introduction",
        "segment_audioUrl": "https://example.com/audio1.mp3",
        "playback_duration": "60",
        "segment_index": "0"
      },
      {
        "segment_title": "Main Content",
        "segment_audioUrl": "https://example.com/audio2.mp3",
        "playback_duration": "120",
        "segment_index": "1"
      }
    ],
    "status": {
      "production_status": "Reviewing Content",
      "inProduction": false
    },
    "users": 0
  }
}
```

#### Get Gists
```
GET /api/gists/{user_id}
```

#### Get Gist
```
GET /api/gists/{user_id}/{gist_id}
```

## Client Integration Guide

When integrating with the Gista-CrewAI API, clients should follow these best practices:

### Authentication
- Always use HTTPS for all API calls
- Include authentication headers for protected endpoints
- Store API keys securely and never expose them in client-side code

### Error Handling
- Implement retry logic with exponential backoff for transient errors
- Handle 4xx and 5xx errors gracefully
- Display user-friendly error messages

### Gist Creation Workflow
1. Store a link using the `/api/links/store` endpoint
2. Create a gist from the link using the `/api/gists/add/{user_id}` endpoint
3. The API will automatically process the gist content (no additional client action required)
4. Poll the gist status periodically to check for updates

### Example Client Code (Swift)

```swift
import Foundation

// MARK: - Segment
struct Segment: Codable {
    let title: String
    let audioUrl: String
    let duration: String
    let index: Int
}

// MARK: - GistStatus
struct GistStatus: Codable {
    var productionStatus: String
    var inProduction: Bool
    
    enum CodingKeys: String, CodingKey {
        case productionStatus = "production_status"
        case inProduction = "inProduction"
    }
}

// MARK: - Gist
struct Gist: Codable {
    let title: String
    let imageUrl: String
    let link: String
    let category: String
    let linkId: String
    let segments: [Segment]
    var gistId: String?
    var isFinished: Bool
    var isPlayed: Bool?
    var isPublished: Bool?
    var playbackDuration: Int
    var playbackTime: Int
    var publisher: String?
    var ratings: Int?
    var users: Int?
    var dateCreated: String?
    var status: GistStatus?
    
    enum CodingKeys: String, CodingKey {
        case title
        case imageUrl = "image_url"
        case link
        case category
        case linkId = "link_id"
        case segments
        case gistId
        case isFinished
        case isPlayed = "is_played"
        case isPublished = "is_published"
        case playbackDuration
        case playbackTime
        case publisher
        case ratings
        case users
        case dateCreated = "date_created"
        case status
    }
}

class GistaAPIClient {
    private let baseURL = "https://us-central1-dof-ai.cloudfunctions.net/api"
    private let apiKey: String
    
    init(apiKey: String) {
        self.apiKey = apiKey
    }
    
    func addGist(userId: String, gist: Gist, completion: @escaping (Result<Gist, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/gists/add/\(userId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        do {
            let encoder = JSONEncoder()
            request.httpBody = try encoder.encode(gist)
            
            URLSession.shared.dataTask(with: request) { data, response, error in
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NSError(domain: "No data", code: 0, userInfo: nil)))
                    return
                }
                
                do {
                    let decoder = JSONDecoder()
                    let response = try decoder.decode(GistResponse.self, from: data)
                    completion(.success(response.gist))
                } catch {
                    completion(.failure(error))
                }
            }.resume()
        } catch {
            completion(.failure(error))
        }
    }
}

// MARK: - GistResponse
struct GistResponse: Codable {
    let message: String
    let gist: Gist
}
```

## Development
- Follow PEP 8 style guide
- Document all functions and classes
- Use type hints
- Write unit tests for new features

## Testing

The project includes a comprehensive test suite organized into unit tests, integration tests, and end-to-end tests.

### Running Tests

#### Using the Test Runner with Server

The `run_tests_with_server.py` script automatically starts the Flask development server, runs the tests, and then stops the server:

```bash
# Run all tests with server
python tests/run_tests_with_server.py

# Run only unit tests with server
python tests/run_tests_with_server.py --unit

# Run only integration tests with server
python tests/run_tests_with_server.py --integration

# Run only end-to-end tests with server
python tests/run_tests_with_server.py --e2e
```

#### Using the Test Runner

The `run_all_tests.py` script provides a convenient way to run all tests without automatically starting the server:

```bash
# Run all tests
python tests/run_all_tests.py

# Run only unit tests
python tests/run_all_tests.py --unit

# Run only integration tests
python tests/run_all_tests.py --integration

# Run only end-to-end tests
python tests/run_all_tests.py --e2e
```

For more information about testing, see the [tests/README.md](tests/README.md) file.

## Deployment
1. Ensure all tests pass
2. Update the version number in `package.json`
3. Deploy to Google Cloud Functions:
   ```
   firebase deploy --only functions
   ```

## Monitoring and Logging
- Monitor API usage and performance using Firebase Console
- Check logs for errors and warnings
- Set up alerts for critical errors

## Support
For questions or issues, please contact the development team or open an issue on GitHub.