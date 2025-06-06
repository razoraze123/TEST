from __future__ import annotations

import json
import os
from datetime import datetime
import tomllib

import db
from db.models import Log, Workflow
import config
from scraper_core import ScraperCore
from optimizer import ImageOptimizer
import storage
from pathlib import Path


def _log(session, wf_id: int, message: str) -> None:
    session.add(Log(created=datetime.utcnow(), level="INFO", message=f"[{wf_id}] {message}"))
    session.commit()


def _execute(cfg: dict, wf_id: int) -> None:
    base_dir = cfg.get("base_dir", config.BASE_DIR)
    links_file = cfg.get("links_file", config.LINKS_FILE_PATH)
    dest = cfg.get("dest_folder", os.path.join(base_dir, config.ROOT_FOLDER))
    steps = cfg.get("order", [])
    suffix = cfg.get("suffix", "image-produit")
    headless = cfg.get("headless", True)
    pattern = cfg.get("image_name_pattern", config.IMAGE_NAME_PATTERN)

    core = ScraperCore(base_dir=base_dir)

    session = db.SessionLocal()
    for step in steps:
        if step == "scrape_images":
            urls = core.charger_liste_urls(links_file)
            _log(session, wf_id, f"scrape_images -> {dest}")
            core.scrap_images(urls, dest, suffix=suffix, headless=headless)
        elif step == "scrape_variants":
            items = [{"id": i, "url": u} for i, u in core.charger_liens_avec_id(links_file).items()]
            _log(session, wf_id, "scrape_variants")
            core.scrap_images_variantes(
                items,
                config.WP_DOMAIN,
                config.WP_UPLOAD_PATH,
                pattern,
                headless=headless,
            )
        elif step == "optimize":
            _log(session, wf_id, f"optimize {dest}")
            optimizer = ImageOptimizer(config.OPTIPNG_PATH, config.CWEBP_PATH)
            for msg in optimizer.iter_optimize_folder(dest):
                _log(session, wf_id, msg)
        else:
            _log(session, wf_id, f"Unknown step: {step}")
    session.close()
    with db.SessionLocal() as s:
        wf = s.get(Workflow, wf_id)
        if wf:
            wf.output_dir = dest
            s.commit()


def run_pipeline(config_path: str) -> int:
    """Run a workflow described in *config_path* and return its id."""
    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)
    base_dir = cfg.get("base_dir", config.BASE_DIR)
    db.init_engine(Path(storage.db_path(base_dir)))
    storage.init_db()
    with db.SessionLocal() as session:
        wf = Workflow(params=json.dumps(cfg), output_dir="")
        session.add(wf)
        session.commit()
        wf_id = wf.id
    _execute(cfg, wf_id)
    return wf_id


def replay_workflow(task_id: int) -> None:
    """Replay a previous workflow using stored parameters."""
    with db.SessionLocal() as session:
        wf = session.get(Workflow, task_id)
        if not wf:
            raise ValueError("workflow not found")
        cfg = json.loads(wf.params)
    _execute(cfg, task_id)
