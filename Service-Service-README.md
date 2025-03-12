## 🔄 Service-to-Service Integration Guide

This section provides detailed instructions for integrating this API with your user service environment.

### Setting Up Your Service Environment

1. **Store the API Key Securely**

   Add the API key to your service's environment variables or secrets manager:
   
   ```bash
   # For Node.js applications
   export SERVICE_API_KEY=your-service-api-key-here
   
   # For Docker environments
   docker run -e SERVICE_API_KEY=your-service-api-key-here your-image
   
   # For Kubernetes
   kubectl create secret generic api-keys --from-literal=service-api-key=your-service-api-key-here
   ```

2. **Configure Base URL**

   Store the base URL in your configuration:
   
   ```javascript
   // config.js example
   module.exports = {
     crewAiApi: {
       baseUrl: 'https://api-yufqiolzaa-uc.a.run.app/api',
       apiKey: process.env.SERVICE_API_KEY
     }
   };
   ```

### Making API Calls from Your Service

#### Node.js Example with Axios

```javascript
const axios = require('axios');
const config = require('./config');

// Create an API client with default headers
const apiClient = axios.create({
  baseURL: config.crewAiApi.baseUrl,
  headers: {
    'X-API-Key': config.crewAiApi.apiKey,
    'Content-Type': 'application/json'
  }
});

// Example: Get all gists for a user
async function getUserGists(userId) {
  try {
    const response = await apiClient.get(`/gists/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user gists:', error.response?.data || error.message);
    throw error;
  }
}

// Example: Update gist status (Signal-based approach)
async function updateGistStatus(userId, gistId) {
  try {
    // Signal-based approach - empty JSON object
    const response = await apiClient.put(`/gists/${userId}/${gistId}/status`, {});
    return response.data;
  } catch (error) {
    console.error('Error updating gist status:', error.response?.data || error.message);
    throw error;
  }
}

// Example: Batch update gists
async function batchUpdateGists(userId, gistIds, inProduction, productionStatus) {
  try {
    const response = await apiClient.put(`/gists/${userId}/batch/status`, {
      gistIds,
      inProduction,
      production_status: productionStatus
    });
    return response.data;
  } catch (error) {
    console.error('Error batch updating gists:', error.response?.data || error.message);
    throw error;
  }
}

// Example: Update gist with links
async function updateGistWithLinks(userId, gistId, links, inProduction, productionStatus) {
  try {
    const response = await apiClient.put(`/gists/${userId}/${gistId}/with-links`, {
      links,
      inProduction,
      production_status: productionStatus
    });
    return response.data;
  } catch (error) {
    console.error('Error updating gist with links:', error.response?.data || error.message);
    throw error;
  }
}
```

#### Python Example with Requests

```python
import requests
import os

# Configuration
BASE_URL = "https://api-yufqiolzaa-uc.a.run.app/api"
API_KEY = os.environ.get("SERVICE_API_KEY")

