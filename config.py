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


def reload() -> Dict[str, str | None]:
    """Reload configuration from disk and update module globals."""
    global BASE_DIR, CHROME_DRIVER_PATH, CHROME_BINARY_PATH, OPTIPNG_PATH, CWEBP_PATH, SUFFIX_FILE_PATH, LINKS_FILE_PATH, ROOT_FOLDER
    _new = config_manager.load()
    BASE_DIR = _new["BASE_DIR"]
    CHROME_DRIVER_PATH = _new["CHROME_DRIVER_PATH"]
    CHROME_BINARY_PATH = _new["CHROME_BINARY_PATH"]
    OPTIPNG_PATH = _new["OPTIPNG_PATH"]
    CWEBP_PATH = _new["CWEBP_PATH"]
    SUFFIX_FILE_PATH = _new["SUFFIX_FILE_PATH"]
    LINKS_FILE_PATH = _new["LINKS_FILE_PATH"]
    ROOT_FOLDER = _new["ROOT_FOLDER"]
    return _new
