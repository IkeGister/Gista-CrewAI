#!/usr/bin/env python3
"""
Test script for the CrewAI Backend API.
This script tests all the API endpoints and saves the responses to JSON files.
"""

import json
import os
import requests
import argparse
import sys

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test the CrewAI Backend API.')
    parser.add_argument('--base-url', default='http://localhost:3000',
                        help='Base URL for the API (default: http://localhost:3000)')
    parser.add_argument('--api-key', default='AIzaSyBpyUfx_HjOdkkaVO2HnOyIPtVDHb7XI6Q',
                        help='API key for authentication')
    parser.add_argument('--user-id', default='test_user_1741057003',
                        help='User ID for testing')
    parser.add_argument('--gist-id', default='gist_1741057003',
                        help='Gist ID for testing')
    parser.add_argument('--save-dir', default='./test-results',
                        help='Directory to save test results')
    parser.add_argument('--verbose', action='store_true',
                        help='Print verbose output')
    return parser.parse_args()

def make_request(method, endpoint, headers=None, data=None, args=None):
    """Make an API request and return the response."""
    if headers is None:
        headers = {}
    
    url = f"{args.base_url}{endpoint}"
    print(f"{Colors.YELLOW}Testing: {method} {endpoint}{Colors.RESET}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            print(f"{Colors.RED}Error: Invalid method {method}{Colors.RESET}")
            return None
        
        # Check if response is valid JSON
        try:
            json_response = response.json()
            print(f"{Colors.GREEN}Success: {response.status_code}{Colors.RESET}")
            if args.verbose:
                print(json.dumps(json_response, indent=2))
            return json_response
        except json.JSONDecodeError:
            print(f"{Colors.RED}Error: Invalid JSON response{Colors.RESET}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        return None

def save_response(response, filename, args):
    """Save the response to a JSON file."""
    if response is None:
        return
    
    os.makedirs(args.save_dir, exist_ok=True)
    filepath = os.path.join(args.save_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(response, f, indent=2)
    
    print(f"{Colors.GREEN}Response saved to {filepath}{Colors.RESET}")

def test_health(args):
    """Test the health endpoint."""
    headers = {'X-API-Key': args.api_key}
    response = make_request('GET', '/api/health', headers=headers, args=args)
    save_response(response, 'health.json', args)
    return response

def test_get_gists(args):
    """Test the get gists endpoint."""
    headers = {'X-API-Key': args.api_key}
    response = make_request('GET', f'/api/gists/{args.user_id}', headers=headers, args=args)
    save_response(response, 'gists.json', args)
    return response

def test_get_gist(args):
    """Test the get specific gist endpoint."""
    headers = {'X-API-Key': args.api_key}
    response = make_request('GET', f'/api/gists/{args.user_id}/{args.gist_id}', headers=headers, args=args)
    save_response(response, 'gist.json', args)
    return response

def test_update_gist_status(args):
    """Test the update gist status endpoint using the signal-based approach."""
    headers = {'X-API-Key': args.api_key, 'Content-Type': 'application/json'}
    
    # Signal-based approach - empty JSON object
    data = {}
    
    # The correct endpoint format based on the CrewAI service implementation
    endpoint = f'/api/gists/{args.user_id}/{args.gist_id}/status'
    
    response = make_request('PUT', endpoint, headers=headers, data=data, args=args)
    save_response(response, 'update_status.json', args)
    return response

def test_batch_update_status(args):
    """Test the batch update status endpoint."""
    headers = {'X-API-Key': args.api_key, 'Content-Type': 'application/json'}
    data = {'gistIds': [args.gist_id], 'inProduction': True, 'production_status': 'review'}
    response = make_request('PUT', f'/api/gists/{args.user_id}/batch/status', headers=headers, data=data, args=args)
    save_response(response, 'batch_update.json', args)
    return response

def test_update_with_links(args):
    """Test the update gist with links endpoint."""
    headers = {'X-API-Key': args.api_key, 'Content-Type': 'application/json'}
    data = {'links': ['link1', 'link2'], 'inProduction': True, 'production_status': 'review'}
    response = make_request('PUT', f'/api/gists/{args.user_id}/{args.gist_id}/with-links', headers=headers, data=data, args=args)
    save_response(response, 'update_with_links.json', args)
    return response

def test_get_links(args):
    """Test the get links endpoint."""
    headers = {'X-API-Key': args.api_key}
    response = make_request('GET', f'/api/links/{args.user_id}', headers=headers, args=args)
    save_response(response, 'links.json', args)
    return response

def test_error_cases(args):
    """Test error cases."""
    # Test invalid API key
    headers = {'X-API-Key': 'invalid_key'}
    response = make_request('GET', '/api/health', headers=headers, args=args)
    save_response(response, 'invalid_api_key.json', args)
    
    # Test non-existent user
    headers = {'X-API-Key': args.api_key}
    response = make_request('GET', '/api/gists/non_existent_user', headers=headers, args=args)
    save_response(response, 'non_existent_user.json', args)
    
    # Test non-existent gist
    response = make_request('GET', f'/api/gists/{args.user_id}/non_existent_gist', headers=headers, args=args)
    save_response(response, 'non_existent_gist.json', args)
    
    # Test invalid JSON payload
    headers = {'X-API-Key': args.api_key, 'Content-Type': 'application/json'}
    try:
        response = requests.put(f"{args.base_url}/api/gists/{args.user_id}/{args.gist_id}/status", 
                               headers=headers, data="invalid_json")
        print(f"{Colors.YELLOW}Testing: Invalid JSON payload{Colors.RESET}")
        print(f"{Colors.RED}Expected error:{Colors.RESET}")
        try:
            json_response = response.json()
            print(json.dumps(json_response, indent=2))
            save_response(json_response, 'invalid_json.json', args)
        except json.JSONDecodeError:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")

def main():
    """Main function."""
    args = parse_args()
    
    # Check if requests module is available
    try:
        import requests
    except ImportError:
        print(f"{Colors.RED}Error: The requests module is required. Please install it with 'pip install requests'.{Colors.RESET}")
        sys.exit(1)
    
    # Check if server is running
    try:
        requests.get(f"{args.base_url}/api/health", timeout=5)
    except requests.exceptions.RequestException:
        print(f"{Colors.RED}Error: Server is not running. Please start the server with 'NODE_ENV=development npx ts-node src/index.ts'{Colors.RESET}")
        return
    
    print(f"{Colors.GREEN}Starting API tests...{Colors.RESET}")
    print()
    
    # Test all endpoints
    test_health(args)
    print()
    
    test_get_gists(args)
    print()
    
    test_get_gist(args)
    print()
    
    test_get_links(args)
    print()
    
    test_update_gist_status(args)
    print()
    
    test_batch_update_status(args)
    print()
    
    test_update_with_links(args)
    print()
    
    # Test error cases
    print(f"{Colors.YELLOW}Testing error cases:{Colors.RESET}")
    print()
    test_error_cases(args)
    
    print()
    print(f"{Colors.GREEN}API tests completed!{Colors.RESET}")

if __name__ == '__main__':
    main() 