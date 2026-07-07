import unittest

from smartmed.services.security_service import hash_secret, is_hashed, verify_secret


class SecurityServiceTests(unittest.TestCase):
    def test_hash_secret_produces_hashed_format(self):
        hashed = hash_secret("1234")

        self.assertTrue(is_hashed(hashed))
        self.assertNotEqual(hashed, "1234")

    def test_hash_secret_uses_random_salt(self):
        first = hash_secret("1234")
        second = hash_secret("1234")

        self.assertNotEqual(first, second)

    def test_verify_secret_accepts_correct_hashed_value(self):
        hashed = hash_secret("geheim")

        self.assertTrue(verify_secret(hashed, "geheim"))

    def test_verify_secret_rejects_wrong_value_for_hashed(self):
        hashed = hash_secret("geheim")

        self.assertFalse(verify_secret(hashed, "falsch"))

    def test_verify_secret_supports_legacy_plaintext(self):
        self.assertTrue(verify_secret("altesPasswort", "altesPasswort"))
        self.assertFalse(verify_secret("altesPasswort", "falsch"))

    def test_is_hashed_detects_plaintext(self):
        self.assertFalse(is_hashed("1234"))
        self.assertTrue(is_hashed(hash_secret("1234")))


if __name__ == "__main__":
    unittest.main()
