"""
Environment Utilities

This module provides utility functions for loading and checking environment variables.
It centralizes the environment configuration logic used across service modules.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_and_load_env_file(override: bool = True) -> Path:
    """
    Find the root .env file and load environment variables from it.
    
    Args:
        override: Whether to override existing environment variables
        
    Returns:
        Path object pointing to the .env file location (even if not found)
    """
    # Find the root directory
    root_dir = Path(__file__).resolve().parent.parent.parent
    env_path = root_dir / '.env'
    logger.info(f"Looking for .env file at: {env_path}")
    
    # Check if the .env file exists
    if env_path.exists():
        logger.info(f".env file found at {env_path}")
        # Try to load the .env file
        load_dotenv(dotenv_path=env_path, override=override)
    else:
        logger.warning(f".env file not found at {env_path}")
    
    return env_path

def check_required_vars(required_vars: List[str]) -> Dict[str, bool]:
    """
    Check if the required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Returns:
        Dictionary mapping variable names to boolean indicating if they are set
    """
    results = {}
    all_set = True
    
    logger.info("Environment check:")
    for var_name in required_vars:
        var_value = os.getenv(var_name)
        if var_value:
            logger.info(f"  {var_name}: SET")
            results[var_name] = True
        else:
            logger.info(f"  {var_name}: NOT SET")
            results[var_name] = False
            all_set = False
    
    results['all_set'] = all_set
    return results

def get_env_with_fallback(primary_var: str, fallback_var: str, default_value: Optional[str] = None) -> str:
    """
    Get an environment variable with fallback options.
    
    Args:
        primary_var: Primary environment variable name
        fallback_var: Fallback environment variable name
        default_value: Default value if neither variable is set
        
    Returns:
        The value of the environment variable or default
    """
    value = os.getenv(primary_var)
    if not value:
        # Try fallback
        value = os.getenv(fallback_var)
        if value:
            logger.info(f"{primary_var} not set, using {fallback_var}: {value}")
        elif default_value:
            # Use default
            logger.warning(f"{primary_var} and {fallback_var} not set, using default: {default_value}")
            value = default_value
    else:
        logger.info(f"Using {primary_var}: {value}")
    
    return value 