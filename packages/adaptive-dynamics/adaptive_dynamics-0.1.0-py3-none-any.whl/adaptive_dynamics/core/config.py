"""Configuration management for Adaptive Dynamics Toolkit."""

import json
import os
from pathlib import Path
from typing import Any


class Config:
    """Configuration manager for ADT modules."""
    
    _instance = None
    _config: dict[str, Any] = {}
    
    def __new__(cls):
        """Singleton implementation."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_defaults()
        return cls._instance
    
    def _load_defaults(self) -> None:
        """Load default configuration settings."""
        self._config = {
            "numerics": {
                "float_precision": "float64",
                "epsilon": 1e-12,
                "max_iterations": 1000
            },
            "logging": {
                "level": "INFO",
                "file": None
            },
            "gpu": {
                "enabled": False,
                "device": 0
            }
        }
        
        # Try to load from user config if it exists
        user_config_path = os.environ.get(
            "ADT_CONFIG", 
            Path.home() / ".adaptive-dynamics" / "config.json"
        )
        
        if Path(user_config_path).exists():
            try:
                with open(user_config_path) as f:
                    user_config = json.load(f)
                    self._update_recursive(self._config, user_config)
            except Exception as e:
                print(f"Warning: Failed to load config from {user_config_path}: {e}")
    
    def _update_recursive(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """Recursively update a nested dictionary."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_recursive(target[key], value)
            else:
                target[key] = value
    
    def get(self, key_path: str, default: Any | None = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., "numerics.epsilon")
            default: Default value if key doesn't exist
            
        Returns:
            The configuration value or default if not found
        """
        keys = key_path.split(".")
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., "numerics.epsilon")
            value: Value to set
        """
        keys = key_path.split(".")
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_user_config(self, path: str | None = None) -> None:
        """
        Save current configuration to user config file.
        
        Args:
            path: Optional custom path for the config file
        """
        if path is None:
            path = os.environ.get(
                "ADT_CONFIG", 
                str(Path.home() / ".adaptive-dynamics" / "config.json")
            )
        
        # Ensure directory exists
        config_dir = os.path.dirname(path)
        os.makedirs(config_dir, exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(self._config, f, indent=2)


# Create default instance
config = Config()