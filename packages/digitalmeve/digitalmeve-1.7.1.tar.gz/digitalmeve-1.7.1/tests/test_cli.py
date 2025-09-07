# tests/test_cli.py
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = str(REPO_ROOT / "src")


def run_cli(*args, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run `python -m digitalmeve.cli ...` with PYTHONPATH=src."""
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + (
        os.pathsep + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )
    return subprocess.run(
        [sys.executable, "-m", "digitalmeve.cli", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )


def test_cli_help_ok():
    r = run_cli("--help")
    assert r.returncode == 0
    assert "usage:" in r.stdout.lower()


def test_generate_then_inspect(tmp_path: pathlib.Path):
    # 1) document d'entrée
    doc = tmp_path / "sample.txt"
    doc.write_text("hello world", encoding="utf-8")

    # 2) generate (stdout = JSON de la preuve)
    r_gen = run_cli(
        "generate",
        str(doc),
        "--issuer",
        "test@example.com",
        "--outdir",
        str(tmp_path),
    )
    assert r_gen.returncode == 0, r_gen.stderr
    proof_obj = json.loads(r_gen.stdout)
    assert isinstance(proof_obj, dict)
    assert "issued_at" in proof_obj

    # 3) écrire la preuve si la lib ne l’a pas créée
    proof_path = tmp_path / "sample.txt.meve.json"
    if not proof_path.exists():
        proof_path.write_text(json.dumps(proof_obj), encoding="utf-8")

    # 4) inspect (résumé lisible en JSON)
    r_ins = run_cli("inspect", str(proof_path))
    assert r_ins.returncode == 0, r_ins.stderr
    summary = json.loads(r_ins.stdout)
    assert {"level", "issuer", "hash_prefix"}.issubset(summary.keys())
