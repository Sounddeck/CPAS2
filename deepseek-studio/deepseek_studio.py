"""
Deepseek Studio - Complete Local AI Development Environment
Main application file combining all components.
"""

import os
import sys
import json
import logging
import argparse
import threading
from pathlib import Path

# Flask for API
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

# Core modules
from deepseek_studio.utils.config import Config
from deepseek_studio.services.ollama import OllamaService
from deepseek_studio.services.database import DatabaseService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("app")

# Flask application
app = Flask(__name__, static_folder='frontend/dist')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global services
config = None
ollama_service = None
database_service = None

# Path configurations
HOME_DIR = os.path.expanduser("~")
APP_DIR = os.path.join(HOME_DIR, ".deepseek-studio")
DATA_DIR = os.path.join(APP_DIR, "data")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

def ensure_directories_exist():
    """Ensure all required directories exist"""
    directories = [APP_DIR, DATA_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")

def initialize_services():
    """Initialize all services"""
    global config, ollama_service, database_service
    
    # Load configuration
    config = Config(CONFIG_PATH)
    config.load_or_create_default()
    
    # Update default model to llama3.2
    config.set('DEFAULT_MODEL', 'llama3.2:latest')
    config.save()
    
    # Initialize database first as other services depend on it
    database_service = DatabaseService(config)
    database_service.initialize()

    # Initialize Ollama service
    ollama_service = OllamaService(config)
    ollama_service.initialize()

    logger.info("All services initialized successfully")

def shutdown_services():
    """Gracefully shutdown all services"""
    logger.info("Shutting down services...")
    
    # Close database connections
    if database_service:
        database_service.close()
    
    logger.info("All services shut down successfully")

# API Routes
@app.route('/')
def serve_frontend():
    """Serve the frontend application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files"""
    return send_from_directory(app.static_folder, path)

@app.route('/api/ollama/chat', methods=['POST'])
def chat():
    """Chat with Ollama model"""
    try:
        data = request.json
        response = ollama_service.chat(data)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ollama/models', methods=['GET'])
def list_models():
    """List available Ollama models"""
    try:
        models = ollama_service.list_models()
        return jsonify(models)
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({"error": str(e)}), 500

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Deepseek Studio - Local AI Development Environment")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the API server")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind the API server")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    try:
        # Ensure required directories exist
        ensure_directories_exist()
        
        # Initialize services
        initialize_services()
        
        # Run the Flask app
        logger.info(f"Starting API server on {args.host}:{args.port}")
        socketio.run(app, host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        # Shutdown services
        shutdown_services()

if __name__ == "__main__":
    main()
