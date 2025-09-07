from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping, Optional, Union

__all__ = [
    "format_identity",
    "load_json",
    "pretty_print",
]


def load_json(path: Union[str, Path]) -> Any:
    """
    Charge un fichier JSON (UTF-8) et renvoie l'objet Python.
    Laisse remonter les exceptions (FileNotFoundError, JSONDecodeError)
    pour que les tests/CLI les gèrent proprement.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def pretty_print(data: Any) -> None:
    """
    Affiche un objet Python en JSON lisible (UTF-8, indenté).
    Utilisé par la commande `inspect` du CLI.
    """
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    print()  # flush avec un saut de ligne


def format_identity(value: Optional[Union[str, Path, Mapping]]) -> str:
    """
    - str  -> retourne la string telle quelle
    - Path -> retourne le nom du fichier (sans extension) en MAJUSCULES
    - dict -> si clé 'identity' présente, on la renvoie
    - autres / None -> lève AttributeError
    """
    if isinstance(value, Path):
        return value.stem.upper()
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping) and "identity" in value:
        return str(value["identity"])
    raise AttributeError("invalid identity")
