class BaseScraper:
    """Base class for scraping plugins."""

    def __init__(self, *args, **kwargs):
        pass

    def scrape_product(self, *args, **kwargs):
        raise NotImplementedError

    def scrape_images(self, *args, **kwargs):
        raise NotImplementedError
