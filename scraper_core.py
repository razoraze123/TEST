import importlib
from typing import Any

import config
from plugins.base import BaseScraper


def _get_plugin_cls(module_name: str) -> type[BaseScraper]:
    module = importlib.import_module(module_name)
    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and issubclass(obj, BaseScraper) and obj is not BaseScraper:
            return obj
    raise ImportError(f"No BaseScraper subclass found in {module_name}")


class ScraperCore:
    """Load and proxy a scraping plugin."""

    plugin_cls: type[BaseScraper] | None = _get_plugin_cls(getattr(config, "SCRAPER_PLUGIN", "plugins.woocommerce"))

    def __init__(self, plugin: str | None = None, **kwargs: Any):
        module_name = plugin or getattr(config, "SCRAPER_PLUGIN", "plugins.woocommerce")
        cls = _get_plugin_cls(module_name)
        ScraperCore.plugin_cls = cls
        self._plugin = cls(**kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._plugin, name)

    # expose common helper methods at class level
    @staticmethod
    def clean_name(name: str) -> str:
        if ScraperCore.plugin_cls is None:
            raise AttributeError("plugin not initialised")
        return ScraperCore.plugin_cls.clean_name(name)  # type: ignore[attr-defined]

    @staticmethod
    def clean_filename(name: str) -> str:
        if ScraperCore.plugin_cls is None:
            raise AttributeError("plugin not initialised")
        return ScraperCore.plugin_cls.clean_filename(name)  # type: ignore[attr-defined]

    @staticmethod
    def slugify(text: str) -> str:
        if ScraperCore.plugin_cls is None:
            raise AttributeError("plugin not initialised")
        return ScraperCore.plugin_cls.slugify(text)  # type: ignore[attr-defined]
