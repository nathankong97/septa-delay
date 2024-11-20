from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import requests
import json
import os
import logging
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


today_date = datetime.now().strftime("%Y-%m-%d")

scraping_dir = f"scraping/trip-updates/{today_date}"
log_dir = f"logs/trip-updates/{today_date}"

os.makedirs(scraping_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Set up logging
log_filename = f"{log_dir}/{get_timestamp()}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

json_filename = f"{scraping_dir}/trip-updates_{get_timestamp()}.json"

API_URL = "https://www3.septa.org/api/gtfsrt/septarail-pa-us/Trip/print.php"


def fetch_and_store_data():
    try:
        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get(API_URL)
        response.raise_for_status()
        feed.ParseFromString(response.content)
        data = MessageToDict(feed.entity)

        # Store data in JSON file
        with open(json_filename, "w") as file:
            json.dump(data, file, indent=4)

        logging.info(f"Data fetched and stored at {datetime.now()}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
    except Exception as e:
        logging.error(f"Error processing data: {e}")


# Run the function once for testing
fetch_and_store_data()
