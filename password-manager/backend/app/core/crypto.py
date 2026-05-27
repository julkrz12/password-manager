import os
import json
import hmac
import hashlib
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type


# Argon2id: parametry minimalne wg OWASP (możesz podnieść memory_cost w zależności od sprzętu)
# Uwaga: do weryfikacji hasła używamy PasswordHasher (argon2-cffi), a do klucza — hash_secret_raw.
ph = PasswordHasher(
    time_cost=2,
    memory_cost=19456,  # KiB ≈ 19 MiB
    parallelism=1,
    hash_len=32,
    salt_len=16,
)


def hash_master_password(master_password: str) -> str:
    return ph.hash(master_password)


def verify_master_password(stored_hash: str, master_password: str) -> bool:
    try:
        ph.verify(stored_hash, master_password)
        return True
    except Exception:
        return False


def derive_key(master_password: str, kdf_salt: bytes) -> bytes:
    # 32 bajty -> AES-256
    return hash_secret_raw(
        secret=master_password.encode('utf-8'),
        salt=kdf_salt,
        time_cost=2,
        memory_cost=19456,
        parallelism=1,
        hash_len=32,
        type=Type.ID,
    )


def encrypt_secret(key: bytes, payload: dict) -> tuple[bytes, bytes]:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce
    plaintext = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return ciphertext, nonce


def decrypt_secret(key: bytes, ciphertext: bytes, nonce: bytes) -> dict:
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode('utf-8'))


def password_fingerprint(key: bytes, password: str) -> bytes:
    # HMAC-SHA256(key, password) — porównywalne, ale nieodwracalne
    return hmac.new(key, password.encode('utf-8'), hashlib.sha256).digest()
