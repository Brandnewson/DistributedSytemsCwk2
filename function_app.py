import azure.functions as func
import logging
import os
import pyodbc
import random
from datetime import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="DS_httpTrigger")
def DS_httpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    # Get configuration from query string
    sensor_count = int(req.params.get('sensor_count', 20))
    batch_size = int(req.params.get('batch_size', 10))
    
    # Get database connection
    conn_str = os.environ.get("SQL_CONNECTION_STRING")
    if not conn_str:
        return func.HttpResponse("Database connection string not found", status_code=500)
    
    try:
        # Generate sensor data
        sensor_data = []
        for sensor_id in range(1, sensor_count + 1):
            sensor_data.append({
                'SensorID': sensor_id,
                'Temperature': round(random.uniform(-10.0, 40.0), 2),
                'Wind': round(random.uniform(0.0, 50.0), 2),
                'RHumidity': round(random.uniform(0.0, 100.0), 2),
                'CO2': round(random.uniform(300.0, 2000.0), 2)
            })
        
        # Upsert sensor data in batches
        upsert_sql = """
        MERGE dbo.Sensors AS target
        USING (VALUES (?, ?, ?, ?, ?)) AS source (SensorID, Temperature, Wind, RHumidity, CO2)
        ON target.SensorID = source.SensorID
        WHEN MATCHED THEN
            UPDATE SET Temperature = source.Temperature, Wind = source.Wind, 
                      RHumidity = source.RHumidity, CO2 = source.CO2
        WHEN NOT MATCHED THEN
            INSERT (SensorID, Temperature, Wind, RHumidity, CO2)
            VALUES (source.SensorID, source.Temperature, source.Wind, source.RHumidity, source.CO2);
        """
        
        total_records = 0
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                # Process in batches
                for i in range(0, len(sensor_data), batch_size):
                    batch = sensor_data[i:i + batch_size]
                    batch_params = [(d['SensorID'], d['Temperature'], d['Wind'], 
                                   d['RHumidity'], d['CO2']) for d in batch]
                    cursor.executemany(upsert_sql, batch_params)
                    total_records += len(batch)
                conn.commit()
        
        return func.HttpResponse(
            f"Successfully upserted {total_records} sensor records (sensor_count={sensor_count}, batch_size={batch_size})",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)