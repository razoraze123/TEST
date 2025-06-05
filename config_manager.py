import os
import json
import tomllib

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
}


def load(path: str = CONFIG_FILE) -> dict:
    """Load configuration from *path* and return a dict of values."""
    cfg = DEFAULTS.copy()
    if os.path.isfile(path):
        try:
            with open(path, "rb") as f:
                content = f.read()
            try:
                data = tomllib.loads(content.decode("utf-8"))
            except Exception:
                data = json.loads(content.decode("utf-8"))
            for key in DEFAULTS:
                if key in data and data[key] not in ("", None):
                    cfg[key] = data[key]
        except Exception as e:
            print(f"Error reading {path}: {e}")
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
