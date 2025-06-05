# Setup and Usage
[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)

## Requirements
- Python 3.10 or newer.
- Google Chrome. The ChromeDriver binary is downloaded automatically at runtime if `CHROME_DRIVER_PATH` is empty.

Install the project using:

```bash
pip install .
```

If you plan to use asynchronous scraping, also install the
`playwright` browsers with:

```bash
playwright install
```

### Quick Start

```bash
pip install .
python Application.py
```

### Other Installation Options

- **Docker**

  ```bash
  docker build -t woocommerce-scraper .
  docker run --rm woocommerce-scraper
  ```

- **Standalone Executable**

  ```bash
  ./build.sh
  dist/woocommerce-scraper --help
  ```

### Running Tests

```bash
pip install .[test]
pytest
```

### Asynchronous Scraping

The scraping functions can run concurrently using `asyncio` and
`playwright`. Pass `concurrent=True` to
`scrap_produits_par_ids`, `scrap_fiches_concurrents` or `ScraperCore.start_scraping`
to enable this mode. Install the extra dependency and browsers with:

```bash
pip install playwright
playwright install
```

## Configuring Paths
Paths are stored in a `config.toml` file located at the repository root. If the
file does not exist, default values from `config_manager.py` are used. The file
contains entries such as:

```toml
BASE_DIR = "/path/to/project"
CHROME_DRIVER_PATH = "/path/to/chromedriver"
CHROME_BINARY_PATH = "/path/to/chrome"
SUFFIX_FILE_PATH = "/path/to/custom_suffixes.py"
LINKS_FILE_PATH = "/path/to/liens_clean.txt"
OPTIPNG_PATH = "tools/optimizers/optipng.exe"
CWEBP_PATH = "tools/optimizers/cwebp.exe"
ROOT_FOLDER = "image"
THEME = "dark"
```

You can edit this file directly or use the **Settings** page in the GUI which
updates it automatically. The defaults mirror the previous behaviour:

* `BASE_DIR` – directory used to store generated files. Defaults to the folder
  containing `config.py`.
* `CHROME_DRIVER_PATH` – optional path to a `chromedriver` executable (useful
  without internet access)
* `CHROME_BINARY_PATH` – optional path to the Chrome binary
* `SUFFIX_FILE_PATH` – file containing custom suffixes for `scraper_images.py`.
  Defaults to `BASE_DIR/custom_suffixes.py`.
* `LINKS_FILE_PATH` – text file listing product URLs. Defaults to
  `BASE_DIR/liens_clean.txt`.
* `THEME` – either `dark` or `light`. Controls the application appearance.

A minimal template file `custom_suffixes.example.py` is included in the
repository. Copy it to `custom_suffixes.py` and edit it to provide your own
suffixes. If `CHROME_DRIVER_PATH` is empty, a driver is downloaded
automatically at runtime.

## Running the Application
`Application.py` is the unique entry point aggregating the GUI, scraping and optimizer features. Launch the GUI with:

```bash
python Application.py
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

### Using the Visual Selector Tab
Open the **Sélecteur visuel** tab from the sidebar and enter the URL of a
product page. After the page loads, move the mouse over the web page to
highlight elements and click one to generate a CSS selector. You can **Copier**
the selector to the clipboard or **Sauvegarder** it. Saved selectors are stored
  in `selectors.json` at the root of the project.

The JavaScript helper `qwebchannel.js` required by this tool is bundled in the
repository at `ui/resources/qwebchannel.js`. If it is missing, the application
falls back to the version provided by PySide6.

### Scraping d’image

The **Scraping d’image** tab now displays a thumbnail preview before files are
saved. Uncheck any images you do not want and press **Enregistrer la
sélection** to move the remaining files into the destination folder. Optional
filters let you ignore images below a certain size or ratio and restrict the
source file type. When saving, a SHA-256 hash is calculated for each picture and
duplicates already present in the target directory are skipped.

### Flask Server (Optional)
`flask_server.py` exposes a small HTTP API for uploading and listing product files. Start it separately if needed:

```bash
python flask_server.py
```

The server listens on port `5000` by default.

## Logging
All console output is also written to `logs/app.log` at the repository root. The
file rotates automatically when it reaches about 1 MB.

## Resuming a Scrape
During scraping, progress is stored in `scraping_checkpoint.json` inside
`BASE_DIR`. If the process stops unexpectedly, run
`ScraperCore.start_scraping(resume=True)` with the same parameters to continue
from the last checkpoint.

## Database

All scraped information is also stored in an SQLite database located at
`BASE_DIR/scraper.db`. The file is created automatically on first use. You can
query it directly using the helper functions in `storage.py` or any SQLite
client. For example:

```bash
python - <<'EOF'
from storage import search_products
print(search_products("shoe"))
EOF
```

Future versions of the CLI and HTTP API will expose similar search features.

## Command Line Interface

Installing the project with `pip install .` exposes a `woocommerce-scraper`
command that provides a few helpful utilities:

```bash
woocommerce-scraper scrape            # scrape descriptions
woocommerce-scraper scrape-images     # download product images
woocommerce-scraper optimize FOLDER   # optimize images inside FOLDER
woocommerce-scraper resume            # continue a previous scrape
```

### Automating with Cron (Linux/macOS)

Add a cron entry with `crontab -e` to run the scraper periodically. For example
to start every day at 3 AM:

```cron
0 3 * * * /usr/bin/woocommerce-scraper scrape >> /path/to/log.txt 2>&1
```

### Automating with Windows Task Scheduler

Create a new **Basic Task** and set the action to start `cmd.exe` with the
argument:

```
/C woocommerce-scraper scrape
```

Ensure that Python and the console script are in the system `PATH`.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
