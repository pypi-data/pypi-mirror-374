from digitalmeve.verifier import verify_identity


def test_verify_identity_valid():
    assert verify_identity("ABC123")


def test_verify_identity_invalid():
    assert not verify_identity("")
