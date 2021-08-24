import asyncio
import hashlib
import os
from datetime import datetime
from time import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pickledb

# Dirty fix to ignore HTTPS warnings
import urllib3
from pytz import UTC

try:
    import service
except ImportError:
    from src import service

urllib3.disable_warnings()

logger = service.log_event(__name__)

FEED_CHUNK_SIZE = 1048576


class Downloader:
    def __init__(self) -> None:
        self.workdir = os.path.dirname(os.path.realpath(__file__))
        self.cache = pickledb.load(
            os.path.join(self.workdir, "cache/cache.json"), auto_dump=False
        )

    async def get_feed(self, feed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Download the feed specified. Just get the feed of its own format without any parsing.
        :param feed: Feed object
        """
        time_start = time()
        successfully_downloaded: int = 0
        unsuccessfully_downloaded: int = 0
        timeout = httpx.Timeout(5, connect=10)

        async with httpx.AsyncClient(verify=False) as client:
            try:
                response = await client.get(
                    feed["feed_url"], allow_redirects=True, timeout=timeout
                )
                if response.status_code == 200:
                    feed_download_time = time() - time_start
                    # TODO: parametrize the option below
                    #
                    # In case you wanna dump feed to the disk
                    # storage.write_to_disk(f"{feed['feed_name']}.{feed['feed_type']}", response.text)
                    hash = hashlib.md5(response.content).hexdigest()
                    # logger.info(
                    #     f"Feed `{feed['feed_name']}` of {len(response.text):.2f} Kbytes downloaded in {feed_download_time:.2f} seconds"
                    # )
                    successfully_downloaded += 1
                    return {feed["feed_name"]: hash}
                else:
                    # logger.error(
                    #     f"Feed `{feed['feed_name']}` can not be downloaded: {response.status_code}: {response.headers}"
                    # )
                    unsuccessfully_downloaded += 1
            except Exception as e:
                logger.error(f"Feed `{feed['feed_name']}` can not be downloaded: {e}")
                unsuccessfully_downloaded += 1

    def is_updated(self, feed_name: str, feed_hash: str) -> bool:
        """
        Check if current feed hash is equal
        to the previous feed hash then returns False,
        otherwise method returns True
        """
        if self.cache.exists(feed_name):
            if self.cache.get(feed_name) == feed_hash:
                return False
            else:
                return True
        else:
            self.cache.set(feed_name, feed_hash)
            self.cache.dump()
            return True

    async def get_all_osint_feeds(self, feeds: List[Dict[str, Any]]) -> None:
        """
        Downloads all opensource feeds from
        configuration file and send it to MQ
        :param feeds: Feeds object
        """
        data = [(self.get_feed(feed)) for feed in feeds]
        results = await asyncio.gather(*data, return_exceptions=False)

        batch_results: List[Tuple] = []
        updated_feeds: List[str] = []

        for feed in results:
            if feed:
                for feed_name, feed_hash in feed.items():
                    if self.is_updated:
                        updated_feeds.append(feed_name)
                        batch_results.append((feed_name, datetime.now(UTC), 1))
                        # print(f"Feed {k} has been updated {v}")
                    elif self.is_updated == False:
                        batch_results.append((feed_name, datetime.now(UTC), 0))
                        # print(f"Feed {k} has not changed since last update")
        # storage.write_stats(batch_results)
        logger.info(
            f"{len(updated_feeds)} feeds updated. Updated feeds: {updated_feeds}"
        )
        return batch_results

    def save_to_database(self, data: List[Tuple]):
        try:
            import storage
        except ImportError:
            from src import storage

        storage.write_stats(data)

    def get_feeds(self, feeds: List[Dict[str, Any]]) -> None:
        """
        Get all feeds specified in configuration file in async mode
        :param feeds: Feeds object
        """
        time_start = time()

        try:
            results = asyncio.run(self.get_all_osint_feeds(feeds))
            self.save_to_database(results)
        finally:
            logger.info(
                f"Successfully downloaded {len(feeds)} feeds in {(time() - time_start):.2f} seconds"
            )
