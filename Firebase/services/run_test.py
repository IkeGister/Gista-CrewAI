#!/usr/bin/env python
"""
Run script for testing the CrewAI service client.
This script sets environment variables directly and then runs the test script.
"""

import os
import sys
import subprocess
from env_utils import find_and_load_env_file, check_required_vars

# Load environment variables from .env file
env_path = find_and_load_env_file()

# Check if required variables are set
required_vars = ['CREW_AI_API_BASE_URL', 'SERVICE_API_KEY']
var_status = check_required_vars(required_vars)

# Set default values for missing variables
if not var_status.get('CREW_AI_API_BASE_URL', False):
    default_url = "https://api-yufqiolzaa-uc.a.run.app/api"
    print(f"\nSetting CREW_AI_API_BASE_URL to default: {default_url}")
    os.environ['CREW_AI_API_BASE_URL'] = default_url

if not var_status.get('SERVICE_API_KEY', False):
    print("\n*** SERVICE_API_KEY not found in .env file. ***")
    print("This key is required for authentication with the CrewAI service.")
    print("Please enter your SERVICE_API_KEY below:")
    service_api_key = input("SERVICE_API_KEY: ").strip()
    if service_api_key:
        os.environ['SERVICE_API_KEY'] = service_api_key
    else:
        print("No SERVICE_API_KEY provided. Tests will fail without this key.")
        sys.exit(1)

# Set other optional environment variables with defaults
if not os.environ.get('API_MAX_RETRIES'):
    os.environ['API_MAX_RETRIES'] = '3'
    print(f"Setting API_MAX_RETRIES to default: {os.environ['API_MAX_RETRIES']}")

if not os.environ.get('API_RETRY_DELAY'):
    os.environ['API_RETRY_DELAY'] = '1'
    print(f"Setting API_RETRY_DELAY to default: {os.environ['API_RETRY_DELAY']}")

# Print environment status
print("\nEnvironment variables set for testing:")
check_required_vars(['CREW_AI_API_BASE_URL', 'SERVICE_API_KEY', 'API_MAX_RETRIES', 'API_RETRY_DELAY'])

print("\nRunning test_crew_ai_service.py...")
# Run the test script and exit with its return code
try:
    result = subprocess.run([sys.executable, "test_crew_ai_service.py"])
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error running test script: {e}")
    sys.exit(1) 