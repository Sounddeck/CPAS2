"""
Database Service - Manages interactions with MongoDB
"""

import os
import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for interacting with MongoDB database"""
    
    def __init__(self, config):
        """Initialize the database service"""
        self.config = config
        self.uri = config.get('MONGODB_URI', 'mongodb://localhost:27017')
        self.db_name = config.get('MONGODB_DB_NAME', 'deepseek_studio')
        self.client = None
        self.db = None
        self.collections = {}
        self.data_path = config.get('MONGODB_DATA_PATH', 
                                  os.path.join(os.path.expanduser('~'), '.deepseek-studio', 'data', 'mongodb'))
    
    def initialize(self) -> bool:
        """Initialize the database service"""
        try:
            logger.info("Initializing database service...")
            
            # Ensure data directory exists
            self._ensure_data_directory()
            
            # Connect to MongoDB
            self._connect()
            
            # Initialize basic collections
            self._initialize_collections()
            
            logger.info("Database service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database service: {str(e)}")
            raise
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path, exist_ok=True)
            logger.info(f"Created MongoDB data directory: {self.data_path}")
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB database: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def _initialize_collections(self):
        """Initialize required collections"""
        required_collections = [
            'conversations',
            'agents',
            'settings'
        ]
        
        for collection_name in required_collections:
            self.collections[collection_name] = self.db[collection_name]
            
            # Create indexes if needed
            if collection_name == 'conversations':
                self.collections[collection_name].create_index([('timestamp', -1)])
            elif collection_name in ['agents', 'settings']:
                self.collections[collection_name].create_index([('id', 1)], unique=True)
        
        # Insert default settings if needed
        if self.db.settings.count_documents({}) == 0:
            self.db.settings.insert_one({
                'id': 'app-settings',
                'theme': 'system',
                'language': 'en',
                'defaultModel': 'llama3.2:latest',
                'saveConversations': True
            })
        
        logger.info("MongoDB collections initialized")
    
    def query(self, collection_name, query=None, options=None):
        """Query documents from a collection"""
        try:
            if not self.db:
                raise Exception('Database not connected')
            
            collection = self.db[collection_name]
            query = query or {}
            options = options or {}
            
            if options.get('findOne'):
                return collection.find_one(query)
            else:
                cursor = collection.find(query)
                
                if options.get('limit'):
                    cursor = cursor.limit(options['limit'])
                
                if options.get('sort'):
                    cursor = cursor.sort(list(options['sort'].items()))
                
                return list(cursor)
        except Exception as e:
            logger.error(f"Query error in collection {collection_name}: {str(e)}")
            raise
    
    def insert(self, collection_name, document):
        """Insert a document into a collection"""
        try:
            if not self.db:
                raise Exception('Database not connected')
            
            collection = self.db[collection_name]
            
            if isinstance(document, list):
                result = collection.insert_many(document)
                return result.inserted_ids
            else:
                result = collection.insert_one(document)
                return result.inserted_id
        except Exception as e:
            logger.error(f"Insert error in collection {collection_name}: {str(e)}")
            raise
    
    def close(self):
        """Close database connection"""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                logger.info("Closed MongoDB connection")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")
