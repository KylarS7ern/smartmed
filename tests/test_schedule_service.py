import unittest
from datetime import datetime

from smartmed.services.schedule_service import (
    berechne_alarm_delay_minuten,
    berechne_naechste_einnahme,
    erstelle_offene_einnahmen,
    finde_faellige_einnahmen,
)


class ScheduleServiceTests(unittest.TestCase):
    def test_finde_faellige_einnahmen_returns_matching_entries_for_current_minute(self):
        jetzt = datetime(2026, 4, 20, 8, 30, 45)
        plan = [
            {"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A"},
            {"tag": "Mo", "zeit": "08:35", "fach": "2", "medikament": "B"},
        ]

        due, normalized_now, minute_key, tag_kurz, zeit_str = finde_faellige_einnahmen(
            plan,
            jetzt=jetzt,
        )

        self.assertEqual(len(due), 1)
        self.assertEqual(normalized_now.second, 0)
        self.assertEqual(minute_key, "2026-04-20 08:30")
        self.assertEqual(tag_kurz, "Mo")
        self.assertEqual(zeit_str, "08:30")

    def test_erstelle_offene_einnahmen_avoids_duplicate_open_entries(self):
        jetzt = datetime(2026, 4, 20, 8, 30, 0)
        due = [{"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 1}]
        existing = [
            {
                "key": ("Mo", "08:30", "1", "A"),
                "bestaetigt": False,
            }
        ]

        neue = erstelle_offene_einnahmen(
            due=due,
            offene_einnahmen=existing,
            jetzt=jetzt,
            delay_min=30,
        )

        self.assertEqual(neue, [])

    def test_berechne_naechste_einnahme_picks_next_future_entry(self):
        jetzt = datetime(2026, 4, 20, 10, 0, 0)
        plan = [
            {"tag": "Mo", "zeit": "09:00", "fach": "1", "medikament": "Alt"},
            {"tag": "Mo", "zeit": "11:00", "fach": "2", "medikament": "Neu"},
            {"tag": "Di", "zeit": "08:00", "fach": "3", "medikament": "Morgen"},
        ]

        entry, dt_next = berechne_naechste_einnahme(plan, jetzt=jetzt)

        self.assertEqual(entry["medikament"], "Neu")
        self.assertEqual(dt_next, datetime(2026, 4, 20, 11, 0, 0))

    def test_berechne_alarm_delay_minuten_falls_back_to_default(self):
        self.assertEqual(berechne_alarm_delay_minuten("abc"), 30)
        self.assertEqual(berechne_alarm_delay_minuten(0), 30)
        self.assertEqual(berechne_alarm_delay_minuten(15), 15)


if __name__ == "__main__":
    unittest.main()