"""
Utility functions for the Memory Layer SDK.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the config file. If None, uses default location.
        
    Returns:
        Dictionary containing configuration data
    """
    if config_path is None:
        config_path = os.path.join(Path.home(), ".memory-layer", "config.json")
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    return {}


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> bool:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path to the config file. If None, uses default location.
        
    Returns:
        True if save was successful, False otherwise
    """
    if config_path is None:
        config_path = os.path.join(Path.home(), ".memory-layer", "config.json")
    
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def get_api_key_from_env() -> Optional[str]:
    """
    Get API key from environment variables.
    
    Returns:
        API key if found, None otherwise
    """
    return os.getenv("MEMORY_LAYER_API_KEY")


def format_memory_for_display(memory: Dict[str, Any], max_length: int = 100) -> str:
    """
    Format a memory for display purposes.
    
    Args:
        memory: Memory dictionary from the API
        max_length: Maximum length of content to display
        
    Returns:
        Formatted string representation of the memory
    """
    content = memory.get("content", "")
    if len(content) > max_length:
        content = content[:max_length] + "..."
    
    memory_id = memory.get("id", "unknown")
    created_at = memory.get("created_at", "unknown")
    
    return f"[{memory_id}] {content} (created: {created_at})"


def validate_api_key(api_key: str) -> bool:
    """
    Validate the format of an API key.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if the API key format is valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Memory Layer API keys should start with 'mlive_'
    if not api_key.startswith('mlive_'):
        return False
    
    # Should have minimum length
    if len(api_key) < 20:
        return False
    
    return True
