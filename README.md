# Setup and Usage

## Requirements
- Python 3.10 or newer.
- Google Chrome. The ChromeDriver binary is downloaded automatically at runtime if `CHROME_DRIVER_PATH` is not provided.

Install the Python dependencies using:

```bash
pip install -r requirements.txt
```

### Quick Start

```bash
pip install -r requirements.txt
python Application.py
```

## Configuring Paths
Paths are read from environment variables so you can customise them without
modifying the source. The defaults are defined in `config.py`:

* `BASE_DIR` – directory used to store generated files. Defaults to the folder
  containing `config.py`.
* `CHROME_DRIVER_PATH` – optional path to a `chromedriver` executable (useful
  without internet access)
* `CHROME_BINARY_PATH` – optional path to the Chrome binary
* `SUFFIX_FILE_PATH` – file containing custom suffixes for `scraper_images.py`.
  Defaults to `BASE_DIR/custom_suffixes.py`.
* `LINKS_FILE_PATH` – text file listing product URLs. Defaults to
  `BASE_DIR/liens_clean.txt`.

A minimal template file `custom_suffixes.example.py` is included in the
repository. Copy it to `custom_suffixes.py` and edit it to provide your own
suffixes.

Set the environment variables to override these locations when running the
scripts.

Example on Linux/macOS:

```bash
export BASE_DIR=/path/to/project
export CHROME_DRIVER_PATH=/path/to/chromedriver  # only if you want to skip auto download
export CHROME_BINARY_PATH=/path/to/chrome
```

If `CHROME_DRIVER_PATH` is not set, a driver is downloaded automatically at
runtime. Other variables fall back to the values defined in `config.py`.

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

### Flask Server (Optional)
`flask_server.py` exposes a small HTTP API for uploading and listing product files. Start it separately if needed:

```bash
python flask_server.py
```

The server listens on port `5000` by default.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
