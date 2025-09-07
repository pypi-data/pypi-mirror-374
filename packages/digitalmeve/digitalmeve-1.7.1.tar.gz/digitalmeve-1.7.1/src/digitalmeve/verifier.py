from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

# --- Imports facultatifs pour l'extraction embarquée (ne cassent pas si absents)
try:  # PDF
    from .embedding_pdf import extract_proof_pdf  # type: ignore
except Exception:  # pragma: no cover
    extract_proof_pdf = None  # type: ignore

try:  # PNG
    from .embedding_png import extract_proof_png  # type: ignore
except Exception:  # pragma: no cover
    extract_proof_png = None  # type: ignore


def verify_identity(identity: str | Path | None) -> bool:
    """
    Vérification minimale de l'identité utilisée par les tests.
    Chaîne vide -> False ; toute chaîne non vide -> True.
    """
    if identity is None:
        return False
    return str(identity).strip() != ""


def verify_file(
    path: str | Path,
    *,
    expected_issuer: Optional[str] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Vérifie un fichier contenant une preuve .meve :
      - JSON (sidecar) : *.meve.json ou *.json
      - PDF embarqué   : *.pdf ou *.meve.pdf
      - PNG embarqué   : *.png ou *.meve.png

    Retourne (ok, info|{"error": "..."}).
    """
    p = Path(path)
    if not p.exists():
        return False, {"error": "File not found"}

    name = p.name.lower()
    suf = p.suffix.lower()

    # 1) Sidecar JSON
    if suf == ".json" or name.endswith(".meve.json"):
        proof = _as_dict(p)
        return verify_meve(proof, expected_issuer=expected_issuer)

    # 2) PDF embarqué
    if suf == ".pdf" or name.endswith(".meve.pdf"):
        if extract_proof_pdf is None:
            return False, {"error": "PDF extraction unavailable"}
        try:
            proof = extract_proof_pdf(p)  # type: ignore[misc]
        except Exception as e:  # pragma: no cover
            return False, {"error": f"PDF extraction failed: {e}"}
        return verify_meve(proof, expected_issuer=expected_issuer)

    # 3) PNG embarqué
    if suf == ".png" or name.endswith(".meve.png"):
        if extract_proof_png is None:
            return False, {"error": "PNG extraction unavailable"}
        try:
            proof = extract_proof_png(p)  # type: ignore[misc]
        except Exception as e:  # pragma: no cover
            return False, {"error": f"PNG extraction failed: {e}"}
        return verify_meve(proof, expected_issuer=expected_issuer)

    return False, {"error": f"Unsupported file type: {suf}"}


def _as_dict(proof: Any) -> Optional[Dict[str, Any]]:
    """
    Accepte :
      - un dict (retourné tel quel)
      - une chaîne JSON
      - un chemin de fichier (Path ou str) pointant vers un JSON
    Retourne un dict ou None si l'entrée n'est pas exploitable.
    """
    if isinstance(proof, dict):
        return proof

    if isinstance(proof, (str, Path)):
        p = Path(proof)
        if p.exists() and p.is_file():
            try:
                text = p.read_text(encoding="utf-8")
                return json.loads(text)
            except Exception:
                return None
        try:
            return json.loads(str(proof))
        except Exception:
            return None

    if isinstance(proof, (bytes, bytearray)):
        try:
            return json.loads(proof.decode("utf-8"))
        except Exception:
            return None

    return None


def verify_meve(
    proof: Any,
    *,
    expected_issuer: Optional[str] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Valide la structure d'une preuve .meve.

    Retourne :
      - (True, <dict de la preuve>) si valide
      - (False, {"error": "<raison>"}) sinon
    """
    obj = _as_dict(proof)
    if not isinstance(obj, dict):
        return False, {"error": "Invalid proof"}

    required: Iterable[str] = (
        "meve_version",
        "issuer",
        "timestamp",
        "subject",
        "hash",
    )
    missing = [k for k in required if k not in obj]
    if missing:
        return False, {"error": "Missing required keys"}  # noqa: E501

    subject = obj.get("subject")
    if not isinstance(subject, dict):
        return False, {"error": "Missing required keys"}  # noqa: E501

    subj_required: Iterable[str] = ("filename", "size", "hash_sha256")
    if any(k not in subject for k in subj_required):
        return False, {"error": "Missing required keys"}  # noqa: E501

    if expected_issuer is not None and obj.get("issuer") != expected_issuer:
        return False, {"error": "Issuer mismatch"}  # noqa: E501

    if obj.get("hash") != subject.get("hash_sha256"):
        return False, {"error": "Hash mismatch"}  # noqa: E501

    try:
        # placeholder de validation de schéma (futur)
        # schema_validate(obj)
        pass
    except Exception as e:  # pragma: no cover
        msg = f"Schema validation failed: {e}"
        return False, {"error": msg}  # noqa: E501

    return True, obj
