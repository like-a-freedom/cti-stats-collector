import time
import schedule
import worker
import service

logger = service.log_event(__name__)
worker = worker.Downloader()

FEED_PATH: str = "config/feeds.yaml"


def start_collecting(feeds):
    logger.info("--- CTI stats collector started: it's time to grab some feeds ---")
    worker.get_feeds(feeds)
    logger.info("--- CTI stats collector stopped: cooldown ---")


if __name__ == "__main__":
    feeds = service.load_feeds(FEED_PATH)
    schedule.every(1).minutes.do(start_collecting, feeds)

    while True:
        schedule.run_pending()
        time.sleep(1)
