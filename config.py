import os

# Default base directory (update as needed)
BASE_DIR = r"C:\\Users\\Lamine\\Desktop\\woocommerce\\code\\CODE POUR BOB"

# Default paths for Chrome driver and binary
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, r"../chromdrivers 137/chromedriver-win64/chromedriver.exe")
CHROME_BINARY_PATH = os.path.join(BASE_DIR, r"../chromdrivers 137/chrome-win64/chrome.exe")

# Default paths for image optimizers
_OPT_DIR = os.path.join(os.path.dirname(__file__), "tools", "optimizers")
OPTIPNG_PATH = os.path.join(_OPT_DIR, "optipng.exe")
CWEBP_PATH = os.path.join(_OPT_DIR, "cwebp.exe")
