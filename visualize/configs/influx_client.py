from os import path

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient.from_config_file("assets/files/config.ini")

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()
