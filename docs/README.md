# Gista-CrewAI API Documentation

This directory contains comprehensive documentation for the Gista-CrewAI API, including deployment guides, testing procedures, and API specifications.

## Documentation Structure

### API Documentation
- [API Documentation](api/API-Documentation.md) - Detailed documentation of the API endpoints and their usage
- [Service Integration](api/SERVICE_INTEGRATION.md) - Documentation for integrating with other services
- [Service Clients](api/SERVICE_CLIENTS.md) - Documentation for the service client modules

### Deployment Documentation
- [Deployment Guide](deployment/DEPLOYMENT.md) - Step-by-step guide for deploying the API
- [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md) - Checklist to ensure all deployment steps are completed

### Testing Documentation
- [API Testing Guide](testing/API_TESTING.md) - Guide for testing the API endpoints
- [Test Refactoring Execution Summary](testing/TestRefactoringExecutionSummary.md) - Summary of the test refactoring process
- [Test Refactoring Plan](testing/TestRefactoringPlan.md) - Plan for refactoring the tests

### Development Documentation
- [Development Session](development/DevSession.md) - Notes from development sessions
- [Debug Information](development/debug/) - Debug-related documentation and notes

### Security Documentation
- [Security Guidelines](security/SECURITY.md) - Security best practices for the Gista-CrewAI API
- [Security Check Script](security/check_security.py) - Script for checking security issues in the codebase

## Scripts

The project includes several utility scripts located in the `scripts/` directory:

- `prepare_for_deployment.sh` - Script for preparing the codebase for deployment
- `run_all_tests.sh` - Script for running all tests
- `run_tests_with_server.sh` - Script for running tests that require the server

## Getting Started

For new developers, we recommend starting with the [API Documentation](api/API-Documentation.md) to understand the API structure, followed by the [API Testing Guide](testing/API_TESTING.md) to learn how to test the API.

For deployment, follow the [Deployment Guide](deployment/DEPLOYMENT.md) and use the [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md) to ensure all steps are completed. 