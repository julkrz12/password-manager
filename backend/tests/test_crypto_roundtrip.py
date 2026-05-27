import os
from backend.app.core.crypto import derive_key, encrypt_secret, decrypt_secret, password_fingerprint


def test_encrypt_decrypt_roundtrip():
    salt = os.urandom(16)
    key = derive_key('VeryStrongMasterPassword!', salt)
    payload = {'account_username':'u', 'password':'p', 'notes':'n'}
    ct, nonce = encrypt_secret(key, payload)
    out = decrypt_secret(key, ct, nonce)
    assert out == payload


def test_fingerprint_deterministic():
    salt = os.urandom(16)
    key = derive_key('VeryStrongMasterPassword!', salt)
    a = password_fingerprint(key, 'pass')
    b = password_fingerprint(key, 'pass')
    c = password_fingerprint(key, 'pass2')
    assert a == b
    assert a != c
