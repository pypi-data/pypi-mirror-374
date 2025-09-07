from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OfficialIdentity:
    """Identité 'officielle'/institutionnelle minimale (extensible)."""

    authority: str
    contact: Optional[str] = None
