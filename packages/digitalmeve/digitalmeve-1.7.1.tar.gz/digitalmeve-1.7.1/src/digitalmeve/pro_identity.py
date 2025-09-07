from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["ProIdentity"]


@dataclass
class ProIdentity:
    """Identité professionnelle minimale (extensible)."""

    company: str
    contact: Optional[str] = None
