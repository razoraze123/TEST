import argparse
import config
from cli import build_parser
import image_pipeline


def test_cli_workflow_invokes_pipeline(monkeypatch, tmp_path):
    cfg = tmp_path / "wf.toml"
    cfg.write_text("order=['scrape_images']\n")
    called = {}
    import cli
    monkeypatch.setattr(cli, "run_pipeline", lambda p: called.setdefault("cfg", p))
    monkeypatch.setattr(cli, "replay_workflow", lambda i: None)

    parser = build_parser()
    args = parser.parse_args(["workflow", str(cfg)])
    args.func(args)
    assert called["cfg"] == str(cfg)
