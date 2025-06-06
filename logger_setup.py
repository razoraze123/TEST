import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "compta_errors.log")

handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[handler, logging.StreamHandler()]
)

# Dedicated handler for accounting errors
accounting_errors_handler = RotatingFileHandler(
    ERROR_LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
)
accounting_errors_handler.setLevel(logging.ERROR)

accounting_logger = logging.getLogger("accounting")
accounting_logger.addHandler(accounting_errors_handler)
