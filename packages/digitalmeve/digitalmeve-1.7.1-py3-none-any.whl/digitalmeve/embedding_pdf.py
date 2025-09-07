from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import pikepdf

# La clé **doit** être un PdfName ET commencer par "/"
MEVE_DOCINFO_KEY = pikepdf.Name("/MeveProof")


def embed_proof_pdf(
    in_path: Path | str,
    proof: Dict[str, Any],
    out_path: Path | str | None = None,
) -> Path:
    """
    Écrit la preuve JSON minifiée dans le DocInfo du PDF sous /MeveProof,
    puis sauvegarde le PDF (par défaut en <in>.meve.pdf).
    """
    in_path = Path(in_path)
    if out_path is None:
        out_path = in_path.with_suffix(".meve.pdf")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(proof, separators=(",", ":"), ensure_ascii=False)

    with pikepdf.Pdf.open(in_path) as pdf:
        info = pdf.docinfo if pdf.docinfo is not None else pikepdf.Dictionary()
        # ⚠️ clé correcte + valeur typée
        info[MEVE_DOCINFO_KEY] = pikepdf.String(payload)
        pdf.docinfo = info
        pdf.save(str(out_path))

    return out_path


def extract_proof_pdf(in_path: Path | str) -> Optional[Dict[str, Any]]:
    """
    Lit /MeveProof depuis le DocInfo du PDF et renvoie un dict ou None.
    """
    in_path = Path(in_path)
    try:
        with pikepdf.Pdf.open(in_path) as pdf:
            info = pdf.docinfo or {}
            raw = info.get(MEVE_DOCINFO_KEY)
            if not raw:
                # fallback défensif si une autre clé existe par erreur
                raw = info.get(pikepdf.Name("/MeveProof"))
            if not raw:
                return None
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", "ignore")
            return json.loads(str(raw))
    except Exception:
        return None
