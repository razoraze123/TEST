import os
import subprocess
from optimizer import ImageOptimizer


def test_optimize_png(monkeypatch, tmp_path):
    recorded = {}
    def fake_run(cmd, capture_output=True, text=True):
        recorded['cmd'] = cmd
        class R:
            returncode = 0
            stderr = ''
        return R()
    monkeypatch.setattr(subprocess, 'run', fake_run)

    file = tmp_path / 'img.png'
    file.write_bytes(b'data')
    opt = ImageOptimizer('optipng', 'cwebp')
    log = opt.optimize_file(str(file))
    assert recorded['cmd'] == ['optipng', '-o7', str(file)]
    assert 'PNG optimisé' in log


def test_optimize_webp(monkeypatch, tmp_path):
    cmds = []
    def fake_run(cmd, capture_output=True, text=True):
        cmds.append(cmd)
        class R:
            returncode = 0
            stderr = ''
        return R()
    monkeypatch.setattr(subprocess, 'run', fake_run)
    replaced = []
    monkeypatch.setattr(os, 'replace', lambda a, b: replaced.append((a, b)))

    file = tmp_path / 'img.webp'
    file.write_bytes(b'')
    opt = ImageOptimizer('optipng', 'cwebp')
    log = opt.optimize_file(str(file))
    tmpfile = str(file) + '.tmp.webp'
    assert cmds[0] == ['cwebp', '-lossless', str(file), '-o', tmpfile]
    assert replaced and replaced[0] == (tmpfile, str(file))
    assert 'WebP optimisé' in log


def test_optimize_unsupported(tmp_path):
    file = tmp_path / 'img.gif'
    file.write_bytes(b'')
    opt = ImageOptimizer('optipng', 'cwebp')
    log = opt.optimize_file(str(file))
    assert 'Format non supporté' in log
