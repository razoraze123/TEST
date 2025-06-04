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

Use the "Mode sans t\u00eate (headless)" checkbox in the settings page to run Chrome without opening a visible window.

## Image Optimization Tools
The project includes an optional image optimizer. Before using this feature,
download `optipng.exe` and `cwebp.exe` and place them inside the
`tools/optimizers/` directory at the root of the repository (or set their
locations in the **Settings** tab):

```
tools/
  optimizers/
    optipng.exe
    cwebp.exe
```

These executables are required for PNG and WebP optimization. If they are
missing, the optimizer will skip the corresponding formats.
The fields are prefilled with `tools/optimizers/optipng.exe` and
`tools/optimizers/cwebp.exe` but you can override them in the **Settings** tab.

### Using the Optimiser Images Tab
Open the **Optimiser Images** tab from the sidebar and choose the folder
containing PNG or WebP files. Click **Lancer l’optimisation** to start the
process. Progress and messages appear in the console below the progress bar.
You can clear the console or save its contents to a log file using the buttons
provided. The paths to `optipng.exe` and `cwebp.exe` can be changed at any time
in the **Settings** tab.

### Flask Server (Optional)
`flask_server.py` exposes a small HTTP API for uploading and listing product files. Start it separately if needed:

```bash
python flask_server.py
```

The server listens on port `5000` by default.
