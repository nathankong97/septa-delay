import logging
import os
from septa.core.utils import get_today_date, create_dir


def setup_logging(module_name):
    log_dir = os.path.join("../logs", module_name, get_today_date())
    create_dir(log_dir)

    # Fixed log filename
    log_filename = os.path.join(log_dir, f"{module_name}.log")

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(console_handler)

    return logger
