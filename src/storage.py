import os
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
# token = "my-super-secret-auth-token"
# org = "org_name"
# bucket = "cti_feeds"

URL = os.environ["INFLUX_URL"]
TOKEN = os.environ["INFLUX_TOKEN"]
ORG = os.environ["INFLUX_ORG"]
BUCKET = os.environ["INFLUX_BUCKET"]

# TODO: Get config from ENV: https://github.com/influxdata/influxdb-client-python
client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)

write_api = client.write_api(write_options=SYNCHRONOUS)


def write_stats(data_batch):
    write_api.write(BUCKET, ORG, data_batch)
    client.__del__()
