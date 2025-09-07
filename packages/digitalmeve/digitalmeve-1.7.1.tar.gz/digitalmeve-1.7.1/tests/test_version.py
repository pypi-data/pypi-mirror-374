import digitalmeve


def test_version():
    # Le package doit exposer __version__
    assert hasattr(digitalmeve, "__version__")

    # Accepte la release 1.7.1 (et les variantes -dev si jamais)
    v = digitalmeve.__version__
    assert isinstance(v, str)
    assert v.startswith("1.7.1"), f"unexpected version: {v}"
