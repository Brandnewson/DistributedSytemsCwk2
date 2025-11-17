import azure.functions as func
import logging
import os
import pymssql
import random
import statistics
import datetime
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="DS_httpTrigger")

### TASK 1: HTTP Trigger Function and Sensor metrics function
def DS_httpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    # Get configuration from query string
    sensor_count = int(req.params.get('sensor_count', 20))
    batch_size = int(req.params.get('batch_size', 10))
    
    # Get database connection from environment variables
    conn_str = {
        "server": os.environ.get("SQL_SERVER"),
        "user": os.environ.get("SQL_USER"),
        "password": os.environ.get("SQL_PASSWORD"),
        "database": os.environ.get("SQL_DATABASE")
    }

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
        
        # Insert sensor data in batches
        insert_sql = """
        INSERT INTO dbo.Sensors (SensorID, Temperature, Wind, RHumidity, CO2, ReadingTime)
        VALUES (%d, %f, %f, %f, %f, %s)
        """
        
        total_records = 0
        with pymssql.connect(**conn_str) as conn:
            with conn.cursor() as cursor:
                for i in range(0, len(sensor_data), batch_size):
                    batch = sensor_data[i:i + batch_size]
                    # Add a timestamp for each reading
                    batch_params = [
                        (d['SensorID'], d['Temperature'], d['Wind'], d['RHumidity'], d['CO2'], datetime.datetime.now())
                        for d in batch
                    ]
                    cursor.executemany(insert_sql, batch_params)
                    total_records += len(batch)
                conn.commit()
        
        return func.HttpResponse(
            f"Successfully inserted {total_records} sensor records (sensor_count={sensor_count}, batch_size={batch_size})",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

def compute_statistics(values):
    if not values:
        return {"mean": None, "median": None, "max": None, "min": None}
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "max": max(values),
        "min": min(values)
    }

@app.route(route="metricsPerSensor", auth_level=func.AuthLevel.ANONYMOUS)
def metricsPerSensor(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    conn_str = os.environ.get("SQL_CONNECTION_STRING")
    if not conn_str:
        return func.HttpResponse("Database connection string not found", status_code=500)

    try:
        # Fetch all sensor readings grouped by SensorID
        query = "SELECT SensorID, Temperature, Wind, RHumidity, CO2 FROM dbo.Sensors"
        data = {}
        with pymssql.connect(**conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    sensor_id = row.SensorID
                    if sensor_id not in data:
                        data[sensor_id] = []
                    data[sensor_id].append({
                        "Temperature": row.Temperature,
                        "Wind": row.Wind,
                        "RHumidity": row.RHumidity,
                        "CO2": row.CO2
                    })

        if not data:
            return func.HttpResponse("No sensor data found.", status_code=404)

        results = {}
        for sensor_id, readings in data.items():
            temperatures = [reading['Temperature'] for reading in readings]
            wind_speeds = [reading['Wind'] for reading in readings]
            rhumidities = [reading['RHumidity'] for reading in readings]
            co2_levels = [reading['CO2'] for reading in readings]

            results[sensor_id] = {
                "Temperature": compute_statistics(temperatures),
                "Wind": compute_statistics(wind_speeds),
                "RHumidity": compute_statistics(rhumidities),
                "CO2": compute_statistics(co2_levels)
            }

        print(results)

        return func.HttpResponse(
            "Sensor metrics analysis complete. Check logs for details.",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


### TASK 2: SQL Trigger and Timer Trigger Functions
@app.schedule(schedule="*/10 * * * * *", arg_name="timer", run_on_startup=True, use_monitor=True)
def timer_trigger(timer: func.TimerRequest) -> None:
    logging.info('Timer trigger function executed at %s', datetime.datetime.now())

    conn_str = {
        "server": os.environ.get("SQL_SERVER"),
        "user": os.environ.get("SQL_USER"),
        "password": os.environ.get("SQL_PASSWORD"),
        "database": os.environ.get("SQL_DATABASE")
    }

    try:
        # Generate sensor data
        sensor_data = []
        sensor_count = 20  # Default sensor count
        batch_size = 10    # Default batch size
        for sensor_id in range(1, sensor_count + 1):
            sensor_data.append({
                'SensorID': sensor_id,
                'Temperature': round(random.uniform(-10.0, 40.0), 2),
                'Wind': round(random.uniform(0.0, 50.0), 2),
                'RHumidity': round(random.uniform(0.0, 100.0), 2),
                'CO2': round(random.uniform(300.0, 2000.0), 2)
            })

        # Insert sensor data in batches
        insert_sql = """
        INSERT INTO dbo.Sensors (SensorID, Temperature, Wind, RHumidity, CO2, ReadingTime)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        total_records = 0
        with pymssql.connect(**conn_str) as conn:
            with conn.cursor() as cursor:
                for i in range(0, len(sensor_data), batch_size):
                    batch = sensor_data[i:i + batch_size]
                    batch_params = [
                        (d['SensorID'], d['Temperature'], d['Wind'], d['RHumidity'], d['CO2'], datetime.datetime.now())
                        for d in batch
                    ]
                    cursor.executemany(insert_sql, batch_params)
                    total_records += len(batch)
                conn.commit()

        logging.info("Successfully inserted %d sensor records", total_records)

    except Exception as e:
        logging.error("Error in timer trigger: %s", str(e))

@app.function_name(name="SensorsSQLTrigger")
@app.sql_trigger(arg_name="sensor_changes",
                 table_name="Sensors",
                 connection_string_setting="SQL_CONNECTION_STRING")
def metricsPerSensor(sensor_changes: str) -> None:
    logging.info("SQL Changes detected: %s", json.loads(sensor_changes))

    conn_str = {
        "server": os.environ.get("SQL_SERVER"),
        "user": os.environ.get("SQL_USER"),
        "password": os.environ.get("SQL_PASSWORD"),
        "database": os.environ.get("SQL_DATABASE")
    }

    try:
        # Fetch all sensor readings grouped by SensorID
        query = "SELECT SensorID, Temperature, Wind, RHumidity, CO2 FROM dbo.Sensors"
        data = {}
        with pymssql.connect(**conn_str) as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    sensor_id = row['SensorID']
                    if sensor_id not in data:
                        data[sensor_id] = []
                    data[sensor_id].append({
                        "Temperature": row['Temperature'],
                        "Wind": row['Wind'],
                        "RHumidity": row['RHumidity'],
                        "CO2": row['CO2']
                    })

        if not data:
            logging.info("No sensor data found.")
            return

        results = {}
        for sensor_id, readings in data.items():
            temperatures = [reading['Temperature'] for reading in readings]
            wind_speeds = [reading['Wind'] for reading in readings]
            rhumidities = [reading['RHumidity'] for reading in readings]
            co2_levels = [reading['CO2'] for reading in readings]

            results[sensor_id] = {
                "Temperature": compute_statistics(temperatures),
                "Wind": compute_statistics(wind_speeds),
                "RHumidity": compute_statistics(rhumidities),
                "CO2": compute_statistics(co2_levels)
            }

        logging.info("Sensor metrics analysis complete: %s", results)

    except Exception as e:
        logging.error("Error in metricsPerSensor: %s", str(e))