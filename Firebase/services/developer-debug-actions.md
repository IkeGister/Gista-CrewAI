# Developer Debug Actions

## Updated Action Plan for CrewAI Service Integration

Based on the response from the CrewAI service team, they've implemented a significant improvement to the gist status update endpoint. The API now uses a **signal-based approach** that eliminates the need for specific payload data. Here's our updated action plan to integrate with this improved API:

### Step 1: Update the `update_gist_status` Method
We'll update the `update_gist_status` method in `crew_ai_service.py` to use the new signal-based approach:

```python
def update_gist_status(self, user_id: str, gist_id: str, 
                      in_production: bool = None, production_status: str = None) -> Dict:
    """
    Update the status of a gist using the signal-based API.
    
    Args:
        user_id: The user ID
        gist_id: The gist ID to update
        in_production: Ignored (kept for backward compatibility)
        production_status: Ignored (kept for backward compatibility)
            
    Returns:
        Dictionary containing the updated gist data or error information
    """
    logger.info(f"Updating status for gist {gist_id} of user {user_id}")
    
    # Signal-based approach - empty JSON object
    data = {}
    
    try:
        return self._make_request('PUT', f'/api/gists/{user_id}/{gist_id}/status', data=data)
    except Exception as e:
        logger.error(f"Error updating gist status: {str(e)}")
        # Return a standardized error response
        return {
            "success": False,
            "error": "Failed to update gist status",
            "message": str(e)
        }
```

### Step 2: Update the `notify_crew_ai` Function
We'll update the `notify_crew_ai` function in `links.py` to use the new signal-based approach:

```python
@links_bp.route('/api/gists/notify-crew-ai/<user_id>/<gist_id>', methods=['POST'])
def notify_crew_ai(user_id, gist_id):
    """
    Notify the CrewAI service about a gist update using the signal-based API.
    
    This endpoint is specifically for notifying the CrewAI service about gist updates.
    It will fail if the CrewAI service is unavailable, unlike the add_gist endpoint
    which continues even if notification fails.
    
    Args:
        user_id: The user ID
        gist_id: The gist ID
        
    Returns:
        A JSON response with the result
    """
    try:
        # First, check if the gist exists
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404
            
        user_data = doc.to_dict()
        gist_exists = False
        
        if 'gists' in user_data:
            for gist in user_data['gists']:
                if gist.get('gistId') == gist_id:
                    gist_exists = True
                    break
                    
        if not gist_exists:
            return jsonify({"error": "Gist not found"}), 404
        
        # Import here to avoid circular imports
        from Firebase.services import CrewAIService
        
        # Initialize the CrewAI service client
        crew_ai_service = CrewAIService()
        
        # Call the CrewAI service to update the gist status using signal-based approach
        status_response = crew_ai_service.update_gist_status(user_id, gist_id)
        
        # Check if the response indicates success
        if status_response.get('success') is False:
            raise Exception(status_response.get('message', 'Unknown error'))
        
        logger.info(f"CrewAI service notified about gist update: {status_response}")
        
        return jsonify({
            "message": "CrewAI service notified successfully", 
            "response": status_response
        }), 200
        
    except Exception as e:
        logger.error(f"Error notifying CrewAI service: {str(e)}")
        return jsonify({
            "error": f"Service unavailable: {str(e)}"
        }), 503  # Service Unavailable
```

### Step 3: Update the Batch Update Method
We'll also update the `batch_update_gists` method in `crew_ai_service.py` to match the API documentation:

```python
def batch_update_gists(self, user_id: str, gist_ids: List[str],
                      in_production: bool = True, production_status: str = "review") -> Dict:
    """
    Update the status of multiple gists.
    
    Args:
        user_id: The user ID
        gist_ids: List of gist IDs to update
        in_production: Whether the gists are in production
        production_status: Current production status (must be one of: draft, review, published)
            
    Returns:
        Dictionary containing the updated gists data
    """
    logger.info(f"Batch updating {len(gist_ids)} gists for user {user_id}")
    
    # Ensure production_status is one of the valid values
    valid_statuses = ['draft', 'review', 'published']
    if production_status not in valid_statuses:
        production_status = 'review'  # Default to 'review' if invalid
    
    data = {
        "gistIds": gist_ids,
        "inProduction": in_production,
        "production_status": production_status
    }
    
    try:
        return self._make_request('PUT', f'/api/gists/{user_id}/batch/status', data=data)
    except Exception as e:
        logger.error(f"Error batch updating gist status: {str(e)}")
        return {
            "success": False,
            "error": "Failed to update gist status",
            "message": str(e)
        }
```

