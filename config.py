import os
from septa.core.utils import get_today_date, get_timestamp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRAPING_DIR = os.path.join(BASE_DIR, "scraping")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

API_URLS = {
    "train_view": "https://www3.septa.org/api/TrainView/index.php",
    "rr_schedules": "https://www3.septa.org/api/RRSchedules/index.php?req1=",
    "trip_updates": "https://www3.septa.org/gtfsrt/septarail-pa-us/Trip/rtTripUpdates.pb",
    "rss_url": "https://github.com/septadev/GTFS/releases.atom",
    "gtfs_public": "https://www3.septa.org/developer/gtfs_public.zip"
}

TRAIN_VIEW_LOG_DIR = os.path.join(LOGS_DIR, "train-view", get_today_date())

RR_SCHEDULES_DIR = os.path.join(LOGS_DIR, "rr-schedules", get_today_date())
RR_SCHEDULES_JSON = os.path.join(SCRAPING_DIR, f"rr_schedules_{get_timestamp()}.json")

TRIP_UPDATES_LOG_DIR = os.path.join(LOGS_DIR, "trip-updates", get_today_date())

GTFS_ZIP_PATH = os.path.join(DATA_DIR, "septa_gtfs.zip")
GTFS_RAIL_PATH = os.path.join(DATA_DIR, "google_rail.zip")
GTFS_DB_PATH = os.path.join(DATA_DIR, "septa.sqlite")

TRAIN_VIEW_DB_PATH = os.path.join(DATA_DIR, "train_view.db")
TRAIN_VIEW_DB_URL = f"sqlite:///{TRAIN_VIEW_DB_PATH}"

TRIP_UPDATES_DB_PATH = os.path.join(DATA_DIR, "trip_updates.db")
TRIP_UPDATES_DB_URL = f"sqlite:///{TRIP_UPDATES_DB_PATH}"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SCRAPING_DIR, exist_ok=True)
os.makedirs(TRAIN_VIEW_LOG_DIR, exist_ok=True)
os.makedirs(RR_SCHEDULES_DIR, exist_ok=True)
os.makedirs(TRIP_UPDATES_LOG_DIR, exist_ok=True)

