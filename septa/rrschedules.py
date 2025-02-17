import json
import os
import asyncio
import aiohttp
import requests
import zipfile
import feedparser
from datetime import datetime, timedelta

from septa.core.logger import setup_logging
from septa.core.utils import create_dir
from septa.core.database import update_database, get_realtime_queries
from config import API_URLS, GTFS_ZIP_PATH, DATA_DIR, RR_SCHEDULES_JSON, RR_SCHEDULES_DIR

logger = setup_logging("rr_schedules")
create_dir(RR_SCHEDULES_DIR)


def check_gtfs_update() -> bool:
    """Check if GTFS data has been updated in the last 24 hours."""
    try:
        feed = feedparser.parse(API_URLS["rss_url"])
        if not feed.entries:
            logger.warning("RSS feed is empty. Skipping GTFS update check.")
            return False

        latest_update = feed["entries"][0].get("updated", None)
        if not latest_update:
            logger.warning("RSS feed has no 'updated' timestamp. Skipping GTFS update check.")
            return False

        update_datetime = datetime.strptime(latest_update, "%Y-%m-%dT%H:%M:%SZ")
        one_day_ago = datetime.utcnow() - timedelta(days=1)

        return one_day_ago <= update_datetime <= datetime.utcnow()
    except Exception as e:
        logger.error(f"Failed to check GTFS update: {e}")
        return False


def download_and_extract_gtfs() -> None:
    """Download and extract the latest GTFS data."""
    try:
        logger.info("Downloading GTFS ZIP file...")
        with requests.get(API_URLS["gtfs_public"], stream=True, timeout=10) as response:
            response.raise_for_status()
            with open(GTFS_ZIP_PATH, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

        logger.info("Extracting GTFS ZIP file...")
        with zipfile.ZipFile(GTFS_ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(DATA_DIR)

        os.remove(GTFS_ZIP_PATH)
        logger.info("GTFS extraction completed.")

    except requests.exceptions.Timeout:
        logger.error("GTFS download timed out.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to process GTFS data: {e}")


async def fetch_rr_schedule(session, query):
    """Fetch real-time schedule data."""
    url = f"{API_URLS['rr_schedules']}{query}"
    try:
        async with session.get(url) as response:
            data = await response.json()
            return {query: data}
    except Exception as e:
        logger.error(f"Error fetching schedule for {query}: {e}")
        return {query: None}


async def fetch_all_rr_schedules(queries):
    """Fetch all schedules asynchronously."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rr_schedule(session, q) for q in queries]
        return await asyncio.gather(*tasks)


def save_to_json(data) -> None:
    """Save fetched schedule data to JSON."""
    try:
        with open(RR_SCHEDULES_JSON, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Schedule data saved at {RR_SCHEDULES_JSON}")
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")


if __name__ == "__main__":
    logger.info("Starting rail schedules processing...")

    # Step 1: Check for GTFS updates and update database if needed
    if check_gtfs_update():
        logger.info("New GTFS update found. Processing...")
        download_and_extract_gtfs()
        update_database(DATA_DIR)
    else:
        logger.info("No new GTFS updates found.")

    # Step 2: Fetch real-time schedules using database queries
    try:
        output = get_realtime_queries()
        if output:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            data = loop.run_until_complete(fetch_all_rr_schedules(output))
            save_to_json(data)
            logger.info("Rail schedules fetching completed.")
        else:
            logger.warning("No valid queries found for real-time schedule fetching.")

    except Exception as e:
        logger.critical(f"Critical error occurred: {e}", exc_info=True)
