import os
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

URL = os.environ["INFLUX_URL"]
TOKEN = os.environ["INFLUX_TOKEN"]
ORG = os.environ["INFLUX_ORG"]
BUCKET = os.environ["INFLUX_BUCKET"]

# TODO: Get config directly from ENV: https://github.com/influxdata/influxdb-client-python
client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)


def write_stats(data_batch):
    write_api.write(BUCKET, ORG, data_batch)
    client.__del__()

def write_to_disk(file_name: str, file_body):
    with open(f"./feeds/{file_name}", "w") as file:
        file.write(file_body)