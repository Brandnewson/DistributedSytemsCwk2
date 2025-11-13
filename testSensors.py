import json
from src.sensor_generator import SensorGenerator

with open("local.settings.json", "r") as f:
    settings = json.load(f)

sensor_count = int(settings["Values"].get("SENSOR_COUNT"))
generator = SensorGenerator(sensor_count)
readings = generator.generate_batch()
for reading in readings:
    print(reading.to_dict())