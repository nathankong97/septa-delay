import logging
try:
    from util import get_timestamp, get_today_date, create_dir
except ImportError:
    from .util import get_timestamp, get_today_date, create_dir


def setup_logging():
    # Define the log directory path
    log_dir = f"logs/train-view/{get_today_date()}"
    create_dir(log_dir)

    # Define the log file name with timestamp
    log_filename = f"{log_dir}/{get_timestamp()}.log"

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the logging level

    # Create a file handler to write logs to the file
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)

    # Create a formatter to define the log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Optionally, add a stream handler to print logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
