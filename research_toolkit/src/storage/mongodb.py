"""
MongoDB storage client for storing research documents.

Handles connection, insertion, and querying of research documents.
"""

from typing import Dict, Any, Optional, List
import os
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError


class MongoDBClient:
    """
    MongoDB client for storing and retrieving research documents.
    
    Uses a collection named 'research_documents' to store all research responses.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize MongoDB client.
        
        Args:
            connection_string: MongoDB connection string. If None, reads from
                              MONGODB_CONNECTION_STRING environment variable.
        """
        if connection_string is None:
            connection_string = os.getenv("MONGODB_CONNECTION_STRING")
            if not connection_string:
                raise ValueError(
                    "MongoDB connection string required. Provide as argument or "
                    "set MONGODB_CONNECTION_STRING environment variable."
                )
        
        self.connection_string = connection_string
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        self._connected = False
    
    def connect(self, database_name: str = "research_toolkit", collection_name: str = "research_documents") -> None:
        """
        Connect to MongoDB and initialize collection.
        
        Args:
            database_name: Name of the database to use (default: "research_toolkit")
            collection_name: Name of the collection to use (default: "research_documents")
            
        Raises:
            ConnectionFailure: If connection to MongoDB fails
        """
        try:
            # Close existing connection if any
            if self.client:
                self.client.close()
            
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            self._connected = True
        except ConnectionFailure as e:
            self._connected = False
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}")
    
    def switch_connection(self, connection_string: str, database_name: str = "research_toolkit", collection_name: str = "research_documents") -> None:
        """
        Switch to a different MongoDB connection.
        
        Args:
            connection_string: New MongoDB connection string
            database_name: Name of the database to use
            collection_name: Name of the collection to use
            
        Raises:
            ConnectionFailure: If connection to MongoDB fails
        """
        self.connection_string = connection_string
        self.connect(database_name, collection_name)
    
    def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a single document into the collection.
        
        Args:
            document: Document dictionary to insert
            
        Returns:
            Dictionary with 'inserted_id' key containing the ObjectId
            
        Raises:
            RuntimeError: If not connected to MongoDB
            PyMongoError: If insertion fails
        """
        if not self._connected or self.collection is None:
            raise RuntimeError("Not connected to MongoDB. Call connect() first.")
        
        try:
            result = self.collection.insert_one(document)
            return {"inserted_id": str(result.inserted_id)}
        except PyMongoError as e:
            raise PyMongoError(f"Failed to insert document: {e}")
    
    def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the filter.
        
        Args:
            filter: Query filter dictionary
            
        Returns:
            Document dictionary if found, None otherwise
            
        Raises:
            RuntimeError: If not connected to MongoDB
            PyMongoError: If query fails
        """
        if not self._connected or self.collection is None:
            raise RuntimeError("Not connected to MongoDB. Call connect() first.")
        
        try:
            result = self.collection.find_one(filter)
            # Convert ObjectId to string for JSON serialization
            if result and "_id" in result:
                result["_id"] = str(result["_id"])
            return result
        except PyMongoError as e:
            raise PyMongoError(f"Failed to find document: {e}")
    
    def find(self, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the filter.
        
        Args:
            filter: Query filter dictionary. If None, returns all documents.
            
        Returns:
            List of document dictionaries
            
        Raises:
            RuntimeError: If not connected to MongoDB
            PyMongoError: If query fails
        """
        if not self._connected or self.collection is None:
            raise RuntimeError("Not connected to MongoDB. Call connect() first.")
        
        try:
            if filter is None:
                cursor = self.collection.find()
            else:
                cursor = self.collection.find(filter)
            
            results = list(cursor)
            # Convert ObjectId to string for JSON serialization
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])
            return results
        except PyMongoError as e:
            raise PyMongoError(f"Failed to find documents: {e}")
    
    def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self._connected = False
    
    def __enter__(self):
        """Context manager entry."""
        if not self._connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