### Step 4: Update the Links Update Method
We'll update the `update_gist_with_links` method in `crew_ai_service.py` to match the API documentation:

```python
def update_gist_with_links(self, user_id: str, gist_id: str, links: List[Dict],
                          in_production: bool = True, production_status: str = "review") -> Dict:
    """
    Update a gist with links and status.
    
    Args:
        user_id: The user ID
        gist_id: The gist ID to update
        links: List of link objects to add to the gist
        in_production: Whether the gist is in production
        production_status: Current production status (must be one of: draft, review, published)
            
    Returns:
        Dictionary containing the updated gist data
    """
    logger.info(f"Updating gist {gist_id} with {len(links)} links for user {user_id}")
    
    # Ensure production_status is one of the valid values
    valid_statuses = ['draft', 'review', 'published']
    if production_status not in valid_statuses:
        production_status = 'review'  # Default to 'review' if invalid
    
    data = {
        "links": links,
        "inProduction": in_production,
        "production_status": production_status
    }
    
    try:
        return self._make_request('PUT', f'/api/gists/{user_id}/{gist_id}/with-links', data=data)
    except Exception as e:
        logger.error(f"Error updating gist with links: {str(e)}")
        return {
            "success": False,
            "error": "Failed to update gist with links",
            "message": str(e)
        }
```

### Step 5: Update the Test Script
We'll update the direct test script to use the signal-based approach:

```python
def test_update_gist_status(args):
    """Test the update gist status endpoint using the signal-based API."""
    headers = {'X-API-Key': args.api_key, 'Content-Type': 'application/json'}
    
    # Signal-based approach - empty JSON object
    data = {}
    
    response = make_request('PUT', f'/api/gists/{args.user_id}/{args.gist_id}/status', headers=headers, data=data, args=args)
    save_response(response, 'update_status.json', args)
    return response
```

### Step 6: Update the Test Case
We'll update the `test_crew_ai_notification` method in `testAPIs.py` to use the signal-based approach:

```python
# Now test the CrewAI notification endpoint
notification_data = {}  # Signal-based approach - empty JSON object

# Attempt to notify CrewAI service
notify_response = self.client.post(
    f'/api/gists/notify-crew-ai/{self.test_user_id}/{gist_id}',
    json=notification_data,
    headers=self.headers
)
```

### Step 7: Implement Asynchronous Processing (Optional)
For production systems, we may want to implement the asynchronous processing approach suggested by the service team:

```python
class GistStatusUpdater:
    def __init__(self, api_key, base_url="https://api-yufqiolzaa-uc.a.run.app"):
        self.api_key = api_key
        self.base_url = base_url
        self.queue = []
        self.is_processing = False
        
    async def queue_update(self, user_id, gist_id):
        """Queue a gist status update for processing"""
        self.queue.append({
            "user_id": user_id,
            "gist_id": gist_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Start processing if not already running
        if not self.is_processing:
            asyncio.create_task(self.process_queue())
    
    async def process_queue(self):
        """Process the queue of gist status updates"""
        self.is_processing = True
        
        while self.queue:
            item = self.queue[0]
            success = await self.update_gist_status(item["user_id"], item["gist_id"])
            
            if success:
                # Remove from queue if successful
                self.queue.pop(0)
            else:
                # Move to end of queue for retry if failed
                self.queue.pop(0)
                # Add back with delay for exponential backoff
                if len(self.queue) < 100:  # Prevent queue from growing too large
                    self.queue.append(item)
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        self.is_processing = False
    
    async def update_gist_status(self, user_id, gist_id):
        """Update a gist's status using the signal-based API"""
        url = f"{self.base_url}/api/gists/{user_id}/{gist_id}/status"
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json={}) as response:
                    if response.status in (200, 201, 204):
                        return True
                    else:
                        logger.error(f"Error updating gist status: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Exception updating gist status: {e}")
            return False
```

### Step 8: Update Documentation
We'll update our documentation to reflect the new signal-based approach:

```python
"""
Note: The CrewAI service endpoint for updating gist status now uses a signal-based approach.
This means that no request body is required - simply making the PUT request to the endpoint
triggers the status update. The server handles setting `inProduction: true` and 
`production_status: "Reviewing Content"` internally.

Example usage:
```python
crew_ai_service = CrewAIService()
response = crew_ai_service.update_gist_status(
    user_id="user123",
    gist_id="gist456"
)
```
"""
```

This action plan addresses all the key changes in the CrewAI service API and should resolve the 500 Internal Server Error issue by using the new signal-based approach.
