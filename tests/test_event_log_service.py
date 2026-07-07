import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from smartmed.services.event_log_service import (
    append_log_entry,
    export_log_to_file,
    format_log_as_text,
    get_log_entry_timestamp,
    prune_old_entries,
)


class EventLogServiceTests(unittest.TestCase):
    def test_append_log_entry_uses_timestamp_key(self):
        entries = []
        now = datetime(2026, 4, 20, 8, 30, 0)

        entry = append_log_entry(entries, "Testeintrag", now=now)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entry["timestamp"], "20.04.2026 08:30:00")
        self.assertEqual(entry["text"], "Testeintrag")

    def test_get_log_entry_timestamp_reads_new_format(self):
        entry = {
            "timestamp": "20.04.2026 08:30:00",
            "text": "Neu",
        }

        self.assertEqual(get_log_entry_timestamp(entry), "20.04.2026 08:30:00")

    def test_get_log_entry_timestamp_reads_legacy_format(self):
        entry = {
            "zeit": "19.04.2026 07:15:00",
            "text": "Alt",
        }

        self.assertEqual(get_log_entry_timestamp(entry), "19.04.2026 07:15:00")

    def test_prune_old_entries_removes_entries_older_than_cutoff(self):
        now = datetime(2026, 4, 20, 8, 0, 0)
        entries = [
            {"timestamp": "01.03.2026 08:00:00", "text": "Zu alt"},
            {"timestamp": "19.04.2026 08:00:00", "text": "Aktuell"},
        ]

        result = prune_old_entries(entries, days=30, now=now)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], "Aktuell")

    def test_prune_old_entries_keeps_entries_with_unparseable_timestamp(self):
        now = datetime(2026, 4, 20, 8, 0, 0)
        entries = [{"text": "Ohne Zeitstempel"}]

        result = prune_old_entries(entries, days=30, now=now)

        self.assertEqual(result, entries)

    def test_format_log_as_text_contains_header_and_entries(self):
        now = datetime(2026, 4, 20, 8, 0, 0)
        entries = [{"timestamp": "19.04.2026 08:00:00", "text": "Einnahme bestätigt"}]

        text = format_log_as_text(entries, patient_name="Erika Musterfrau", exportiert_am=now)

        self.assertIn("SmartMediSpender", text)
        self.assertIn("Erika Musterfrau", text)
        self.assertIn("19.04.2026 08:00:00 - Einnahme bestätigt", text)

    def test_format_log_as_text_handles_empty_log(self):
        text = format_log_as_text([], patient_name="Erika")

        self.assertIn("Keine Log-Einträge vorhanden.", text)

    def test_export_log_to_file_writes_readable_file(self):
        entries = [{"timestamp": "19.04.2026 08:00:00", "text": "Test"}]

        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp)
            pfad = export_log_to_file(
                entries, export_dir, patient_name="Erika",
                now=datetime(2026, 4, 20, 8, 0, 0),
            )

            self.assertTrue(pfad.exists())
            inhalt = pfad.read_text(encoding="utf-8")
            self.assertIn("Test", inhalt)
            self.assertIn("Erika", inhalt)


if __name__ == "__main__":
    unittest.main()