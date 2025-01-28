# Gista API Documentation

## Base URL 

## Authentication
All endpoints require Firebase Authentication. Include the ID token in the Authorization header: 

## Endpoints

### Links API

#### 1. Store Link
Stores a new link in the user's collection.

**Endpoint:** `POST /links/store`

**Request Body:** 

{
"user_id": "string",
"link": {
"category": "string",
"title": "string",
"url": "string"
}
}

**Response:**
```json
{
  "message": "Link stored successfully",
  "link": {
    "category": "string",
    "date_added": "timestamp",
    "gist_created": {
      "gist_created": false,
      "gist_id": null,
      "image_url": null,
      "link_id": "string",
      "link_title": "string",
      "link_type": "Web|PDF",
      "url": "string"
    }
  }
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request body
- `500`: Server error

#### 2. Update Link Gist Status
Updates a link's gist status when a gist is created from it.

**Endpoint:** `PUT /links/update-gist-status/:user_id/:link_id`

**URL Parameters:**
- `user_id`: User's unique identifier
- `link_id`: Link's unique identifier

**Request Body:**
```json
{
  "gist_id": "string",
  "image_url": "string",
  "link_title": "string"
}
```

**Response:**
```json
{
  "message": "Link gist status updated successfully",
  "link": {
    "category": "string",
    "date_added": "timestamp",
    "gist_created": {
      "gist_created": true,
      "gist_id": "string",
      "image_url": "string",
      "link_id": "string",
      "link_title": "string",
      "link_type": "Web|PDF",
      "url": "string"
    }
  }
}
```

#### 3. Get User's Links
Retrieves all links for a specific user.

**Endpoint:** `GET /links/:user_id`

**Response:**
```json
{
  "links": [
    {
      "category": "string",
      "date_added": "timestamp",
      "gist_created": {
        "gist_created": "boolean",
        "gist_id": "string",
        "image_url": "string",
        "link_id": "string",
        "link_title": "string",
        "link_type": "Web|PDF",
        "url": "string"
      }
    }
  ],
  "count": "number"
}
```

### Gists API

#### 1. Create Gist
Creates a new gist from a link.

**Endpoint:** `POST /gists/add/:user_id`

**Request Body:**
```json
{
  "title": "string",
  "link": "string",
  "image_url": "string",
  "category": "string",
  "segments": [
    {
      "audioUrl": "string",
      "duration": "number",
      "title": "string"
    }
  ],
  "playback_duration": "number",
  "publisher": "string",
  "ratings": "number",
  "users": "number"
}
```

**Response:**
```json
{
  "message": "Gist added successfully",
  "gist": {
    "title": "string",
    "category": "string",
    "date_created": "timestamp",
    "image_url": "string",
    "is_played": false,
    "is_published": true,
    "link": "string",
    "playback_duration": "number",
    "publisher": "string",
    "ratings": "number",
    "segments": [
      {
        "segment_audioUrl": "string",
        "segment_duration": "number",
        "segment_index": "number",
        "segment_title": "string"
      }
    ],
    "status": {
      "is_done_playing": false,
      "is_now_playing": false,
      "playback_time": 0
    },
    "users": "number"
  }
}
```

#### 2. Update Gist Status
Updates a gist's playback status.

**Endpoint:** `PUT /gists/update/:user_id/:gist_id`

**Request Body:**
```json
{
  "is_done_playing": "boolean",
  "is_now_playing": "boolean",
  "playback_time": "number",
  "is_played": "boolean",
  "ratings": "number",
  "users": "number"
}
```

**Response:**
```json
{
  "message": "Gist updated successfully"
}
```

#### 3. Get User's Gists
Retrieves all gists for a specific user.

**Endpoint:** `GET /gists/:user_id`

**Response:**
```json
{
  "gists": [
    {
      // Full gist object as described in Create Gist response
    }
  ]
}
```

## Error Responses
All endpoints may return these error responses:

```json
{
  "error": "Error message description"
}
```

**Common Status Codes:**
- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Invalid or missing token
- `404`: Not Found - Resource doesn't exist
- `500`: Server Error - Internal processing error