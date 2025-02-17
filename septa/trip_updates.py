import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
from datetime import datetime

from septa.core.utils import create_dir
from septa.core.logger import setup_logging
from septa.core.database import store_trip_updates, init_trip_updates_db
from config import API_URLS, TRIP_UPDATES_LOG_DIR

logger = setup_logging("trip_updates")
create_dir(TRIP_UPDATES_LOG_DIR)


def fetch_trip_updates():
    try:
        logger.info("Starting Trip Updates scraper...")
        response = requests.get(API_URLS["trip_updates"], timeout=15)
        response.raise_for_status()
        if not response.content:
            logger.warning("Received empty trip updates.")
            return

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        data = MessageToDict(feed)
        trip_updates = data.get("entity", [])
        if trip_updates:
            timestamp = datetime.utcnow()
            store_trip_updates(trip_updates, timestamp)
            logger.info(f"Stored {len(trip_updates)} trip updates in SQLite.")

        else:
            logger.warning("No trip updates found.")
        logger.info("Trip Updates scraping completed.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching trip updates: {e}")
    except Exception as e:
        logger.error(f"Error processing trip updates: {e}")


if __name__ == "__main__":
    init_trip_updates_db()
    fetch_trip_updates()
