import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from smartmed.services.backup_service import (
    export_data_to_file,
    list_backup_files,
    load_backup_file,
)


class BackupServiceTests(unittest.TestCase):
    def test_export_data_to_file_writes_readable_json(self):
        data = {"users": {"Anna": {}}, "admin_pin": "", "current_user": "Anna"}

        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp)
            pfad = export_data_to_file(
                data, export_dir, now=datetime(2026, 4, 20, 8, 0, 0)
            )

            self.assertTrue(pfad.exists())
            self.assertIn("smartmed_backup_2026-04-20", pfad.name)

            geladen = load_backup_file(pfad)
            self.assertEqual(geladen, data)

    def test_list_backup_files_returns_newest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp)
            export_data_to_file({"users": {}}, export_dir, now=datetime(2026, 4, 20, 8, 0, 0))
            export_data_to_file({"users": {}}, export_dir, now=datetime(2026, 4, 22, 8, 0, 0))

            dateien = list_backup_files(export_dir)

            self.assertEqual(len(dateien), 2)
            self.assertIn("2026-04-22", dateien[0].name)
            self.assertIn("2026-04-20", dateien[1].name)

    def test_list_backup_files_returns_empty_list_for_missing_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp) / "does_not_exist"

            self.assertEqual(list_backup_files(export_dir), [])

    def test_list_backup_files_ignores_unrelated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp)
            export_data_to_file({"users": {}}, export_dir, now=datetime(2026, 4, 20, 8, 0, 0))
            (export_dir / "log_export_2026-04-20.txt").write_text("kein backup")

            dateien = list_backup_files(export_dir)

            self.assertEqual(len(dateien), 1)

    def test_load_backup_file_rejects_invalid_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            pfad = Path(tmp) / "kaputt.json"
            pfad.write_text('{"nicht_users": true}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_backup_file(pfad)


if __name__ == "__main__":
    unittest.main()
