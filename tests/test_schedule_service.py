import unittest
from datetime import date, datetime

from smartmed.services.schedule_service import (
    bereinige_offene_einnahmen,
    berechne_alarm_delay_minuten,
    berechne_naechste_einnahme,
    bestaetige_offene_einnahmen,
    deserialize_offene_einnahmen,
    erstelle_offene_einnahmen,
    finde_faellige_einnahmen,
    ist_eintrag_faellig_am,
    serialize_offene_einnahmen,
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
                "key": ("Mo", "08:30", "1", "A", "2026-04-20"),
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

    def test_bestaetige_offene_einnahmen_reports_no_late_confirmation_normally(self):
        due = [{"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 1}]
        offene = [
            {
                "key": ("Mo", "08:30", "1", "A", "2026-04-20"),
                "bestaetigt": False,
                "alarm_verschickt": False,
            }
        ]

        result = bestaetige_offene_einnahmen(due, offene, datetime(2026, 4, 20, 8, 31))

        self.assertEqual(len(result["log_texte"]), 1)
        self.assertEqual(result["verspaetet_bestaetigt"], [])
        self.assertTrue(offene[0]["bestaetigt"])

    def test_bestaetige_offene_einnahmen_detects_late_confirmation_after_alarm(self):
        due = [{"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 1}]
        offene = [
            {
                "key": ("Mo", "08:30", "1", "A", "2026-04-20"),
                "bestaetigt": False,
                "alarm_verschickt": True,
            }
        ]

        result = bestaetige_offene_einnahmen(due, offene, datetime(2026, 4, 20, 9, 5))

        self.assertEqual(len(result["verspaetet_bestaetigt"]), 1)
        self.assertEqual(result["verspaetet_bestaetigt"][0], due[0])
        self.assertTrue(offene[0]["bestaetigt"])

    # --- ist_eintrag_faellig_am: Wiederholungstypen ---

    def test_ist_eintrag_faellig_am_woechentlich_matches_only_that_weekday(self):
        eintrag = {"wiederholung": "woechentlich", "tag": "Mo", "zeit": "08:00"}

        self.assertTrue(ist_eintrag_faellig_am(eintrag, date(2026, 4, 20)))  # Montag
        self.assertFalse(ist_eintrag_faellig_am(eintrag, date(2026, 4, 21)))  # Dienstag

    def test_ist_eintrag_faellig_am_defaults_to_woechentlich_when_field_missing(self):
        eintrag = {"tag": "Mo", "zeit": "08:00"}

        self.assertTrue(ist_eintrag_faellig_am(eintrag, date(2026, 4, 20)))

    def test_ist_eintrag_faellig_am_taeglich_matches_every_day(self):
        eintrag = {"wiederholung": "taeglich", "zeit": "08:00"}

        self.assertTrue(ist_eintrag_faellig_am(eintrag, date(2026, 4, 20)))
        self.assertTrue(ist_eintrag_faellig_am(eintrag, date(2026, 4, 27)))

    def test_ist_eintrag_faellig_am_taeglich_respects_bis_datum(self):
        eintrag = {"wiederholung": "taeglich", "zeit": "08:00", "bis_datum": "22.04.2026"}

        self.assertTrue(ist_eintrag_faellig_am(eintrag, date(2026, 4, 22)))
        self.assertFalse(ist_eintrag_faellig_am(eintrag, date(2026, 4, 23)))

    def test_ist_eintrag_faellig_am_einmalig_matches_only_exact_date(self):
        eintrag = {"wiederholung": "einmalig", "datum": "05.09.2026", "zeit": "08:00"}

        self.assertTrue(ist_eintrag_faellig_am(eintrag, date(2026, 9, 5)))
        self.assertFalse(ist_eintrag_faellig_am(eintrag, date(2026, 9, 6)))

    def test_ist_eintrag_faellig_am_einmalig_without_datum_never_matches(self):
        eintrag = {"wiederholung": "einmalig", "zeit": "08:00"}

        self.assertFalse(ist_eintrag_faellig_am(eintrag, date(2026, 9, 5)))

    # --- finde_faellige_einnahmen mit gemischten Wiederholungstypen ---

    def test_finde_faellige_einnahmen_includes_taeglich_and_einmalig(self):
        jetzt = datetime(2026, 4, 20, 8, 0, 0)  # Montag
        plan = [
            {"wiederholung": "taeglich", "zeit": "08:00", "fach": "1", "medikament": "Vitamin"},
            {"wiederholung": "einmalig", "datum": "20.04.2026", "zeit": "08:00", "fach": "2", "medikament": "Einmal"},
            {"wiederholung": "einmalig", "datum": "21.04.2026", "zeit": "08:00", "fach": "3", "medikament": "Morgen"},
            {"wiederholung": "woechentlich", "tag": "Di", "zeit": "08:00", "fach": "4", "medikament": "Dienstag"},
        ]

        due, _jetzt, _minute_key, _tag_kurz, _zeit_str = finde_faellige_einnahmen(plan, jetzt=jetzt)

        medikamente = {e["medikament"] for e in due}
        self.assertEqual(medikamente, {"Vitamin", "Einmal"})

    # --- berechne_naechste_einnahme mit taeglich/einmalig ---

    def test_berechne_naechste_einnahme_considers_taeglich_entries(self):
        jetzt = datetime(2026, 4, 20, 10, 0, 0)
        plan = [{"wiederholung": "taeglich", "zeit": "09:00", "medikament": "Vitamin"}]

        entry, dt_next = berechne_naechste_einnahme(plan, jetzt=jetzt)

        self.assertEqual(entry["medikament"], "Vitamin")
        self.assertEqual(dt_next, datetime(2026, 4, 21, 9, 0, 0))

    def test_berechne_naechste_einnahme_finds_einmalig_far_in_future(self):
        jetzt = datetime(2026, 4, 20, 10, 0, 0)
        plan = [{"wiederholung": "einmalig", "datum": "05.09.2026", "zeit": "08:00", "medikament": "Termin"}]

        entry, dt_next = berechne_naechste_einnahme(plan, jetzt=jetzt)

        self.assertEqual(entry["medikament"], "Termin")
        self.assertEqual(dt_next, datetime(2026, 9, 5, 8, 0, 0))

    def test_berechne_naechste_einnahme_ignores_taeglich_entry_past_bis_datum(self):
        jetzt = datetime(2026, 4, 20, 10, 0, 0)
        plan = [{"wiederholung": "taeglich", "zeit": "09:00", "bis_datum": "19.04.2026", "medikament": "Abgelaufen"}]

        entry, dt_next = berechne_naechste_einnahme(plan, jetzt=jetzt)

        self.assertIsNone(entry)
        self.assertIsNone(dt_next)

    # --- bereinige_offene_einnahmen ---

    def test_bereinige_offene_einnahmen_removes_old_resolved_entries(self):
        jetzt = datetime(2026, 4, 20, 12, 0, 0)
        offene = [
            {"bestaetigt": True, "faellige_zeit": datetime(2026, 4, 17, 8, 0, 0)},
            {"bestaetigt": False, "alarm_verschickt": True, "faellige_zeit": datetime(2026, 4, 17, 8, 0, 0)},
        ]

        result = bereinige_offene_einnahmen(offene, jetzt=jetzt, tage=2)

        self.assertEqual(result, [])

    def test_bereinige_offene_einnahmen_keeps_recent_and_unresolved_entries(self):
        jetzt = datetime(2026, 4, 20, 12, 0, 0)
        aktuell_unbestaetigt = {"bestaetigt": False, "alarm_verschickt": False, "faellige_zeit": datetime(2026, 4, 10, 8, 0, 0)}
        kuerzlich_bestaetigt = {"bestaetigt": True, "faellige_zeit": datetime(2026, 4, 20, 8, 0, 0)}
        offene = [aktuell_unbestaetigt, kuerzlich_bestaetigt]

        result = bereinige_offene_einnahmen(offene, jetzt=jetzt, tage=2)

        self.assertEqual(result, [aktuell_unbestaetigt, kuerzlich_bestaetigt])

    def test_erstelle_offene_einnahmen_keys_include_date_so_daily_entries_dont_collide_across_days(self):
        due = [{"zeit": "08:00", "fach": "1", "medikament": "Vitamin"}]

        tag1 = erstelle_offene_einnahmen(
            due=due, offene_einnahmen=[], jetzt=datetime(2026, 4, 20, 8, 0, 0), delay_min=30
        )
        # Ein Eintrag von "gestern", der nie bestätigt wurde (z.B. Alarm ausgelöst).
        gestern_unbestaetigt = dict(tag1[0])
        gestern_unbestaetigt["bestaetigt"] = False

        tag2 = erstelle_offene_einnahmen(
            due=due, offene_einnahmen=[gestern_unbestaetigt], jetzt=datetime(2026, 4, 21, 8, 0, 0), delay_min=30
        )

        self.assertEqual(len(tag2), 1)
        self.assertNotEqual(tag1[0]["key"], tag2[0]["key"])

    def test_serialize_offene_einnahmen_converts_tuple_key_and_datetimes(self):
        offene = [{
            "key": ("Mo", "08:00", "1", "A", "2026-04-20"),
            "eintrag": {"medikament": "A"},
            "faellige_zeit": datetime(2026, 4, 20, 8, 0, 0),
            "deadline": datetime(2026, 4, 20, 8, 30, 0),
            "bestaetigt": False,
            "alarm_verschickt": False,
        }]

        serialisiert = serialize_offene_einnahmen(offene)

        self.assertIsInstance(serialisiert[0]["key"], list)
        self.assertEqual(serialisiert[0]["key"], ["Mo", "08:00", "1", "A", "2026-04-20"])
        self.assertIsInstance(serialisiert[0]["faellige_zeit"], str)
        self.assertIsInstance(serialisiert[0]["deadline"], str)

    def test_deserialize_offene_einnahmen_restores_tuple_key_and_datetimes(self):
        gespeichert = [{
            "key": ["Mo", "08:00", "1", "A", "2026-04-20"],
            "eintrag": {"medikament": "A"},
            "faellige_zeit": "2026-04-20T08:00:00",
            "deadline": "2026-04-20T08:30:00",
            "bestaetigt": False,
            "alarm_verschickt": False,
        }]

        wiederhergestellt = deserialize_offene_einnahmen(gespeichert)

        self.assertEqual(wiederhergestellt[0]["key"], ("Mo", "08:00", "1", "A", "2026-04-20"))
        self.assertEqual(wiederhergestellt[0]["faellige_zeit"], datetime(2026, 4, 20, 8, 0, 0))
        self.assertEqual(wiederhergestellt[0]["deadline"], datetime(2026, 4, 20, 8, 30, 0))

    def test_serialize_then_deserialize_round_trip_preserves_key_equality(self):
        """Wichtig für die Dedup-/Bestätigungslogik: der Key muss nach einem
        Speichern+Laden-Zyklus weiterhin per Tupel-Gleichheit vergleichbar sein."""
        original_key = ("Mo", "08:00", "1", "A", "2026-04-20")
        offene = [{
            "key": original_key,
            "eintrag": {},
            "faellige_zeit": datetime(2026, 4, 20, 8, 0, 0),
            "deadline": datetime(2026, 4, 20, 8, 30, 0),
            "bestaetigt": False,
            "alarm_verschickt": False,
        }]

        rundgereist = deserialize_offene_einnahmen(serialize_offene_einnahmen(offene))

        self.assertEqual(rundgereist[0]["key"], original_key)

    def test_deserialize_offene_einnahmen_handles_missing_or_empty_data(self):
        self.assertEqual(deserialize_offene_einnahmen([]), [])
        self.assertEqual(deserialize_offene_einnahmen(None), [])


if __name__ == "__main__":
    unittest.main()