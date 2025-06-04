# Setup and Usage

## Requirements
- Python 3.10 or newer.
- Google Chrome and the matching ChromeDriver.

Install the Python dependencies using:

```bash
pip install -r requirements.txt
```

## Configuring Paths
Edit `config.py` and update the following variables so that they point to your local installation:

```python
BASE_DIR = r"C:\\path\\to\\project"
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, r"path/to/chromedriver.exe")
CHROME_BINARY_PATH = os.path.join(BASE_DIR, r"path/to/chrome.exe")
```

`BASE_DIR` defines where scraped data and output files will be stored. The paths for `CHROME_DRIVER_PATH` and `CHROME_BINARY_PATH` must correspond to your Chrome driver and Chrome executable.

## Running the Application
Launch the GUI application with:

```bash
python main.py
```

This starts the PySide6 interface for scraping WooCommerce products.

### Flask Server (Optional)
`flask_server.py` exposes a small HTTP API for uploading and listing product files. Start it separately if needed:

```bash
python flask_server.py
```

The server listens on port `5000` by default.
