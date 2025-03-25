"""
Ollama Service - Manages interactions with Ollama AI models
"""

import requests
import logging
import json

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with Ollama models"""
    
    def __init__(self, config):
        """Initialize the Ollama service"""
        self.config = config
        self.base_url = f"{config.get('OLLAMA_HOST')}:{config.get('OLLAMA_PORT')}"
        self.default_model = config.get('DEFAULT_MODEL', 'llama3.2:latest')
        self.models_cache = []
        
    def initialize(self) -> bool:
        """Initialize the Ollama service"""
        try:
            logger.info("Initializing Ollama service...")
            
            # Check if Ollama is running
            self._check_ollama_running()
            
            # Fetch and cache available models
            self.list_models()
            
            logger.info("Ollama service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Ollama service: {str(e)}")
            raise
    
    def _check_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            response.raise_for_status()
            logger.info("Ollama is running")
            return True
        except Exception as e:
            logger.error(f"Ollama is not running: {str(e)}")
            raise Exception("Ollama is not running. Please start Ollama first.")
    
    def list_models(self) -> list:
        """List available models in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            # Extract model names
            if 'models' in data:
                self.models_cache = [model.get('name') for model in data.get('models', [])]
                logger.info(f"Available models: {', '.join(self.models_cache)}")
            else:
                self.models_cache = []
                logger.warning("No models found in Ollama")
            
            return self.models_cache
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            raise
    
    def chat(self, params: dict) -> dict:
        """Chat with an Ollama model"""
        try:
            messages = params.get('messages', [])
            model = params.get('model', self.default_model)
            options = params.get('options', {})
            
            # Check if model exists
            if model not in self.models_cache:
                logger.warning(f"Model {model} not found in cache")
                self.list_models()
                
                if model not in self.models_cache:
                    logger.warning(f"Model {model} not available, using default: {self.default_model}")
                    model = self.default_model
            
            # Prepare request
            request_data = {
                'model': model,
                'messages': messages
            }
            
            # Add options if provided
            if options:
                request_data['options'] = {
                    'temperature': options.get('temperature', 0.7),
                    'top_p': options.get('topP', 0.9),
                    'max_tokens': options.get('maxTokens')
                }
                
                # Remove None values
                request_data['options'] = {k: v for k, v in request_data['options'].items() if v is not None}
            
            # Make API request
            logger.info(f"Sending chat request to model: {model}")
            response = requests.post(f"{self.base_url}/api/chat", json=request_data)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            raise
