"""
Configuration utilities for Deepseek Studio
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for Deepseek Studio"""
    
    def __init__(self, config_path):
        """Initialize the configuration manager"""
        self.config_path = config_path
        self.config_data = {}
        self.default_config = {
            # Model settings
            'DEFAULT_MODEL': 'llama3.2:latest',
            'OLLAMA_HOST': 'http://localhost',
            'OLLAMA_PORT': '11434',
            
            # System settings
            'LOG_LEVEL': 'INFO',
            
            # MongoDB settings
            'MONGODB_URI': 'mongodb://localhost:27017',
            'MONGODB_DB_NAME': 'deepseek_studio',
            'MONGODB_AUTO_START': True,
            'MONGODB_DATA_PATH': os.path.join(os.path.expanduser('~'), '.deepseek-studio', 'data', 'mongodb'),
            
            # UI settings
            'THEME': 'system',
            'LANGUAGE': 'en',
        }
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def save(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def load_or_create_default(self):
        """Load configuration or create default if it doesn't exist"""
        if not self.load():
            logger.info("Creating default configuration")
            self.config_data = self.default_config.copy()
            return self.save()
        return True
    
    def get(self, key, default=None):
        """Get a configuration value"""
        # Check in config data
        value = self.config_data.get(key)
        if value is not None:
            return value
        
        # Check in environment variables
        env_value = os.environ.get(key)
        if env_value is not None:
            # Convert some types
            if env_value.lower() in ['true', 'false']:
                return env_value.lower() == 'true'
            try:
                # Try to convert to int or float
                if '.' in env_value:
                    return float(env_value)
                return int(env_value)
            except ValueError:
                pass
            return env_value
        
        # Fall back to default config
        return self.default_config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value"""
        self.config_data[key] = value
    
    def update(self, new_config):
        """Update configuration with new values"""
        self.config_data.update(new_config)
        return self.save()
    
    def reset(self):
        """Reset configuration to default"""
        self.config_data = self.default_config.copy()
        return self.save()

