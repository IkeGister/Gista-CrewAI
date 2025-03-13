# Gista-CrewAI API Scripts

This directory contains utility scripts for the Gista-CrewAI API.

## Available Scripts

### Deployment Scripts

- `prepare_for_deployment.sh` - Prepares the codebase for deployment by:
  - Creating a clean deployment package
  - Removing sensitive files
  - Creating example templates for configuration files
  - Adding deployment documentation

### Testing Scripts

- `run_all_tests.sh` - Runs all tests for the API, including:
  - Firebase configuration tests
  - API tests
  - Live API tests
  - Auto-create gist tests
  
  Note: This script will prompt you to start the server before running tests that require it.

- `run_tests_with_server.sh` - Automatically starts the server, runs all tests, and stops the server.

## Usage

Make sure the scripts are executable:

```bash
chmod +x scripts/*.sh
```

Then run the scripts from the project root directory:

```bash
# To prepare for deployment
./scripts/prepare_for_deployment.sh

# To run all tests
./scripts/run_all_tests.sh

# To run tests with server
./scripts/run_tests_with_server.sh 