# flake8: noqa
from __future__ import annotations

import json
from pathlib import Path

import pytest

from digitalmeve.core import generate_meve, verify_meve


def _write_sample(tmp_path: Path, name: str = "sample.txt") -> Path:
    f = tmp_path / name
    f.write_text("hello world")
    return f


def test_generate_and_verify_valid(tmp_path: Path) -> None:
    infile = _write_sample(tmp_path)
    outdir = tmp_path / "out"
    outdir.mkdir()

    meve = generate_meve(infile, outdir=outdir, issuer="DigitalMeve Test Suite")

    # Vérifie la structure du dict
    assert isinstance(meve, dict)

    # Vérifie que le fichier a bien été écrit
    out_file = outdir / f"{infile.name}.meve.json"
    assert out_file.exists(), "outfile should be created"

    # Relecture + vérification
    ok, info = verify_meve(out_file, expected_issuer="DigitalMeve Test Suite")
    assert ok is True
    assert isinstance(info, dict)
    assert info["subject"]["filename"] == infile.name


def test_generate_meve_in_memory(tmp_path: Path) -> None:
    infile = _write_sample(tmp_path)
    meve = generate_meve(infile)
    ok, info = verify_meve(meve)
    assert ok is True
    assert info["subject"]["filename"] == infile.name


def test_verify_meve_rejects_invalid(tmp_path: Path) -> None:
    wrong = {"issuer": "X", "meve_version": "1.0", "subject": {}}
    ok, info = verify_meve(wrong, expected_issuer="DigitalMeve Test Suite")
    assert ok is False
    assert isinstance(info, dict)
    assert "Missing" in info.get("error", "") or "issuer mismatch" in info.get(
        "error", ""
    )
