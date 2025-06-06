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
file is missing or cannot be read, a new one is written automatically using
defaults from `config_manager.py` and a warning is logged to `logs/app.log`.
The file looks like this:

```toml
BASE_DIR = "/path/to/project"
CHROME_DRIVER_PATH = ""
CHROME_BINARY_PATH = ""
OPTIPNG_PATH = "tools/optimizers/optipng.exe"
CWEBP_PATH = "tools/optimizers/cwebp.exe"
SUFFIX_FILE_PATH = "/path/to/project/custom_suffixes.py"
LINKS_FILE_PATH = "/path/to/project/liens_clean.txt"
ROOT_FOLDER = "image"
THEME = "dark"
WP_DOMAIN = "https://monsite.com"
WP_UPLOAD_PATH = "wp-content/uploads/2025/06"
IMAGE_NAME_PATTERN = "{id}:{variant}-{name}.webp"
```

You can edit this file directly or use the **Settings** page in the GUI which
updates it automatically. Each key is described below:

* `BASE_DIR` – directory used to store generated files. Defaults to the folder
  containing `config.py`.
* `CHROME_DRIVER_PATH` – optional path to a `chromedriver` executable (useful
  without internet access)
* `CHROME_BINARY_PATH` – optional path to the Chrome binary
* `OPTIPNG_PATH` – path to the `optipng` executable used for optimisation
* `CWEBP_PATH` – path to the `cwebp` executable
* `SUFFIX_FILE_PATH` – file containing custom suffixes for `scraper_images.py`.
  Defaults to `BASE_DIR/custom_suffixes.py`.
* `LINKS_FILE_PATH` – text file listing product URLs. Defaults to
  `BASE_DIR/liens_clean.txt`.
* `ROOT_FOLDER` – subdirectory inside `BASE_DIR` where images are written.
  Defaults to `"image"`.
* `THEME` – either `dark` or `light`. Controls the application appearance.
* `WP_DOMAIN` – base URL of the WordPress site used when uploading files.
* `WP_UPLOAD_PATH` – target upload directory relative to `WP_DOMAIN`.
* `IMAGE_NAME_PATTERN` – formatting pattern for generated image names.
  The pattern supports `{id}`, `{variant}` and `{name}` placeholders which are
  replaced with the product identifier, variant label and original file name.

A minimal template file `custom_suffixes.example.py` is included in the
repository. Copy it to `custom_suffixes.py` and edit it to provide your own
suffixes. If `CHROME_DRIVER_PATH` is empty, a driver is downloaded
automatically at runtime.

## Running the Application
`Application.py` is the unique entry point aggregating the GUI, scraping and optimizer features. Launch the GUI with:

```bash
python Application.py
```

This starts the PySide6 interface for scraping WooCommerce products and also
launches `flask_server.py` in the background. The API listens on port `5000`
and automatically stops when you close the GUI.

To run the server manually you can execute:

```bash
python flask_server.py
```

Press `Ctrl+C` to stop the service or terminate the process from your
task manager.

Use the "Mode sans t\u00eate (headless)" checkbox in the settings page to run Chrome without opening a visible window.

### Adding Custom Pages

You can extend the dashboard with your own pages:

1. Define a new `_create_<name>_page` method in `DashboardWindow` or
   `BaseWindow`. The method should return the widget representing the page.
2. Call this method inside `_setup_ui` and append the widget to `self.stack`.
3. Insert an entry in the appropriate sidebar section using `add_section` or
   `self.sidebar.addItem` so users can navigate to the page.

Example for a **Saisie de pièces** page:

```python
class DashboardWindow(...):
    def _create_saisie_de_pieces_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Saisie de pièces"))
        layout.addStretch(1)
        return page

    def _setup_ui(self):
        ...
        self.page_saisie = self._create_saisie_de_pieces_page()
        self.stack.addWidget(self.page_saisie)
        ...
        self.sidebar.addItem(QListWidgetItem("Saisie de pièces"))
```

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

### Scraping d’images avancé

Load a product list from an Excel or CSV file containing the columns `ID` and `URL`. Configure the **Lien WordPress** format in the settings by specifying the base upload path, e.g. `https://monsite.com/wp-content/uploads/2025/06/`. When scraping completes, export the resulting table using the dedicated **Exporter** button.

Example snippet of the output table:

```
ID | Variante | URL concurrent | Nom image          | Lien WordPress
A1 | Rouge    | https://...    | a1-rouge-face.webp | https://monsite.com/wp-content/uploads/2025/06/a1-rouge-face.webp
```

### Flask Server API
`flask_server.py` exposes a small HTTP API for uploading and listing product files. The server is started automatically when launching the GUI with `Application.py` and listens on port `5000` by default.

## Logging
All console output is also written to `logs/app.log` at the repository root. The
file rotates automatically when it reaches about 1 MB. Errors coming from the
`accounting` package are additionally stored in `logs/compta_errors.log`.
Monitor the log live with:

```bash
tail -f logs/app.log
```

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

### Using the Rapports Page
Open the **Rapports** page from the sidebar to visualise scraping statistics such as article totals, error counts and batch progression. Charts are generated with Matplotlib and you can export the data to CSV or PDF.

## Utilisation de l’onglet Comptabilité

Ouvrez l’onglet **Comptabilité** depuis la barre latérale pour gérer vos
transactions. Utilisez **Importer relevé…** pour charger un fichier CSV ou Excel
contenant vos opérations. Les colonnes attendues sont décrites dans le fichier
`accounting/HELP.md`. Les lignes importées apparaissent dans un tableau.

Sous la barre de boutons, des filtres permettent de restreindre l’affichage :
période, texte du libellé, plage de montants, type de mouvement, catégorie et
l’option **Non rapprochées**. Les résultats se mettent à jour immédiatement.

Sélectionnez une transaction puis cliquez sur **Rapprocher** pour l’associer à
l’écriture correspondante du journal. L’application suggère automatiquement les
écritures compatibles et marque la ligne comme « Rapprochée » une fois validée.

Le bouton **Exporter** permet d’enregistrer les transactions ou les écritures au
format CSV ou Excel pour un traitement extérieur. Une aide détaillée se trouve
dans le fichier [accounting/HELP.md](accounting/HELP.md).

## Export comptable

L'application prend en charge l'export des journaux et rapports
comptables. Reportez-vous au fichier
[accounting/README.md](accounting/README.md) pour une description
détaillée des formats disponibles et de l'organisation des fichiers.

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

## Node.js and Go Microservices

Additional microservices can be implemented in the `js_modules` and
`go_modules` directories. To start a Node.js service:

```bash
cd js_modules/<service>
npm install
npm start    # or: node dist/index.js
```

For a Go service:

```bash
cd go_modules/<service>
go build
./<service>
```

Stop the service with `Ctrl+C` and interact with its HTTP API using `curl` or
from the main application.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
