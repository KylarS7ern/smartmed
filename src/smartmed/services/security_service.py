import hashlib
import hmac
import os

_ALGORITHM = "pbkdf2"
_HASH_NAME = "sha256"
_ITERATIONS = 200_000
_SALT_BYTES = 16


def hash_secret(value: str) -> str:
    """Hasht einen Klartext-Wert (PIN/Passwort) mit PBKDF2-HMAC-SHA256.

    Format: pbkdf2$<iterationen>$<salt_hex>$<hash_hex>
    """
    salt = os.urandom(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(_HASH_NAME, value.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ALGORITHM}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def is_hashed(stored: str) -> bool:
    """Prüft, ob ein gespeicherter Wert bereits im Hash-Format vorliegt."""
    return stored.startswith(f"{_ALGORITHM}$")


def verify_secret(stored: str, candidate: str) -> bool:
    """Prüft einen Klartext-Kandidaten gegen einen gespeicherten Wert.

    Unterstützt sowohl neu gehashte Werte als auch alte Klartext-Werte
    (Rückwärtskompatibilität mit bestehenden Daten auf dem Pi).
    """
    if not is_hashed(stored):
        return hmac.compare_digest(stored, candidate)

    try:
        _, iterations_str, salt_hex, digest_hex = stored.split("$", 3)
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac(_HASH_NAME, candidate.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)
