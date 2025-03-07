#!/bin/bash
# Cleanup script for Gista-CrewAI project
# Run this script before committing to clean up temporary files

echo "🧹 Starting cleanup process..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} +
find . -name ".coverage" -delete
find . -name ".coverage.*" -delete

# Remove Jupyter Notebook checkpoints
echo "Removing Jupyter Notebook checkpoints..."
find . -name ".ipynb_checkpoints" -type d -exec rm -rf {} +

# Remove temporary files
echo "Removing temporary files..."
find . -name ".DS_Store" -delete
find . -name "*.log" -delete
find . -name "*.tmp" -delete
find . -name "*.temp" -delete

# Remove virtual environment (uncomment if needed)
# echo "Removing virtual environment..."
# rm -rf venv/

# Remove Node.js modules (uncomment if needed)
# echo "Removing node_modules..."
# find . -name "node_modules" -type d -exec rm -rf {} +

# Remove build artifacts
echo "Removing build artifacts..."
find . -name "build" -type d -exec rm -rf {} +
find . -name "dist" -type d -exec rm -rf {} +
find . -name "*.egg-info" -type d -exec rm -rf {} +

# Remove Firebase logs and cache
echo "Removing Firebase logs and cache..."
find . -name "firebase-debug.log" -delete
find . -name ".firebase" -type d -exec rm -rf {} +

echo "✅ Cleanup complete!"
echo "Total space freed: $(du -sh .)" 