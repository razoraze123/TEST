import os
import json
import time
import subprocess
import multiprocessing
from pathlib import Path

import requests
import pytest

import app


def test_run_process_success(monkeypatch):
    captured = {}
    def fake_run(cmd, input=None, capture_output=True, text=True, check=False):
        captured['cmd'] = cmd
        return type('R', (), {'stdout': 'OUT', 'returncode': 0})()
    monkeypatch.setattr(subprocess, 'run', fake_run)
    out, code = app._run_process(['echo', 'hi'])
    assert out == 'OUT'
    assert code == 0
    assert captured['cmd'] == ['echo', 'hi']


def test_run_process_exception(monkeypatch):
    def fake_run(cmd, input=None, capture_output=True, text=True, check=False):
        raise FileNotFoundError('boom')
    monkeypatch.setattr(subprocess, 'run', fake_run)
    out, code = app._run_process(['missing'])
    assert code == 1
    assert 'Error running' in out


@pytest.mark.parametrize('call,expected', [
    (lambda: app.run_node_script('test.js'), ['node', 'js_modules/test.js']),
    (lambda: app.run_go_binary('bin', ['a']), ['go_modules/bin', 'a']),
    (lambda: app.run_rust_binary('bin', ['a']), ['rust_modules/bin', 'a']),
    (lambda: app.run_c_binary('bin', ['a']), ['c_modules/bin', 'a']),
])
def test_run_commands(monkeypatch, call, expected):
    captured = {}
    def fake_run(cmd, input=None, capture_output=True, text=True, check=False):
        captured['cmd'] = cmd
        return type('R', (), {'stdout': 'ok', 'returncode': 3})()
    monkeypatch.setattr(subprocess, 'run', fake_run)
    out, code = call()
    assert code == 3
    assert captured['cmd'] == expected


def test_run_with_tempfile(monkeypatch):
    created = {}
    def fake_run_process(cmd, input_data=""):
        created['cmd'] = cmd
        Path(cmd[1]).write_text('TMPDATA')
        return 'PROC', 0
    monkeypatch.setattr(app, '_run_process', fake_run_process)
    removed = []
    monkeypatch.setattr(os, 'remove', lambda p: removed.append(p))
    out, code = app.run_with_tempfile('bin', ['x'])
    assert code == 0
    assert 'TMPDATA' in out
    assert created['cmd'][0] == 'bin'
    assert removed and str(removed[0]) == created['cmd'][1]


# ---------------- Flask server tests -----------------

def _run_server(json_path, fiches_dir, port):
    import flask_server
    flask_server.CHEMIN_JSON = json_path
    flask_server.DOSSIER_FICHES = fiches_dir
    flask_server.app.run(port=port, use_reloader=False)


def test_flask_server_endpoints(tmp_path):
    json_file = tmp_path / 'produits.json'
    json_file.write_text(json.dumps([{'id': '1', 'nom': 'Test'}]))
    fiches = tmp_path / 'fiches'
    port = 5050
    proc = multiprocessing.Process(target=_run_server, args=(str(json_file), str(fiches), port))
    proc.start()
    try:
        for _ in range(20):
            try:
                requests.get(f'http://localhost:{port}/get-produits', timeout=1)
                break
            except Exception:
                time.sleep(0.1)
        r = requests.get(f'http://localhost:{port}/get-produits?batch=1')
        assert r.status_code == 200
        assert r.json()['produits'][0]['id'] == '1'

        r = requests.post(f'http://localhost:{port}/upload-fiche', json={'id': '1', 'nom': 'Test', 'html': '<p>x</p>'})
        assert r.status_code == 200
        assert (fiches / '1-test.txt').exists()

        r = requests.get(f'http://localhost:{port}/list-fiches')
        assert '1-test.txt' in r.json()

        r = requests.post(f'http://localhost:{port}/upload-fiche', json={'id': '2'})
        assert r.status_code == 400
    finally:
        proc.terminate()
        proc.join()
