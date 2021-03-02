import asyncio
import hashlib
import os
from datetime import datetime
from time import time
from typing import Any, Dict, List

import httpx
import pickledb

# Dirty fix to ignore HTTPS warnings
import urllib3
from pytz import UTC

import storage
import service

urllib3.disable_warnings()

logger = service.log_event(__name__)

FEED_CHUNK_SIZE = 1048576


class Downloader:
    async def get_feed(self, feed: Dict[str, Any]) -> None:
        """
        Download the feed specified. Just get the feed of its own format without any parsing.
        :param feed: Feed object
        """
        time_start = time()
        timeout = httpx.Timeout(5, connect=10)

        async with httpx.AsyncClient(verify=False) as client:
            try:
                response = await client.get(
                    feed["feed_url"], allow_redirects=True, timeout=timeout
                )
                if response.status_code == 200:
                    feed_download_time = time() - time_start
                    hash = hashlib.md5(response.content).hexdigest()
                    logger.info(
                        f"Feed `{feed['feed_name']}` of {len(response.text):.2f} Kbytes downloaded in {feed_download_time:.2f} seconds"
                    )
                    return {feed["feed_name"]: hash}
                else:
                    logger.error(
                        f"Feed `{feed['feed_name']}` can not be downloaded: {response.status_code}: {response.headers}"
                    )
            except Exception as e:
                logger.error(f"Feed `{feed['feed_name']}` can not be downloaded: {e}")

    async def get_all_osint_feeds(self, feeds: List[Dict[str, Any]]) -> None:
        """
        Downloads all opensource feeds from
        configuration file and send it to MQ
        :param feeds: Feeds object
        """
        data = [(self.get_feed(feed)) for feed in feeds]
        results = await asyncio.gather(*data, return_exceptions=False)

        self.workdir = os.path.dirname(os.path.realpath(__file__))
        self.cache = pickledb.load(
            os.path.join(self.workdir, "cache/cache.json"), auto_dump=False
        )

        batch_results: List[Dict[str, Any]] = []
        updated_feeds: List[str] = []

        for feed in results:
            if feed:
                for k, v in feed.items():

                    if self.cache.exists(k):
                        if self.cache.get(k) == v:
                            # print(f"Feed {k} has not changed since last update")
                            batch_results.append(
                                {
                                    "measurement": "update_status",
                                    "tags": {"feed_name": k},
                                    "fields": {"is_updated": 0},
                                    "time": datetime.now(UTC),
                                }
                            )
                    else:
                        # print(f"Feed {k} has been updated {v}")
                        updated_feeds.append(k)
                        self.cache.set(k, v)
                        batch_results.append(
                            {
                                "measurement": "update_status",
                                "tags": {"feed_name": k},
                                "fields": {"is_updated": 1},
                                "time": datetime.now(UTC),
                            }
                        )

        storage.write_stats(batch_results)
        self.cache.dump()
        logger.info(f"{len(updated_feeds)} updated. Updated feeds: {updated_feeds}")

    def get_feeds(self, feeds: List[Dict[str, Any]]) -> None:
        """
        Get all feeds specified in configuration file in async mode
        :param feeds: Feeds object
        """
        time_start = time()

        try:
            asyncio.run(self.get_all_osint_feeds(feeds))
        finally:
            logger.info(
                f"Successfully downloaded {len(feeds)} feeds in {(time() - time_start):.2f} seconds"
            )
