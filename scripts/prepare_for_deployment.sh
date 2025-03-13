#!/bin/bash

# Script to prepare the Gista-CrewAI API for secure deployment
# This script will:
# 1. Create backup copies of sensitive files
# 2. Create example templates without actual credentials
# 3. Remove sensitive files from the deployment package

echo "===== Preparing Gista-CrewAI API for Secure Deployment ====="

# Create a deployment directory
DEPLOY_DIR="deployment-package"
echo "Creating deployment directory: $DEPLOY_DIR"
mkdir -p $DEPLOY_DIR

# Copy all files except sensitive ones
echo "Copying files to deployment directory..."
rsync -av --exclude='.env' \
          --exclude='service-account.json' \
          --exclude='*firebase-adminsdk*' \
          --exclude='.git' \
          --exclude='venv' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='node_modules' \
          --exclude='.DS_Store' \
          ./ $DEPLOY_DIR/

# Create example templates in the deployment directory
echo "Creating example templates..."
cp .env.example $DEPLOY_DIR/

# Create a README for deployment
cat > $DEPLOY_DIR/DEPLOYMENT_README.md << 'EOF'
# Gista-CrewAI API Deployment Package

This is a secure deployment package for the Gista-CrewAI API with the enhanced auto-create gist functionality.

## Important Security Notes

1. **Environment Variables**: Before deploying, you must set up the required environment variables in your production environment. See `.env.example` for the required variables.

2. **Firebase Service Account**: You must provide a Firebase service account JSON file for authentication. This should be securely stored and not committed to version control.

3. **API Keys**: All API keys should be set as environment variables in your production environment, not hardcoded in the codebase.

## Deployment Steps

1. Set up environment variables in your production environment
2. Provide the Firebase service account JSON file
3. Deploy the functions to Firebase
4. Verify the deployment by running the test scripts

For detailed deployment instructions, refer to the `DEPLOYMENT.md` file.
EOF

echo "===== Deployment package created successfully ====="
echo "The deployment package is ready in the '$DEPLOY_DIR' directory."
echo "IMPORTANT: Before deploying, make sure to set up all required environment variables in your production environment."
echo "           Refer to DEPLOYMENT.md and DEPLOYMENT_README.md for detailed instructions." 