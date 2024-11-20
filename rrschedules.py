import requests
import json
import os
import logging
from datetime import datetime

# TODO: Need to research train number data
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


today_date = datetime.now().strftime("%Y-%m-%d")

scraping_dir = f"scraping/rr-schedule/{today_date}"
log_dir = f"logs/rr-schedule/{today_date}"

os.makedirs(scraping_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Set up logging
log_filename = f"{log_dir}/{get_timestamp()}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

json_filename = f"{scraping_dir}/rr-schedule_{get_timestamp()}.json"

API_URL = "https://www3.septa.org/api/RRSchedules/index.php"


def fetch_and_store_data():
    try:
        # Fetching data from the API
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

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
