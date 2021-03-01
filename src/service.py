import logging
import os
from typing import Any, Dict, List, Optional
import yaml


def log_event(module_name: str, log_level=logging.INFO) -> Optional[logging.Logger]:
    """
    Write meesages into log file
    """
    logger = logging.getLogger(
        module_name
    )  # another approach is to use `logger.propagate = False`
    if not len(logger.handlers):
        handler = logging.FileHandler("collector.log")
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s: %(message)s",
            datefmt="%d-%m-%Y %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger
    else:
        return logger


def load_config(config_path: str) -> Optional[Dict[str, Any]]:
    """
    Load configuration from file
    :param config_path: Custom path to configuration file
    """

    logger = log_event(__name__)
    workdir = os.path.dirname(os.path.realpath("__file__"))

    if config_path is not None:
        try:
            with open(os.path.join(workdir, config_path), "r") as config_file:
                config = yaml.safe_load(config_file)
            return config
        except yaml.YAMLError as e:
            logger.error(f"An error excepted while trying to read config: {e}")
            exit()
    else:
        logger.error("Configuration file not found")
        exit()


def load_feeds(feed_path: str) -> List[Dict[str, Any]]:
    feeds = load_config(feed_path)
    feed: Dict[str, Any] = {}
    feed_pack: List = [feed]
    logger = log_event(__name__)

    for item in feeds["COMMUNITY_FEEDS"].items():
        feed["feed_name"] = item[0]
        for property in item[1]:
            if "url" in property:
                feed["feed_url"] = property["url"]
            elif "type" in property:
                feed["feed_type"] = property["type"]
        feed_pack.append(feed.copy())
    logger.info(f"Feeds loaded: got {len(feed_pack)} feeds from config")

    return feed_pack
