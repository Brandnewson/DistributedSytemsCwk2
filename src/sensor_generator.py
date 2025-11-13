"""
Sensor data generator module.
Generates simulated sensor readings with realistic variations.
"""
import random
from datetime import datetime
from typing import List, Tuple, Dict, Any

class SensorReading:
    """Represents a single sensor reading."""
    
    def __init__(
        self,
        sensor_id: str,
        temperature: float,
        wind_speed: float,
        humidity: float,
        co2_level: float,
        timestamp: datetime = None
    ):
        """
        Initialize a sensor reading.
        
        Args:
            sensor_id: Unique sensor identifier (e.g., "SENSOR_001")
            temperature: Temperature in Celsius
            wind_speed: Wind speed in miles per hour
            humidity: Relative humidity percentage (0-100)
            co2_level: CO2 level in parts per million (ppm)
            timestamp: Reading timestamp (defaults to now)
        """
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.wind_speed = wind_speed
        self.humidity = humidity
        self.co2_level = co2_level
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_tuple(self) -> Tuple[str, datetime, float, float, float, float]:
        """
        Convert reading to tuple for database insertion.
        
        Returns:
            Tuple: (sensor_id, timestamp, temperature, wind_speed, humidity, co2_level)
        """
        return (
            self.sensor_id,
            self.timestamp,
            self.temperature,
            self.wind_speed,
            self.humidity,
            self.co2_level
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert reading to dictionary.
        
        Returns:
            Dictionary representation of the reading
        """
        return {
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'wind_speed': self.wind_speed,
            'humidity': self.humidity,
            'co2_level': self.co2_level
        }


class SensorGenerator:
    """Generator for simulated sensor readings with a range."""
    
    # Baseline values for Leeds, UK weather patterns
    BASE_TEMPERATURE = 10.0  # Celsius
    BASE_WIND_SPEED = 5.0   # kph
    BASE_HUMIDITY = 40.0     # %
    BASE_CO2_LEVEL = 420.0   # ppm
    
    # Variation ranges (min, max offsets from base)
    TEMP_VARIATION = (-10.0, 10.0)
    WIND_VARIATION = (0.0, 20.0)
    HUMIDITY_VARIATION = (-20.0, 20.0)
    CO2_VARIATION = (-50.0, 200.0)
    
    def __init__(self, sensor_count):
        """
        Initialize the sensor generator.
        
        Args:
            sensor_count: Number of sensors to simulate
        """
        self.sensor_count = sensor_count
        self.sensor_ids = [f"{i:03d}" for i in range(1, sensor_count + 1)]
    
    def generate_reading(self, sensor_id: str) -> SensorReading:
        """
        Generate a single sensor reading with random variations.
        
        Args:
            sensor_id: The sensor identifier
        
        Returns:
            SensorReading: A new sensor reading with randomized values
        """
        temperature = self.BASE_TEMPERATURE + random.uniform(*self.TEMP_VARIATION)
        wind_speed = max(0, self.BASE_WIND_SPEED + random.uniform(*self.WIND_VARIATION))
        humidity = max(0, min(100, self.BASE_HUMIDITY + random.uniform(*self.HUMIDITY_VARIATION)))
        co2_level = max(300, self.BASE_CO2_LEVEL + random.uniform(*self.CO2_VARIATION))
        
        # Round values to 2 decimal places
        temperature = round(temperature, 2)
        wind_speed = round(wind_speed, 2)
        humidity = round(humidity, 2)
        co2_level = round(co2_level, 2)
        
        return SensorReading(
            sensor_id=sensor_id,
            temperature=temperature,
            wind_speed=wind_speed,
            humidity=humidity,
            co2_level=co2_level
        )
    
    def generate_batch(self, count: int = None) -> List[SensorReading]:
        """
        Generate a batch of sensor readings.
        
        Args:
            count: Number of readings to generate (defaults to sensor_count)
        
        Returns:
            List of SensorReading objects
        """
        if count is None:
            count = self.sensor_count
        
        readings = []
        timestamp = datetime.now()
        
        # Generate readings for the specified number of sensors
        for i in range(count):
            sensor_id = self.sensor_ids[i % len(self.sensor_ids)]
            reading = self.generate_reading(sensor_id)
            reading.timestamp = timestamp
            readings.append(reading)
        
        return readings
    
    def readings_to_tuples(self, readings: List[SensorReading]) -> List[Tuple]:
        """
        Convert list of readings to list of tuples for batch insert.
        
        Args:
            readings: List of SensorReading objects
        
        Returns:
            List of tuples ready for database insertion
        """
        return [reading.to_tuple() for reading in readings]
