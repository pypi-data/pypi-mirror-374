# tests/test_embed_png.py
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from digitalmeve.embedding_png import embed_proof_png, extract_proof_png


def test_png_embed_and_extract(tmp_path: Path) -> None:
    # 1) créer un petit PNG (2x2)
    src_png = tmp_path / "sample.png"
    Image.new("RGB", (2, 2), (255, 0, 0)).save(src_png)
    assert src_png.exists()

    # 2) preuve minimale à embarquer
    issued = (
        datetime(2025, 1, 1, tzinfo=timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    proof = {
        "meve_version": "1.0",
        "issued_at": issued,
        "timestamp": issued,  # compat
        "issuer": "Personal",
        "status": "Personal",
        "certified": "self",
        "hash_sha256": "00" * 32,
        "subject": {
            "filename": "sample.png",
            "size": src_png.stat().st_size,
            "hash_sha256": "00" * 32,
        },
    }

    # 3) embarquer puis extraire
    out_png = tmp_path / "sample.embedded.png"
    res = embed_proof_png(src_png, proof, out_png)
    assert res.exists()

    extracted = extract_proof_png(out_png)
    assert extracted is not None
    assert extracted.get("issuer") == "Personal"
    assert extracted.get("subject", {}).get("filename") == "sample.png"
