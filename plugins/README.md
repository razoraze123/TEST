# Scraping Plugins

Each scraper implementation lives in its own module inside this folder.
A plugin must define a subclass of `BaseScraper` and implement the
methods used by the application (e.g. `scrape_product`, `scrape_images`,
`scrap_produits_par_ids`, ...).

To create a new connector:

1. Create a new `yourplatform.py` file here.
2. Implement a `class YourScraper(BaseScraper)` providing the required
   methods.
3. Update `config.toml` by setting `SCRAPER_PLUGIN = "plugins.yourplatform"`.

The `ScraperCore` class will automatically load the plugin specified in
this configuration value.
