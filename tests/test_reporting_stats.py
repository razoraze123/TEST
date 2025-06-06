import db
import storage
import reporting


def _setup(tmp_path):
    path = tmp_path / "r.db"
    db.init_engine(path)
    storage.init_db()


def test_counts(tmp_path):
    _setup(tmp_path)
    storage.upsert_product("1", "A", "S1", "10", "d")
    storage.record_competitor("1", "t", "u", "/f", "OK")
    storage.record_competitor("1", "t", "u", "/f2", "Erreur")

    assert reporting.total_articles() == 1
    errs = reporting.error_counts()
    assert len(errs) == 1
    assert errs[0].status == "Erreur"
    assert errs[0].count == 1


def test_progress_batches(tmp_path):
    _setup(tmp_path)
    storage.upsert_product("1", "A", "S1", "10", "d")
    for i in range(10):
        storage.record_competitor("1", f"t{i}", "u", f"/f{i}", "OK")

    batches = reporting.progress_by_batch(batch_size=4)
    assert batches == [(1, 4), (2, 4), (3, 2)]
