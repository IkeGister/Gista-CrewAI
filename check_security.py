#!/usr/bin/env python3
"""
Security check script for Gista-CrewAI API deployment.
This script scans the codebase for potential security issues before deployment.
"""

import os
import re
import sys
from pathlib import Path
import json

# Patterns to look for
PATTERNS = {
    "API Key": r'[a-zA-Z0-9_-]{20,}',
    "Firebase Key": r'AIza[a-zA-Z0-9_-]{35}',
    "Private Key": r'-----BEGIN PRIVATE KEY-----',
    "Password": r'password["\s:=]+[^;,\s]{8,}',
    "Bearer Token": r'bearer\s+[a-zA-Z0-9_\-\.]+',
    "Authorization Header": r'authorization["\s:=]+[^;,\s]{8,}',
    "IP Address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
}

# Files and directories to ignore
IGNORE_DIRS = [
    '.git', 'venv', 'env', 'node_modules', '__pycache__', 
    'build', 'dist', '.pytest_cache', '.coverage'
]
IGNORE_FILES = [
    '.env', '.env.example', 'service-account.json', '.gitignore',
    'check_security.py', 'DEPLOYMENT.md', 'README.md'
]
IGNORE_EXTENSIONS = [
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin',
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.pdf'
]

def should_ignore(path):
    """Check if a file or directory should be ignored."""
    path_parts = path.parts
    
    # Check if any part of the path is in IGNORE_DIRS
    if any(part in IGNORE_DIRS for part in path_parts):
        return True
    
    # Check if the file name is in IGNORE_FILES
    if path.name in IGNORE_FILES:
        return True
    
    # Check if the file extension is in IGNORE_EXTENSIONS
    if path.suffix in IGNORE_EXTENSIONS:
        return True
    
    return False

def scan_file(file_path):
    """Scan a file for potential security issues."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            for pattern_name, pattern in PATTERNS.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Skip if it's likely a false positive
                    match_text = match.group(0)
                    if (pattern_name == "API Key" and 
                        (len(match_text) > 100 or 
                         "example" in match_text.lower() or 
                         "your-" in match_text.lower())):
                        continue
                    
                    line_num = content[:match.start()].count('\n') + 1
                    context = content[max(0, match.start() - 20):match.start() + len(match_text) + 20]
                    context = context.replace('\n', ' ').strip()
                    
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'pattern': pattern_name,
                        'context': f"...{context}..."
                    })
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return issues

def main():
    """Main function to scan the codebase."""
    root_dir = Path('.')
    all_issues = []
    
    print("Scanning for potential security issues...")
    
    for path in root_dir.glob('**/*'):
        if path.is_file() and not should_ignore(path):
            issues = scan_file(path)
            all_issues.extend(issues)
    
    if all_issues:
        print(f"\n🚨 Found {len(all_issues)} potential security issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"\n{i}. {issue['pattern']} in {issue['file']} (line {issue['line']}):")
            print(f"   {issue['context']}")
        
        print("\n⚠️  Please review these issues before deployment!")
        print("   Remember to remove or secure any sensitive information.")
        return 1
    else:
        print("\n✅ No potential security issues found!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 