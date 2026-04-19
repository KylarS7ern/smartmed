import unittest
from datetime import datetime

from smartmed.services.event_log_service import (
    append_log_entry,
    get_log_entry_timestamp,
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


if __name__ == "__main__":
    unittest.main()