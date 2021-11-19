import os
from typing import List, Tuple
from clickhouse_driver import Client

DB_URL = os.environ["DB_URL"]

try:
    client = Client(DB_URL)
except Exception as e:
    raise Exception(e)

def init_db():
    try:
        client.execute(f"CREATE DATABASE IF NOT EXISTS stats;")
    except Exception as e:
        raise Exception(f"Can't create db: {e}")
    try:
        client.execute("""
            CREATE TABLE IF NOT EXISTS stats.cti_feeds_stats 
                (
                    feed_name   String,
                    dt  DateTime('Europe/Moscow'),
                    is_updated  UInt8
                ) ENGINE = MergeTree()
                ORDER BY dt;
                """
            )
    except Exception as e:
        raise Exception(f"Can't create table: {e}")

def write_stats(data_batch: List[Tuple]):
    init_db()
    try:
        client.execute(f'INSERT INTO stats.cti_feeds_stats VALUES', data_batch, ";")
    except Exception as e:
        raise Exception(f"Unable to insert data into db: {e}")

def write_to_disk(file_name: str, file_body):
    with open(f"./feeds/{file_name}", "w") as file:
        file.write(file_body)