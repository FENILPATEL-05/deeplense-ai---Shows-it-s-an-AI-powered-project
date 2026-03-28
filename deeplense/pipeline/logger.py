import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "errors.log")

logger = logging.getLogger("deeplense_pipeline")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(console_fmt)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.WARNING)
file_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(file_fmt)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
