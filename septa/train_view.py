from datetime import datetime

from septa.core.fetcher import fetch_data
from septa.core.logger import setup_logging
from septa.core.utils import create_dir
from septa.core.database import store_train_view, init_db
from config import API_URLS, TRAIN_VIEW_LOG_DIR

logger = setup_logging("train_view")
create_dir(TRAIN_VIEW_LOG_DIR)


def fetch_and_store_train_view():
    try:
        logger.info("Starting Train View scraper...")
        data = fetch_data(API_URLS["train_view"])
        if not data:
            logger.warning("Received empty Train View data.")
            return
        timestamp = datetime.utcnow()
        init_db()
        store_train_view(data, timestamp)
        logger.info(f"Train View data stored.")

    except Exception as e:
        logger.error(f"Failed to fetch or store Train View data: {e}")


if __name__ == "__main__":
    fetch_and_store_train_view()
