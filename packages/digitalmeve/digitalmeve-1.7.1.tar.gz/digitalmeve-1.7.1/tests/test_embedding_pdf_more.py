from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import pikepdf

from digitalmeve.embedding_pdf import embed_proof_pdf, extract_proof_pdf


def _proof_for(name: str) -> dict:
    issued = (
        datetime(2025, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    )
    return {
        "meve_version": "1.0",
        "issuer": "Personal",
        "issued_at": issued,
        "timestamp": issued,
        "metadata": {},
        "subject": {"filename": name, "size": 0, "hash_sha256": "00" * 32},
        "hash": "00" * 32,
        "preview_b64": "",
    }


def test_pdf_embed_with_out_path_and_extract(tmp_path: Path):
    # PDF minimal vide
    src = tmp_path / "doc.pdf"
    with pikepdf.Pdf.new() as pdf:
        pdf.save(str(src))

    out = tmp_path / "doc.meve.pdf"
    proof = _proof_for("doc.pdf")

    # 1) embed vers un chemin explicite
    out_path = embed_proof_pdf(src, proof, out_path=out)
    assert out_path == out
    assert out.exists()

    # 2) extract et vérifications basiques
    extracted = extract_proof_pdf(out)
    assert isinstance(extracted, dict)
    assert extracted.get("issuer") == "Personal"
    assert extracted.get("subject", {}).get("filename") == "doc.pdf"
