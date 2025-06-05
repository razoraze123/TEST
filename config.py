import os

# Default base directory (can be overridden via the BASE_DIR environment variable)
BASE_DIR = os.environ.get(
    "BASE_DIR",
    r"C:\\Users\\Lamine\\Desktop\\woocommerce\\code\\CODE POUR BOB",
)

# Default paths for Chrome driver and binary; can be overridden with
# CHROME_DRIVER_PATH and CHROME_BINARY_PATH environment variables
CHROME_DRIVER_PATH = os.environ.get(
    "CHROME_DRIVER_PATH",
    os.path.join(
        BASE_DIR,
        r"../chromdrivers 137/chromedriver-win64/chromedriver.exe",
    ),
)
CHROME_BINARY_PATH = os.environ.get(
    "CHROME_BINARY_PATH",
    os.path.join(BASE_DIR, r"../chromdrivers 137/chrome-win64/chrome.exe"),
)

# Default paths for image optimizers
_OPT_DIR = os.path.join(os.path.dirname(__file__), "tools", "optimizers")
OPTIPNG_PATH = os.path.join(_OPT_DIR, "optipng.exe")
CWEBP_PATH = os.path.join(_OPT_DIR, "cwebp.exe")

# Optional configuration for scraper_images.py
SUFFIX_FILE_PATH = os.environ.get(
    "SUFFIX_FILE_PATH",
    r"C:\\Users\\Lamine\\Desktop\\woocommerce\\code\\custom_suffixes.py",
)
LINKS_FILE_PATH = os.environ.get(
    "LINKS_FILE_PATH",
    r"C:\\Users\\Lamine\\Desktop\\woocommerce\\code\\liens_clean.txt",
)
ROOT_FOLDER = os.environ.get("ROOT_FOLDER", "image")
