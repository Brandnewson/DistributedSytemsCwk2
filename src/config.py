"""
Configuration module for Azure Functions.
Loads environment variables and provides configuration values.
"""
import os
from typing import Optional


class Config:
    """Configuration class for the sensor data collection system."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.sql_connection_string = os.environ.get('SQL_CONNECTION_STRING', '')
        self.sensor_count = int(os.environ.get('SENSOR_COUNT', '20'))
        self.batch_size = int(os.environ.get('BATCH_SIZE', '20'))
        self.app_insights_key = os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY', '')
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.sql_connection_string:
            return False, "SQL_CONNECTION_STRING not configured"
        
        if self.sensor_count <= 0:
            return False, "SENSOR_COUNT must be positive"
        
        if self.batch_size <= 0:
            return False, "BATCH_SIZE must be positive"
        
        return True, None


# Global configuration instance
config = Config()
