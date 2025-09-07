import json
from pathlib import Path


def _load_schema_path() -> Path:
    """Retourne le chemin du schéma (schemas/meve-1.schema.json)."""
    repo_root = Path(__file__).resolve().parents[1]
    p = repo_root / "schemas" / "meve-1.schema.json"
    if not p.exists():
        raise FileNotFoundError(
            f"Schéma introuvable: {p}. Place le fichier dans schemas/meve-1.schema.json"
        )
    if p.stat().st_size == 0:
        raise ValueError(f"Schéma vide: {p}")
    return p


def test_schema_loadable():
    """Le schéma doit être un JSON valide non vide."""
    path = _load_schema_path()
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert data.get("$schema", "").startswith("https://json-schema.org/")
