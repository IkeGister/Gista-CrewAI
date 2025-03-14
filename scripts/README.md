# Scripts Directory

This directory contains utility scripts for development, testing, deployment, and maintenance of the Gista-CrewAI API.

## Directory Structure

- `auth/`: Authentication-related scripts
- `deployment/`: Deployment scripts
- `development/`: Development server and tools
- `maintenance/`: Maintenance scripts
- `security/`: Security checking tools

## Authentication Scripts (`auth/`)

- **generate_token.py**: Generates Firebase custom tokens for testing and authentication
  - Usage: `python scripts/auth/generate_token.py`
  
- **sign_in_with_custom_token.py**: Exchanges custom tokens for Firebase ID tokens
  - Usage: `python scripts/auth/sign_in_with_custom_token.py`

## Deployment Scripts (`deployment/`)

- **prepare_for_deployment.sh**: Prepares the codebase for secure deployment
  - Usage: `bash scripts/deployment/prepare_for_deployment.sh`
  - Creates a sanitized deployment package without sensitive information
  - Generates example configuration templates

## Development Scripts (`development/`)

- **run_dev_server.py**: Runs the Flask development server
  - Usage: `python scripts/development/run_dev_server.py`
  - Alternative: Use the helper script `./run_server.sh` in the root directory

## Maintenance Scripts (`maintenance/`)

- **cleanup.sh**: Cleans up temporary files, caches, and build artifacts
  - Usage: `bash scripts/maintenance/cleanup.sh`
  - Removes Python cache files, build directories, and temporary files

## Security Scripts (`security/`)

- **check_security.py**: Scans the codebase for potential security issues
  - Usage: `python scripts/security/check_security.py`
  - Detects API keys, credentials, and other sensitive information that shouldn't be committed

## Migration Scripts

- **migrate_to_subcollections.sh**: Migrates the database from flat structure to subcollections
  - Usage: `bash scripts/migrate_to_subcollections.sh`

- **migrate_to_subcollections_gista.sh**: Gista-specific migration script
  - Usage: `bash scripts/migrate_to_subcollections_gista.sh`

## Testing Scripts

- **run_all_tests.sh**: Runs all tests in the test suite
  - Usage: `bash scripts/run_all_tests.sh`

- **run_tests_with_server.sh**: Runs tests that require the development server
  - Usage: `bash scripts/run_tests_with_server.sh`

- **test_gist_status_update.py**: Tests the gist status update functionality
  - Usage: `python scripts/test_gist_status_update.py`

- **test_status_update_flow.py**: Tests the complete status update flow
  - Usage: `python scripts/test_status_update_flow.py`

- **test_user_gists.py**: Tests user gist retrieval functionality
  - Usage: `python scripts/test_user_gists.py`

- **test-api.sh**: Performs API tests using curl commands
  - Usage: `bash scripts/test-api.sh`

## Usage

Make sure the scripts are executable:

```bash
chmod +x scripts/*.sh
```

Then run the scripts from the project root directory:

```bash
# To prepare for deployment
./scripts/deployment/prepare_for_deployment.sh

# To run all tests
./scripts/run_all_tests.sh

# To run tests with server
./scripts/run_tests_with_server.sh 