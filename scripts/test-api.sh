#!/bin/bash

# Test script for the CrewAI Backend API
# This script runs the test_crewai-backend_endpoints.py script and saves the results

# Create test results directory if it doesn't exist
mkdir -p ./test-results

echo "Starting CrewAI Backend API tests..."
echo

# Run the test_crewai-backend_endpoints.py script
python3 functions/test_crewai-backend_endpoints.py --verbose

# Check if the test was successful
if [ $? -eq 0 ]; then
    echo "Saving sample responses for documentation..."
    # Copy the test results to a documentation directory
    cp -r ./test-results ./docs/api-samples 2>/dev/null || echo "Could not copy to docs directory"
    echo "Sample responses saved to ./test-results directory"
else
    echo "Tests failed. Check the output for errors."
    exit 1
fi 