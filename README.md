# Setup and Usage

## Requirements
- Python 3.10 or newer.
- Google Chrome and the matching ChromeDriver.

Install the Python dependencies using:

```bash
pip install -r requirements.txt
```

## Configuring Paths
Paths are read from environment variables so you can customise them without
modifying the source. Set the following variables before running the scripts
(or adjust the defaults in `config.py`):

* `BASE_DIR` – directory used to store generated files
* `CHROME_DRIVER_PATH` – path to your `chromedriver` executable
* `CHROME_BINARY_PATH` – path to the Chrome binary
* `SUFFIX_FILE_PATH` – file containing custom suffixes for `scraper_images.py`
* `LINKS_FILE_PATH` – text file listing product URLs

Example on Linux/macOS:

```bash
export BASE_DIR=/path/to/project
export CHROME_DRIVER_PATH=/path/to/chromedriver
export CHROME_BINARY_PATH=/path/to/chrome
```

If these variables are not set, reasonable defaults defined in `config.py` are
used.

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

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
