import json
import os
import db
import config
from image_pipeline import run_pipeline, replay_workflow
from scraper_core import ScraperCore
from optimizer import ImageOptimizer


def test_run_and_replay_pipeline(monkeypatch, tmp_path):
    cfg_path = tmp_path / "wf.toml"
    cfg_path.write_text("order=['scrape_images','optimize']\n")
    links = tmp_path / "links.txt"
    links.write_text("http://p1\n")

    monkeypatch.setattr(config, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(config, "ROOT_FOLDER", "out")
    monkeypatch.setattr(config, "LINKS_FILE_PATH", str(links))

    calls = []
    from plugins import woocommerce
    monkeypatch.setattr(woocommerce.WooCommerceScraper, "charger_liste_urls", lambda self, path: ["http://p1"])
    monkeypatch.setattr(woocommerce.WooCommerceScraper, "scrap_images", lambda self, urls, dest, **k: calls.append(("scrape", dest)))
    monkeypatch.setattr(ImageOptimizer, "iter_optimize_folder", lambda self, folder: ["ok"])

    run_id = run_pipeline(str(cfg_path))
    with db.SessionLocal() as s:
        wf = s.get(db.models.Workflow, run_id)
        assert wf and os.path.basename(wf.output_dir) == "out"
        params = json.loads(wf.params)
        assert params["order"] == ["scrape_images", "optimize"]

    calls.clear()
    replay_workflow(run_id)
    assert calls and calls[0][1].endswith("out")
