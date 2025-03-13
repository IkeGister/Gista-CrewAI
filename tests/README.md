# Gista-CrewAI API Tests

This directory contains all tests for the Gista-CrewAI API, organized into the following categories:

## Test Structure

- **Unit Tests** (`tests/unit/`): Tests for individual components without external dependencies
  - `test_firebase.py`: Tests for Firebase configuration and core functionality
  - `test_apis.py`: Tests for API endpoints using mocked dependencies

- **Integration Tests** (`tests/integration/`): Tests that verify the interaction between components
  - `test_api_live.py`: Tests for live API endpoints with real HTTP requests
  - `test_auto_create_gist.py`: Tests for the auto-create gist functionality

- **End-to-End Tests** (`tests/e2e/`): Tests that verify the entire system
  - `test_crewai-backend_endpoints.py`: Tests for the backend endpoints in a production-like environment

## Running Tests

### Using the Test Runner with Server

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

# Specify a custom port for the server
python tests/run_tests_with_server.py --port 5002
```

### Using the Test Runner

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

# Run tests without prompting for server confirmation
python tests/run_all_tests.py --no-prompt
```

### Running Tests Individually

You can also run tests individually:

#### Unit Tests

```bash
# Run Firebase config tests
python -m unittest tests.unit.test_firebase

# Run API tests
python -m unittest tests.unit.test_apis
```

#### Integration Tests

```bash
# Run live API tests
python tests/integration/test_api_live.py

# Run auto-create gist tests
python tests/integration/test_auto_create_gist.py
```

#### End-to-End Tests

```bash
# Run backend endpoint tests
python tests/e2e/test_crewai-backend_endpoints.py
```

## Server Requirements

Some tests require the Flask development server to be running. You can start the server with:

```bash
python run_dev_server.py
```

The test runner will prompt you to confirm that the server is running before executing tests that require it, or you can use the `run_tests_with_server.py` script to automatically start and stop the server. 