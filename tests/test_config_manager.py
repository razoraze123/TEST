import tomllib
import config_manager


def test_load_creates_missing_file(tmp_path, capsys):
    cfg_path = tmp_path / "cfg.toml"
    cfg = config_manager.load(str(cfg_path))
    assert cfg_path.exists()
    data = tomllib.loads(cfg_path.read_text())
    assert data["BASE_DIR"] == config_manager.DEFAULTS["BASE_DIR"]
    captured = capsys.readouterr().out
    assert "Default configuration written" in captured


def test_load_rewrites_invalid_file(tmp_path, capsys):
    cfg_path = tmp_path / "cfg.toml"
    cfg_path.write_text("invalid]")
    cfg = config_manager.load(str(cfg_path))
    data = tomllib.loads(cfg_path.read_text())
    assert cfg == config_manager.DEFAULTS
    assert data["ROOT_FOLDER"] == config_manager.DEFAULTS["ROOT_FOLDER"]
    captured = capsys.readouterr().out
    assert "Default configuration written" in captured
