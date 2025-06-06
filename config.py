from __future__ import annotations
import os
from typing import Dict

import config_manager

_cfg = config_manager.load()

BASE_DIR = _cfg["BASE_DIR"]
CHROME_DRIVER_PATH = _cfg["CHROME_DRIVER_PATH"]
CHROME_BINARY_PATH = _cfg["CHROME_BINARY_PATH"]
_OPT_DIR = os.path.join(os.path.dirname(__file__), "tools", "optimizers")
OPTIPNG_PATH = _cfg["OPTIPNG_PATH"]
CWEBP_PATH = _cfg["CWEBP_PATH"]
SUFFIX_FILE_PATH = _cfg["SUFFIX_FILE_PATH"]
LINKS_FILE_PATH = _cfg["LINKS_FILE_PATH"]
ROOT_FOLDER = _cfg["ROOT_FOLDER"]
THEME = _cfg["THEME"]
WP_DOMAIN = _cfg["WP_DOMAIN"]
WP_UPLOAD_PATH = _cfg["WP_UPLOAD_PATH"]
IMAGE_NAME_PATTERN = _cfg["IMAGE_NAME_PATTERN"]
SCRAPER_PLUGIN = _cfg.get("SCRAPER_PLUGIN", "plugins.woocommerce")
ENABLE_FLASK_API = _cfg.get("ENABLE_FLASK_API", "false")


def reload() -> Dict[str, str | None]:
    """Reload configuration from disk and update module globals."""
    global BASE_DIR, CHROME_DRIVER_PATH, CHROME_BINARY_PATH, OPTIPNG_PATH, CWEBP_PATH, SUFFIX_FILE_PATH, LINKS_FILE_PATH, ROOT_FOLDER, THEME, WP_DOMAIN, WP_UPLOAD_PATH, IMAGE_NAME_PATTERN, SCRAPER_PLUGIN, ENABLE_FLASK_API
    _new = config_manager.load()
    BASE_DIR = _new["BASE_DIR"]
    CHROME_DRIVER_PATH = _new["CHROME_DRIVER_PATH"]
    CHROME_BINARY_PATH = _new["CHROME_BINARY_PATH"]
    OPTIPNG_PATH = _new["OPTIPNG_PATH"]
    CWEBP_PATH = _new["CWEBP_PATH"]
    SUFFIX_FILE_PATH = _new["SUFFIX_FILE_PATH"]
    LINKS_FILE_PATH = _new["LINKS_FILE_PATH"]
    ROOT_FOLDER = _new["ROOT_FOLDER"]
    THEME = _new["THEME"]
    WP_DOMAIN = _new["WP_DOMAIN"]
    WP_UPLOAD_PATH = _new["WP_UPLOAD_PATH"]
    IMAGE_NAME_PATTERN = _new["IMAGE_NAME_PATTERN"]
    SCRAPER_PLUGIN = _new.get("SCRAPER_PLUGIN", "plugins.woocommerce")
    ENABLE_FLASK_API = _new.get("ENABLE_FLASK_API", "false")
    return _new
