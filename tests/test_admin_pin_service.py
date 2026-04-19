import unittest

from smartmed.services.admin_pin_service import (
    build_admin_pin_update,
    has_admin_pin,
    verify_admin_pin,
)


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


if __name__ == "__main__":
    unittest.main()