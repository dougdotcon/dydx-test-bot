"""
Configuration utilities for the trading bot.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

def load_env(env_path: Optional[str] = None) -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file (default: config/.env)
    
    Raises:
        FileNotFoundError: If .env file is not found
    """
    if env_path is None:
        env_path = "config/.env"
    
    env_file = Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(
            f"Environment file not found: {env_path}. "
            "Copy .env.example to .env and configure your credentials."
        )
    
    load_dotenv(env_file)

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to config file (default: config/config.json)
    
    Returns:
        Configuration dictionary
    
    Raises:
        FileNotFoundError: If config file is not found
        json.JSONDecodeError: If config file is not valid JSON
    """
    if config_path is None:
        config_path = "config/config.json"
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    return config

def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to config file (default: config/config.json)
    """
    if config_path is None:
        config_path = "config/config.json"
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration.
    
    Args:
        config: Configuration dictionary
    
    Raises:
        ValueError: If configuration is invalid
    """
    required_keys = {
        "trading": ["market", "timeframe", "volume_factor", "risk_reward_ratio"],
        "risk": ["max_position_size", "max_risk_per_trade"],
        "technical": ["resistance_period", "volume_lookback"],
        "network": {
            "endpoints": ["rest", "ws"]
        }
    }

    def check_keys(data: Dict, keys: Dict, path: str = ""):
        for key, value in keys.items():
            if key not in data:
                raise ValueError(f"Missing required configuration: {path}{key}")
            
            if isinstance(value, list):
                for subkey in value:
                    if subkey not in data[key]:
                        raise ValueError(
                            f"Missing required configuration: {path}{key}.{subkey}"
                        )
            elif isinstance(value, dict):
                check_keys(data[key], value, f"{path}{key}.")

    check_keys(config, required_keys)

def get_env_var(name: str, default: Optional[Any] = None, required: bool = False) -> Any:
    """
    Get environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
    
    Returns:
        Environment variable value or default
    
    Raises:
        ValueError: If required variable is not found
    """
    value = os.getenv(name, default)
    if required and value is None:
        raise ValueError(f"Required environment variable not found: {name}")
    
    return value
