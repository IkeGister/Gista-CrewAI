# Gista-CrewAI API Deployment Guide

This guide outlines the steps to deploy the Gista-CrewAI API with the enhanced auto-create gist functionality.

## Pre-Deployment Security Checklist

Before deploying, complete these critical security steps:

1. **Secure Sensitive Information**
   - Remove any hardcoded API keys from the codebase
   - Ensure `.env` and `service-account.json` files are in `.gitignore`
   - Verify no credentials are committed to the repository

2. **Environment Variables**
   - Set up environment variables in your production environment
   - For cloud deployments (GCP, AWS, Azure), use their secrets management services
   - For Firebase Functions, use the Firebase CLI to set environment variables:
     ```bash
     firebase functions:config:set openai.key="your-key" anthropic.key="your-key" firebase.projectid="your-project-id"
     ```

## Deployment Steps

### 1. Prepare the Deployment Package

```bash
# Create a clean deployment package
git clone https://github.com/your-repo/Gista-CrewAI-v2.git deployment-package
cd deployment-package

# Remove any sensitive files before pushing
rm -f .env service-account.json
```

### 2. Deploy to Firebase Functions

```bash
# Install Firebase CLI if not already installed
npm install -g firebase-tools

# Login to Firebase
firebase login

# Select your project
firebase use dof-ai

# Deploy the functions
firebase deploy --only functions
```

### 3. Update Environment Variables

```bash
# Set environment variables for Firebase Functions
firebase functions:config:set \
  openai.apikey="YOUR_OPENAI_API_KEY" \
  anthropic.apikey="YOUR_ANTHROPIC_API_KEY" \
  firebase.projectid="dof-ai" \
  crewai.apiurl="https://api-yufqiolzaa-uc.a.run.app/api" \
  crewai.apikey="YOUR_SERVICE_API_KEY"
```

### 4. Verify Deployment

1. Test the deployed API using the test scripts:
   ```bash
   # Update the API_BASE_URL in your test environment to point to the deployed API
   export API_BASE_URL=https://us-central1-dof-ai.cloudfunctions.net/api
   
   # Run the tests against the deployed API
   python test_api_live.py
   python test_auto_create_gist.py
   ```

2. Manually test the key endpoints:
   - `/api/users/create`
   - `/api/links/store` with `auto_create_gist=true`
   - `/api/links/store` with `auto_create_gist=false`
   - `/api/gists/{userId}`

## Post-Deployment Monitoring

1. **Monitor Firebase Logs**
   ```bash
   firebase functions:log
   ```

2. **Set Up Error Alerting**
   - Configure Firebase Alerts for function errors
   - Set up monitoring for critical API endpoints

3. **Performance Monitoring**
   - Monitor function execution times
   - Track API response times
   - Set up alerts for performance degradation

## Rollback Procedure

If issues are detected after deployment:

1. **Immediate Rollback**
   ```bash
   # Deploy the previous version
   firebase deploy --only functions:api --function-source=./previous-version
   ```

2. **Investigate Issues**
   - Check logs for error messages
   - Verify environment variables are correctly set
   - Test the API in a staging environment

## Security Best Practices

1. **Regularly Rotate API Keys**
   - Set a schedule to rotate all API keys
   - Update environment variables after rotation

2. **Audit Access**
   - Regularly review who has access to the Firebase project
   - Limit access to production environment variables

3. **Monitor for Unusual Activity**
   - Set up alerts for unusual API usage patterns
   - Monitor for unauthorized access attempts 