import unittest

from smartmed.services.admin_pin_service import (
    build_admin_pin_update,
    has_admin_pin,
    verify_admin_pin,
)
from smartmed.services.security_service import is_hashed


class AdminPinServiceTests(unittest.TestCase):
    def test_has_admin_pin_recognizes_non_empty_pin(self):
        self.assertTrue(has_admin_pin("1234"))
        self.assertFalse(has_admin_pin("   "))
        self.assertFalse(has_admin_pin(""))

    def test_build_admin_pin_update_accepts_empty_inputs_as_disable(self):
        result = build_admin_pin_update("", "")

        self.assertTrue(result["ok"])
        self.assertEqual(result["admin_pin"], "")

    def test_build_admin_pin_update_rejects_mismatch(self):
        result = build_admin_pin_update("1234", "9999")

        self.assertFalse(result["ok"])
        self.assertIsNone(result["admin_pin"])

    def test_verify_admin_pin_accepts_matching_value(self):
        result = verify_admin_pin("1234", "1234")

        self.assertTrue(result["ok"])
        self.assertEqual(result["message"], "")

    def test_build_admin_pin_update_stores_hashed_value(self):
        result = build_admin_pin_update("1234", "1234")

        self.assertTrue(result["ok"])
        self.assertTrue(is_hashed(result["admin_pin"]))
        self.assertNotEqual(result["admin_pin"], "1234")

    def test_verify_admin_pin_accepts_hashed_value(self):
        stored = build_admin_pin_update("1234", "1234")["admin_pin"]

        result = verify_admin_pin(stored, "1234")

        self.assertTrue(result["ok"])
        self.assertFalse(result["needs_rehash"])

    def test_verify_admin_pin_flags_legacy_plaintext_for_rehash(self):
        result = verify_admin_pin("1234", "1234")

        self.assertTrue(result["ok"])
        self.assertTrue(result["needs_rehash"])

    def test_verify_admin_pin_rejects_wrong_value(self):
        stored = build_admin_pin_update("1234", "1234")["admin_pin"]

        result = verify_admin_pin(stored, "9999")

        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()