import os
import logging
from typing import Any, Dict, List, Optional, Tuple
from clickhouse_driver import Client

DB_URL = os.environ["DB_URL"]

logging.basicConfig(
    level=logging.DEBUG,
    filename="storage.log",
    format="%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

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
        client.execute(
            """
            CREATE TABLE IF NOT EXISTS stats.cti_feeds_stats 
                (
                    feed_name   String,
                    dt  DateTime('Europe/Moscow'),
                    is_updated  UInt8
                ) ENGINE = MergeTree()
                ORDER BY dt;
                """
        )
        return 1
    except Exception as e:
        raise Exception(f"Can't create table: {e}")


def write_stats(data_batch: List[Dict[str, Any]]) -> Optional[int]:
    init_db()
    try:
        client.execute(
            f"INSERT INTO stats.cti_feeds_stats VALUES", to_tuple(data_batch), ";"
        )
        logging.info(f"Inserted {len(data_batch)} items")
        return 1
    except Exception as e:
        raise Exception(f"Unable to insert data into db: {e}")


def to_tuple(data: List[Dict[str, Any]]) -> List[Tuple]:
    tuples_list = []
    for item in data:
        tuples_list.append(tuple(item.values()))
    return tuples_list


def write_to_disk(file_name: str, file_body):
    with open(f"./feeds/{file_name}", "w") as file:
        file.write(file_body)
