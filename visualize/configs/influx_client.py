from os import path
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

client = InfluxDBClient.from_config_file(path.join(path.dirname(__file__), "..", "..", "config.ini"))

write_api = client.write_api(write_options=ASYNCHRONOUS)
query_api = client.query_api()