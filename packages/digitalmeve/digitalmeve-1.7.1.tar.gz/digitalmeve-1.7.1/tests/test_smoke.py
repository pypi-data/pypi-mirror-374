from __future__ import annotations

import digitalmeve


def test_package_smoke() -> None:
    # évite F401 "imported but unused" + vérifie un attribut
    assert hasattr(digitalmeve, "__version__")