# Default headers
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Example: Get all gists for a user
def get_user_gists(user_id):
    try:
        response = requests.get(f"{BASE_URL}/gists/{user_id}", headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user gists: {e}")
        raise

# Example: Update gist status (Signal-based approach)
def update_gist_status(user_id, gist_id):
    try:
        # Signal-based approach - empty JSON object
        response = requests.put(
            f"{BASE_URL}/gists/{user_id}/{gist_id}/status", 
            headers=headers,
            json={}  # Empty JSON object
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating gist status: {e}")
        raise

# Example: Batch update gists
def batch_update_gists(user_id, gist_ids, in_production, production_status):
    try:
        payload = {
            "gistIds": gist_ids,
            "inProduction": in_production,
            "production_status": production_status
        }
        response = requests.put(
            f"{BASE_URL}/gists/{user_id}/batch/status", 
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error batch updating gists: {e}")
        raise

# Example: Update gist with links
def update_gist_with_links(user_id, gist_id, links, in_production, production_status):
    try:
        payload = {
            "links": links,
            "inProduction": in_production,
            "production_status": production_status
        }
        response = requests.put(
            f"{BASE_URL}/gists/{user_id}/{gist_id}/with-links", 
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating gist with links: {e}")
        raise
```

### Error Handling Best Practices

1. **Implement Retry Logic**

   For transient failures, implement an exponential backoff retry strategy:

   ```javascript
   // Node.js example with axios-retry
   const axios = require('axios');
   const axiosRetry = require('axios-retry');

   const apiClient = axios.create({
     baseURL: config.crewAiApi.baseUrl,
     headers: { 'X-API-Key': config.crewAiApi.apiKey }
   });

   // Configure retry behavior
   axiosRetry(apiClient, {
     retries: 3,
     retryDelay: axiosRetry.exponentialDelay,
     retryCondition: (error) => {
       // Retry on network errors or 5XX responses
       return axiosRetry.isNetworkOrIdempotentRequestError(error) || 
              (error.response && error.response.status >= 500);
     }
   });
   ```

2. **Circuit Breaker Pattern**

   Implement a circuit breaker to prevent cascading failures:

   ```javascript
   // Node.js example with opossum
   const CircuitBreaker = require('opossum');

   const options = {
     failureThreshold: 50,
     resetTimeout: 10000,
     timeout: 3000
   };

   const getUserGistsBreaker = new CircuitBreaker(getUserGists, options);
   
   getUserGistsBreaker.fire('user123')
     .then(console.log)
     .catch(console.error);
   
   getUserGistsBreaker.on('open', () => console.log('Circuit breaker opened'));
   getUserGistsBreaker.on('close', () => console.log('Circuit breaker closed'));
   ```

### Monitoring and Logging

Implement proper logging for all API calls to facilitate debugging:

```javascript
// Request interceptor
apiClient.interceptors.request.use(request => {
  console.log(`[API Request] ${request.method.toUpperCase()} ${request.url}`);
  return request;
});

// Response interceptor
apiClient.interceptors.response.use(
  response => {
    console.log(`[API Response] ${response.status} ${response.config.method.toUpperCase()} ${response.config.url}`);
    return response;
  },
  error => {
    console.error(`[API Error] ${error.response?.status || 'Network Error'} ${error.config?.method?.toUpperCase() || 'UNKNOWN'} ${error.config?.url || 'Unknown URL'}`);
    return Promise.reject(error);
  }
);
```

### Important Notes About the Signal-Based API

1. **Single Gist Update Endpoint**

   The `/gists/{userId}/{gistId}/status` endpoint now uses a signal-based approach:
   
   - No request body is required - simply making the PUT request triggers the status update
   - The server handles setting `inProduction: true` and `production_status: "Reviewing Content"` internally
   - This simplifies integration by removing the need to specify payload data

2. **Other Endpoints**

   Note that only the single gist update endpoint uses the signal-based approach. The batch update and update-with-links endpoints still require full payloads with specific fields:
   
   - Batch update: Requires `gistIds`, `inProduction`, and `production_status` fields
   - Update with links: Requires `links`, `inProduction`, and `production_status` fields

### Auto-Create Gist Functionality

The `/api/links/store` endpoint has been enhanced to automatically create a gist when a link is stored. This simplifies the integration workflow by reducing the number of API calls required.

#### How It Works

1. When a link is stored with `auto_create_gist=true` (default), the endpoint will:
   - Store the link in the user's profile
   - Create a gist from the link with default values
   - Update the link's `gist_created` status
   - Notify the CrewAI service about the new gist
   - Return the gistId in the response

2. When `auto_create_gist=false`, the endpoint will:
   - Store the link in the user's profile
   - Return a success message

#### Example Usage

```javascript
// Node.js example with axios
async function storeLink(userId, link, autoCreateGist = true) {
  try {
    const response = await apiClient.post('/links/store', {
      user_id: userId,
      link: link,
      auto_create_gist: autoCreateGist
    });
    
    if (autoCreateGist) {
      // The response contains the gistId
      const gistId = response.data.gistId;
      console.log(`Link stored and gist created with ID: ${gistId}`);
      return gistId;
    } else {
      console.log('Link stored successfully without creating a gist');
      return null;
    }
  } catch (error) {
    console.error('Error storing link:', error.response?.data || error.message);
    throw error;
  }
}

// Example link data
const link = {
  category: "Technology",
  gist_created: {
    link_title: "Example Article",
    url: "https://example.com/article",
    image_url: "https://example.com/image.jpg"
  }
};

// Store link and create gist
const gistId = await storeLink('user123', link);

// Store link without creating gist
await storeLink('user123', link, false);
```

#### Benefits for Service Integration

1. **Simplified Workflow**: Reduces the number of API calls required to create a gist from a link
2. **Atomic Operation**: Ensures that the link and gist are created together, reducing the risk of inconsistent data
3. **Automatic Notification**: The CrewAI service is automatically notified about the new gist
4. **Flexible Control**: Services can choose whether to create a gist automatically or handle it separately