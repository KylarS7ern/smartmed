import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from smartmed.services.storage_service import load_json_data, save_json_data


class StorageServiceTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_file = Path(tmp) / "data.json"
            data = {"users": {"Standard": {"name": "Erika"}}}

            ok = save_json_data(data_file, data)

            self.assertTrue(ok)
            self.assertEqual(load_json_data(data_file), data)

    def test_load_missing_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_file = Path(tmp) / "does_not_exist.json"

            self.assertEqual(load_json_data(data_file), {})

    def test_save_does_not_leave_temp_files_behind(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_file = Path(tmp) / "data.json"

            save_json_data(data_file, {"a": 1})

            self.assertEqual(list(Path(tmp).iterdir()), [data_file])

    def test_save_keeps_old_file_intact_if_interrupted_mid_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_file = Path(tmp) / "data.json"
            save_json_data(data_file, {"version": "old"})

            with patch(
                "smartmed.services.storage_service.json.dump",
                side_effect=OSError("stromausfall"),
            ):
                ok = save_json_data(data_file, {"version": "new"})

            self.assertFalse(ok)
            self.assertEqual(load_json_data(data_file), {"version": "old"})
            self.assertEqual(list(Path(tmp).iterdir()), [data_file])


if __name__ == "__main__":
    unittest.main()
