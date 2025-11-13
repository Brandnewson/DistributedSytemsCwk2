"""
Database module for Azure SQL connectivity.
Provides connection management and query execution utilities.
"""
import pyodbc
from typing import List, Tuple, Any, Optional
from .config import config

class Database:
    """Database connection and query execution manager."""
    
    def __init__(self):
        """Initialize database connection parameters."""
        self.connection_string = config.sql_connection_string
    
    def get_connection(self) -> pyodbc.Connection:
        """
        Create and return a database connection.
        
        Returns:
            pyodbc.Connection: Active database connection
        
        Raises:
            Exception: If connection fails
        """
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except Exception as e:
            raise
    
    def execute_batch_insert(
        self, 
        query: str, 
        values: List[Tuple[Any, ...]]
    ) -> int:
        """
        Execute a basic batch insert operation.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, values)
        conn.commit()
        row_count = len(values)
        cursor.close()
        conn.close()
        return row_count

# Global database instance
database = Database()
