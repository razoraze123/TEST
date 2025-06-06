import json

import pytest

from scraper_core import ScraperCore


class DummySpan:
    def __init__(self, text):
        self._text = text

    @property
    def text(self):
        return self._text


class DummyLabel:
    def __init__(self, driver, name):
        self.driver = driver
        self.name = name

    def is_displayed(self):
        return True

    def click(self):
        self.driver.current_variant = self.name

    def find_element(self, by=None, value=None):
        return DummySpan(self.name)


class DummyImg:
    def __init__(self, src):
        self.src = src

    def get_attribute(self, name):
        if name == "src":
            return self.src
        return None


class DummyDriver:
    def __init__(self, pages):
        self.pages = pages
        self.current_url = None
        self.current_variant = None

    def execute_cdp_cmd(self, *a, **k):
        pass

    def get(self, url):
        self.current_url = url

    def find_elements(self, by=None, value=None):
        page = self.pages[self.current_url]
        if value == "label.color-swatch":
            return [DummyLabel(self, n) for n in page["variants"]]
        if value == ".product-gallery__media img":
            imgs = page["variants"][self.current_variant]
            return [DummyImg(s) for s in imgs]
        return []

    def quit(self):
        pass


def test_scrap_images_variantes(monkeypatch, tmp_path):
    pages = {
        "http://p1": {
            "variants": {
                "Red": ["http://img/red1.webp"],
                "Blue": ["http://img/blue1.webp"],
            }
        }
    }

    monkeypatch.setattr(
        "selenium.webdriver.Chrome", lambda service=None, options=None: DummyDriver(pages)
    )
    monkeypatch.setattr(
        "webdriver_manager.chrome.ChromeDriverManager.install", lambda self=None: "driver"
    )
    monkeypatch.setattr("time.sleep", lambda *a, **k: None)

    core = ScraperCore(base_dir=tmp_path)
    items = [{"id": "99", "url": "http://p1"}]
    df = core.scrap_images_variantes(items, "https://wp", "upload", "{id}-{variant}-{name}")

    assert set(df.columns) == {
        "id produit",
        "variante",
        "url concurrent",
        "nom image",
        "lien wordpress",
    }
    assert len(df) == 2
    assert df.iloc[0]["lien wordpress"].startswith("https://wp/upload/")

    mapping_path = tmp_path / "mapping_images_variantes.json"
    assert mapping_path.exists()
    mapping = json.loads(mapping_path.read_text())
    assert "99" in mapping and "Red" in mapping["99"]
