from datetime import datetime
import streamlit as st

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from pandas import DataFrame
import asyncio

import warnings
from influxdb_client.client.warnings import MissingPivotFunction

warnings.simplefilter("ignore", MissingPivotFunction)

bucket = "datahub"
org = "BDPOC"

@st.experimental_singleton
def get_influx_client():
    return InfluxDBClient.from_config_file("config.ini")

async def query_data(time, device, tags=[]):
    if (not device) or (len(tags) == 0):
        return DataFrame()
    client = get_influx_client()
    query = f'''from(bucket: {json.dumps(bucket)})
						|> range(start: -{time})
						|> filter(fn: (r) => r._measurement == {json.dumps(device)})
						|> filter(fn: (r) => contains(value: r._field, set: {json.dumps(tags)}))
						|> keep(columns: ["_time", "_value", "_field"])
                        //|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''
    # print(query)
    print("Bat dau")
    tables = client.query_api().query_data_frame(query, org=org)
    print("xong")
    return tables
