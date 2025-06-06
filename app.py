"""Run cross-language modules for demonstration purposes."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Tuple


def _run_process(cmd: Iterable[str], *, input_data: str = "") -> Tuple[str, int]:
    """Helper to run *cmd* and return its stdout and return code."""
    try:
        result = subprocess.run(
            list(cmd),
            input=input_data,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # process failed to start
        return f"Error running {cmd}: {exc}", 1
    return result.stdout, result.returncode


# Node.js ---------------------------------------------------------------------

def run_node_script(script: str, input_data: str = "") -> Tuple[str, int]:
    """Run a Node.js script located under ``js_modules``.

    The script should already exist; only ``node`` is invoked here.
    ``input_data`` is piped to the process and the stdout along with the
    return code is returned.
    """
    script_path = Path("js_modules") / script
    return _run_process(["node", str(script_path)], input_data=input_data)


# Go --------------------------------------------------------------------------

def run_go_binary(binary: str, args: Iterable[str] | None = None, *, input_data: str = "") -> Tuple[str, int]:
    """Run a precompiled Go binary from ``go_modules``.

    ``args`` is an optional list of command line arguments passed to the binary.
    ``input_data`` is forwarded to the subprocess via stdin.
    """
    bin_path = Path("go_modules") / binary
    cmd = [str(bin_path)]
    if args:
        cmd.extend(args)
    return _run_process(cmd, input_data=input_data)


# Rust ------------------------------------------------------------------------

def run_rust_binary(binary: str, args: Iterable[str] | None = None, *, input_data: str = "") -> Tuple[str, int]:
    """Run a compiled Rust binary found in ``rust_modules``."""
    bin_path = Path("rust_modules") / binary
    cmd = [str(bin_path)]
    if args:
        cmd.extend(args)
    return _run_process(cmd, input_data=input_data)


# C ---------------------------------------------------------------------------

def run_c_binary(binary: str, args: Iterable[str] | None = None, *, input_data: str = "") -> Tuple[str, int]:
    """Run a compiled C/C++ program stored in ``c_modules``."""
    bin_path = Path("c_modules") / binary
    cmd = [str(bin_path)]
    if args:
        cmd.extend(args)
    return _run_process(cmd, input_data=input_data)


# Temporary file example ------------------------------------------------------

def run_with_tempfile(binary: str, args: Iterable[str] | None = None) -> Tuple[str, int]:
    """Example showing how to use a temporary file with an external binary."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        cmd = [binary, str(tmp_path)]
        if args:
            cmd.extend(args)
        stdout, code = _run_process(cmd)
        if tmp_path.exists():
            stdout += tmp_path.read_text()
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    return stdout, code
