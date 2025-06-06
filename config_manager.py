import os
import json
import logging
import tomllib

import logger_setup  # noqa: F401  # configure logging

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.toml")

_DEFAULT_BASE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_OPT_DIR = os.path.join(os.path.dirname(__file__), "tools", "optimizers")

DEFAULTS = {
    "BASE_DIR": _DEFAULT_BASE,
    "CHROME_DRIVER_PATH": None,
    "CHROME_BINARY_PATH": None,
    "OPTIPNG_PATH": os.path.join(_DEFAULT_OPT_DIR, "optipng.exe"),
    "CWEBP_PATH": os.path.join(_DEFAULT_OPT_DIR, "cwebp.exe"),
    "SUFFIX_FILE_PATH": os.path.join(_DEFAULT_BASE, "custom_suffixes.py"),
    "LINKS_FILE_PATH": os.path.join(_DEFAULT_BASE, "liens_clean.txt"),
    "ROOT_FOLDER": "image",
    "THEME": "dark",
    "WP_DOMAIN": "https://monsite.com",
    "WP_UPLOAD_PATH": "wp-content/uploads/2025/06",
    "IMAGE_NAME_PATTERN": "{id}:{variant}-{name}.webp",
}


def load(path: str = CONFIG_FILE) -> dict:
    """Load configuration from *path* and return a dict of values."""
    cfg = DEFAULTS.copy()
    need_write = False
    if os.path.isfile(path):
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            for key in DEFAULTS:
                if data.get(key):
                    cfg[key] = data[key]
        except Exception as e:
            logging.error("Error reading %s: %s", path, e)
            need_write = True
    else:
        logging.warning("Config file %s missing", path)
        need_write = True
    if need_write:
        save(cfg, path)
        logging.info("Default configuration written to %s", path)
        print(f"Default configuration written to {path}")
    return cfg


def save(cfg: dict, path: str = CONFIG_FILE) -> None:
    """Write configuration dictionary to *path* in a minimal TOML format."""
    lines = []
    for key, value in cfg.items():
        if value is None:
            value = ""
        escaped = str(value).replace("\"", "\\\"")
        lines.append(f'{key} = "{escaped}"')
    tmp = "\n".join(lines)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(tmp)
    except Exception as e:
        print(f"Error writing {path}: {e}")
