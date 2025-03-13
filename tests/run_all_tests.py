#!/usr/bin/env python3
"""
Test Runner for Gista-CrewAI API

This script runs all tests for the Gista-CrewAI API, including unit tests,
integration tests, and end-to-end tests.
"""

import os
import sys
import unittest
import subprocess
import argparse

def run_unit_tests():
    """Run all unit tests"""
    print("\n===== Running Unit Tests =====")
    
    # Run Firebase config tests
    print("\nRunning Firebase config tests...")
    unittest.main(module='tests.unit.test_firebase', argv=['first-arg-is-ignored'], exit=False)
    
    # Run API tests
    print("\nRunning API tests...")
    unittest.main(module='tests.unit.test_apis', argv=['first-arg-is-ignored'], exit=False)
    
    print("\nUnit tests completed.")

def run_integration_tests(server_required=True):
    """Run all integration tests"""
    print("\n===== Running Integration Tests =====")
    
    if server_required:
        print("\nWARNING: These tests require the Flask development server to be running.")
        response = input("Is the server running? (y/n): ")
        if response.lower() != 'y':
            print("Please start the server with 'python run_dev_server.py' and try again.")
            return
    
    # Run live API tests
    print("\nRunning live API tests...")
    result = subprocess.run([sys.executable, "tests/integration/test_api_live.py"])
    if result.returncode != 0:
        print("Live API tests failed.")
        return
    
    # Run auto-create gist tests
    print("\nRunning auto-create gist tests...")
    result = subprocess.run([sys.executable, "tests/integration/test_auto_create_gist.py"])
    if result.returncode != 0:
        print("Auto-create gist tests failed.")
        return
    
    print("\nIntegration tests completed.")

def run_e2e_tests(server_required=True):
    """Run all end-to-end tests"""
    print("\n===== Running End-to-End Tests =====")
    
    if server_required:
        print("\nWARNING: These tests require the Flask development server to be running.")
        response = input("Is the server running? (y/n): ")
        if response.lower() != 'y':
            print("Please start the server with 'python run_dev_server.py' and try again.")
            return
    
    # Run backend endpoint tests
    print("\nRunning backend endpoint tests...")
    result = subprocess.run([sys.executable, "tests/e2e/test_crewai-backend_endpoints.py"])
    if result.returncode != 0:
        print("Backend endpoint tests failed.")
        return
    
    print("\nEnd-to-end tests completed.")

def main():
    """Main function to run tests"""
    parser = argparse.ArgumentParser(description='Run tests for Gista-CrewAI API')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--no-prompt', action='store_true', help='Do not prompt for server confirmation')
    
    args = parser.parse_args()
    
    # If no arguments are provided, run all tests
    if not (args.unit or args.integration or args.e2e or args.all):
        args.all = True
    
    # Run tests based on arguments
    if args.unit or args.all:
        run_unit_tests()
    
    if args.integration or args.all:
        run_integration_tests(not args.no_prompt)
    
    if args.e2e or args.all:
        run_e2e_tests(not args.no_prompt)
    
    print("\n===== All Tests Completed =====")

if __name__ == "__main__":
    # Add the current directory to the path so that imports work
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main() 