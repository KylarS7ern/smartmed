import unittest

from smartmed.services.user_account_service import (
    build_password_change_result,
    build_password_reset_result,
    create_user_result,
    delete_user_result,
    user_requires_password,
    verify_user_password,
)
from smartmed.services.security_service import hash_secret, is_hashed


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


    def test_delete_user_result_succeeds_for_non_last_user(self):
        users = {"Anna": {}, "Bert": {}}

        result = delete_user_result(users=users, username="Bert", current_user="Anna")

        self.assertTrue(result["ok"])
        self.assertFalse(result["clears_current_user"])

    def test_delete_user_result_flags_deleting_the_current_user(self):
        users = {"Anna": {}, "Bert": {}}

        result = delete_user_result(users=users, username="Anna", current_user="Anna")

        self.assertTrue(result["ok"])
        self.assertTrue(result["clears_current_user"])

    def test_delete_user_result_rejects_last_remaining_user(self):
        users = {"Anna": {}}

        result = delete_user_result(users=users, username="Anna", current_user="Anna")

        self.assertFalse(result["ok"])
        self.assertIn("letzte", result["message"].lower())

    def test_delete_user_result_rejects_unknown_username(self):
        users = {"Anna": {}, "Bert": {}}

        result = delete_user_result(users=users, username="Carla", current_user="Anna")

        self.assertFalse(result["ok"])

    def test_password_change_requires_correct_current_password(self):
        result = build_password_change_result(
            current_password_stored=hash_secret("alt"),
            current_password_input="falsch",
            new_password_text="neu123",
            new_password_confirm_text="neu123",
        )

        self.assertFalse(result["ok"])
        self.assertIn("Aktuelles Passwort", result["message"])

    def test_password_change_rejects_mismatched_new_passwords(self):
        result = build_password_change_result(
            current_password_stored="",
            current_password_input="",
            new_password_text="neu123",
            new_password_confirm_text="anders",
        )

        self.assertFalse(result["ok"])
        self.assertIn("stimmen nicht überein", result["message"])

    def test_password_change_succeeds_and_hashes_new_password(self):
        result = build_password_change_result(
            current_password_stored=hash_secret("alt"),
            current_password_input="alt",
            new_password_text="neu123",
            new_password_confirm_text="neu123",
        )

        self.assertTrue(result["ok"])
        self.assertTrue(is_hashed(result["password"]))

    def test_password_change_with_empty_new_password_removes_protection(self):
        result = build_password_change_result(
            current_password_stored=hash_secret("alt"),
            current_password_input="alt",
            new_password_text="",
            new_password_confirm_text="",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["password"], "")

    def test_password_change_skips_current_password_check_when_none_set(self):
        result = build_password_change_result(
            current_password_stored="",
            current_password_input="irrelevant",
            new_password_text="neu123",
            new_password_confirm_text="neu123",
        )

        self.assertTrue(result["ok"])

    def test_password_reset_result_succeeds_for_existing_user(self):
        users = {"Anna": {"password": hash_secret("geheim")}}

        result = build_password_reset_result(users=users, username="Anna")

        self.assertTrue(result["ok"])

    def test_password_reset_result_rejects_unknown_username(self):
        users = {"Anna": {}}

        result = build_password_reset_result(users=users, username="Carla")

        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
