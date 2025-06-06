import os
from pathlib import Path

import db
import storage


def test_upsert_and_search(tmp_path):
    path = tmp_path / "test.db"
    db.init_engine(path)
    storage.init_db()

    storage.upsert_product("1", "Test Shoe", "SKU1", "10", "folder")
    storage.upsert_variant("1", "SKU1-V", "Variant", "9")
    storage.record_competitor("1", "title", "http://x", "/f", "ok")

    results = storage.search_products("Test")
    assert results == [("1", "Test Shoe", "SKU1", "10")]
