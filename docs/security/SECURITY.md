# Gista-CrewAI API Security Guidelines

This document outlines security best practices for the Gista-CrewAI API.

## Security Considerations

### API Keys and Credentials

- **Never commit API keys or credentials to version control**
- Store sensitive information in environment variables or secure secret management systems
- Use the `.env` file for local development, but ensure it is in `.gitignore`
- For production, use Firebase Functions environment configuration:
  ```bash
  firebase functions:config:set openai.key="your-key" anthropic.key="your-key"
  ```

### Firebase Service Account

- The Firebase service account JSON file contains sensitive credentials
- Never commit this file to version control
- Store it securely and restrict access to authorized personnel only
- For local development, you can:
  - Place the file at `functions/src/service-account.json` (ensure it's in `.gitignore`)
  - Set the `FIREBASE_SERVICE_ACCOUNT` environment variable to the path of your service account file

### Authentication

- All API endpoints should require authentication
- Use Firebase Authentication for user authentication
- Use API keys for service-to-service authentication
- Implement rate limiting to prevent abuse

### Data Security

- Validate all input data
- Sanitize data before storing or processing
- Implement proper error handling to avoid exposing sensitive information
- Use HTTPS for all API endpoints

## Security Checks

The `check_security.py` script in this directory can be used to scan the codebase for potential security issues:

```bash
python docs/security/check_security.py
```

This script will scan for:
- API keys
- Firebase credentials
- Private keys
- Passwords
- Bearer tokens
- Authorization headers
- IP addresses

## Deployment Security

Before deploying to production, ensure:

1. All sensitive information is removed from the codebase
2. Environment variables are properly configured in the production environment
3. Firebase security rules are properly configured
4. API endpoints are properly secured

See the [Deployment Checklist](../deployment/DEPLOYMENT_CHECKLIST.md) for a complete list of security-related deployment steps.

## Security Best Practices

1. **Regularly rotate API keys**
   - Set a schedule to rotate all API keys
   - Update environment variables after rotation

2. **Audit access**
   - Regularly review who has access to the Firebase project
   - Limit access to production environment variables

3. **Monitor for unusual activity**
   - Set up alerts for unusual API usage patterns
   - Monitor for unauthorized access attempts

4. **Keep dependencies updated**
   - Regularly update dependencies to patch security vulnerabilities
   - Use tools like `npm audit` or `pip-audit` to check for vulnerabilities 