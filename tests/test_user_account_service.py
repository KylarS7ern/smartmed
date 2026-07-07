import unittest

from smartmed.services.user_account_service import (
    create_user_result,
    user_requires_password,
    verify_user_password,
)
from smartmed.services.security_service import is_hashed


class UserAccountServiceTests(unittest.TestCase):
    def test_create_user_result_hashes_non_empty_password(self):
        result = create_user_result(
            users={},
            username_text="Anna",
            password_text="geheim",
            settings={},
        )

        self.assertTrue(result["ok"])
        self.assertTrue(is_hashed(result["user_data"]["password"]))

    def test_create_user_result_keeps_empty_password_empty(self):
        result = create_user_result(
            users={},
            username_text="Anna",
            password_text="",
            settings={},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["user_data"]["password"], "")

    def test_user_requires_password_false_for_empty_password(self):
        users = {"Anna": {"password": ""}}

        self.assertFalse(user_requires_password(users, "Anna"))

    def test_verify_user_password_accepts_hashed_password(self):
        result = create_user_result(
            users={},
            username_text="Anna",
            password_text="geheim",
            settings={},
        )
        users = {"Anna": result["user_data"]}

        verify_result = verify_user_password(users, "Anna", "geheim")

        self.assertTrue(verify_result["ok"])
        self.assertFalse(verify_result["needs_rehash"])

    def test_verify_user_password_flags_legacy_plaintext_for_rehash(self):
        users = {"Anna": {"password": "geheim"}}

        result = verify_user_password(users, "Anna", "geheim")

        self.assertTrue(result["ok"])
        self.assertTrue(result["needs_rehash"])

    def test_verify_user_password_rejects_wrong_password(self):
        result = create_user_result(
            users={},
            username_text="Anna",
            password_text="geheim",
            settings={},
        )
        users = {"Anna": result["user_data"]}

        verify_result = verify_user_password(users, "Anna", "falsch")

        self.assertFalse(verify_result["ok"])


if __name__ == "__main__":
    unittest.main()
