## Setup
- Install Python dependencies (Python >=3.10) with:
  ```bash
  pip install .
  ```
- For tests, install extras and Playwright browsers if needed:
  ```bash
  pip install .[test]
  playwright install
  ```
- Optional Docker build:
  ```bash
  docker build -t woocommerce-scraper .
  docker run --rm woocommerce-scraper
  ```
- Node.js microservices live under `js_modules/`:
  ```bash
  cd js_modules/<service>
  npm install
  npm start       # or: node dist/index.js
  ```
- Go microservices under `go_modules/`:
  ```bash
  cd go_modules/<service>
  go build
  ./<service>
  ```
- Native C module example:
  ```bash
  cd c_modules/hello
  make
  ```
- Native Rust module example:
  ```bash
  cd rust_modules/hello
  cargo build --release
  ```
- The SQLite database is created automatically on first run using paths from `config.toml`.

## Lancement & tests
- Launch the graphical application:
  ```bash
  python Application.py
  ```
- Start only the Flask API:
  ```bash
  python flask_server.py
  ```
- Run the full test suite:
  ```bash
  pytest
  ```
- Example CLI usage after installation:
  ```bash
  woocommerce-scraper scrape            # scrape descriptions
  woocommerce-scraper scrape-images     # download product images
  woocommerce-scraper optimize FOLDER   # optimize images inside FOLDER
  woocommerce-scraper resume            # continue a previous scrape
  woocommerce-scraper workflow cfg.toml # run image workflow
  ```

## Code style & lint
- No formatting or lint configuration (Black, Ruff, etc.) detected.
- No pre-commit hooks defined.

## Convention de commit / branche
- No commit message or branching convention found.

## Fichiers ou dossiers à NE PAS modifier
- Generated folders such as `build/`, `dist/`, `*.egg-info/`.
- Caches: `__pycache__/`, `*.py[cod]`, `env/`, `.venv`, `.env`.
- Logs and database files under `logs/` and `*.db`.

## Recettes ou workflows spéciaux
- Configuration values live in `config.toml`; if missing, running the app will generate one with defaults.
- Image optimization expects `optipng.exe` and `cwebp.exe` inside `tools/optimizers/` unless paths are overridden.
- Scrape progress can be resumed using `ScraperCore.start_scraping(resume=True)` or the `woocommerce-scraper resume` command.
- Workflows defined by a TOML file can be run and replayed using `image_pipeline.run_pipeline` or the CLI `woocommerce-scraper workflow`.

## Exemple de pull-request ou checklist
- No PR template found in `.github/`.
