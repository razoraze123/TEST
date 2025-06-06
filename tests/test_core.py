import os
import pandas as pd
import asyncio
import pytest

from scraper_core import ScraperCore
from plugins import woocommerce as scraper_woocommerce


class DummyBrowser:
    async def close(self):
        pass

class DummyChromium:
    async def launch(self, headless=True):
        return DummyBrowser()

class DummyPlay:
    chromium = DummyChromium()
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.mark.asyncio
async def test_scrap_produits_parsing(monkeypatch, tmp_path):
    simple_html = (tmp_path / "simple.html")
    variable_html = (tmp_path / "variable.html")
    # copy example data
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    simple_html.write_text(open(os.path.join(data_dir, "simple.html")).read())
    variable_html.write_text(open(os.path.join(data_dir, "variable.html")).read())

    html_map = {
        "http://simple": simple_html.read_text(),
        "http://var": variable_html.read_text(),
    }

    async def fake_scrape(self, browser, url):
        return html_map[url]

    monkeypatch.setattr(scraper_woocommerce, "async_playwright", lambda: DummyPlay())
    monkeypatch.setattr(ScraperCore, "async_scrape_product", fake_scrape)

    captured = {}
    monkeypatch.setattr(pd.DataFrame, "to_excel", lambda self, path, index=False: captured.setdefault("df", self))

    core = ScraperCore(base_dir=tmp_path)
    id_url_map = {"1": "http://simple", "2": "http://var"}
    ids = ["1", "2"]
    ok, err = await core._scrap_produits_par_ids_async(id_url_map, ids, [], None, lambda: False, True)

    df = captured.get("df")
    assert ok == 2
    assert err == 0
    assert len(df) == 4
    simple_row = df[df["ID Produit"] == "1"].iloc[0]
    assert simple_row["Type"] == "simple"
    assert simple_row["Name"] == "Basic Product"
    variable_rows = df[df["ID Produit"] == "2"]
    assert set(variable_rows["Type"]) == {"variable", "variation"}
    var_parent = variable_rows[variable_rows["Type"] == "variable"].iloc[0]
    assert var_parent["Attribute 1 value(s)"] == "Red | Green"


def test_clean_helpers():
    assert ScraperCore.clean_name("Crème Brûlée-") == "creme brulee"
    assert ScraperCore.clean_filename("Crème Brûlée!.jpg") == "creme-bruleejpg"
