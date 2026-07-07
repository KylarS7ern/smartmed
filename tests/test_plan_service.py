import unittest

from smartmed.services.plan_service import (
    create_plan_entry,
    delete_plan_entry,
    format_plan_entry_summary,
    plan_entry_sort_key,
)


class PlanServiceTests(unittest.TestCase):
    def test_create_plan_entry_assigns_medication_to_empty_slot(self):
        plan = []
        fach_medikamente = {}

        result = create_plan_entry(
            plan_eintraege=plan,
            fach_medikamente=fach_medikamente,
            medikament="Aspirin",
            fach="1",
            tag="Mo",
            zeit="08:00",
            anzahl=2,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(len(plan), 1)
        self.assertEqual(result["fach_medikamente"], {"1": "Aspirin"})
        self.assertIn("Plan-Eintrag neu", result["log_text"])

    def test_create_plan_entry_rejects_conflicting_medication_for_same_slot(self):
        plan = []
        fach_medikamente = {"1": "Aspirin"}

        result = create_plan_entry(
            plan_eintraege=plan,
            fach_medikamente=fach_medikamente,
            medikament="Ibuprofen",
            fach="1",
            tag="Mo",
            zeit="08:00",
            anzahl=1,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["prefill_medikament"], "Aspirin")
        self.assertEqual(plan, [])

    def test_delete_plan_entry_rebuilds_slot_mapping(self):
        entry_1 = {
            "medikament": "Aspirin",
            "fach": "1",
            "tag": "Mo",
            "zeit": "08:00",
            "anzahl": 1,
        }
        entry_2 = {
            "medikament": "Vitamin D",
            "fach": "2",
            "tag": "Di",
            "zeit": "09:00",
            "anzahl": 1,
        }
        plan = [entry_1, entry_2]

        result = delete_plan_entry(plan_eintraege=plan, eintrag=entry_1)

        self.assertTrue(result["ok"])
        self.assertEqual(plan, [entry_2])
        self.assertEqual(result["fach_medikamente"], {"2": "Vitamin D"})

    def test_create_plan_entry_stores_taeglich_with_bis_datum(self):
        plan = []

        result = create_plan_entry(
            plan_eintraege=plan,
            fach_medikamente={},
            medikament="Vitamin D",
            fach="1",
            zeit="08:00",
            anzahl=1,
            wiederholung="taeglich",
            bis_datum="31.12.2026",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(plan[0]["wiederholung"], "taeglich")
        self.assertEqual(plan[0]["bis_datum"], "31.12.2026")
        self.assertIsNone(plan[0]["tag"])

    def test_create_plan_entry_defaults_to_woechentlich(self):
        plan = []

        create_plan_entry(
            plan_eintraege=plan,
            fach_medikamente={},
            medikament="Aspirin",
            fach="1",
            tag="Mo",
            zeit="08:00",
            anzahl=1,
        )

        self.assertEqual(plan[0]["wiederholung"], "woechentlich")

    def test_format_plan_entry_summary_woechentlich(self):
        eintrag = {"tag": "Mo", "zeit": "08:00", "fach": "1", "medikament": "Aspirin", "anzahl": 2}

        self.assertEqual(
            format_plan_entry_summary(eintrag),
            "Mo 08:00 | Fach 1 | Aspirin (x2)",
        )

    def test_format_plan_entry_summary_taeglich_with_end_date(self):
        eintrag = {
            "wiederholung": "taeglich", "zeit": "08:00", "fach": "1",
            "medikament": "Vitamin D", "anzahl": 1, "bis_datum": "31.12.2026",
        }

        self.assertEqual(
            format_plan_entry_summary(eintrag),
            "Täglich 08:00 (bis 31.12.2026) | Fach 1 | Vitamin D (x1)",
        )

    def test_format_plan_entry_summary_einmalig(self):
        eintrag = {
            "wiederholung": "einmalig", "datum": "05.09.2026", "zeit": "08:00",
            "fach": "2", "medikament": "Termin-Tablette", "anzahl": 1,
        }

        self.assertEqual(
            format_plan_entry_summary(eintrag),
            "Einmalig 05.09.2026 08:00 | Fach 2 | Termin-Tablette (x1)",
        )

    def test_plan_entry_sort_key_orders_taeglich_before_woechentlich_before_einmalig(self):
        taeglich = {"wiederholung": "taeglich", "zeit": "08:00"}
        woechentlich = {"wiederholung": "woechentlich", "tag": "Mo", "zeit": "08:00"}
        einmalig = {"wiederholung": "einmalig", "datum": "01.01.2027", "zeit": "08:00"}

        eintraege = [einmalig, woechentlich, taeglich]
        eintraege.sort(key=plan_entry_sort_key)

        self.assertEqual(eintraege, [taeglich, woechentlich, einmalig])

    def test_plan_entry_sort_key_orders_einmalig_chronologically(self):
        spaeter = {"wiederholung": "einmalig", "datum": "05.09.2026", "zeit": "08:00"}
        frueher = {"wiederholung": "einmalig", "datum": "01.05.2026", "zeit": "08:00"}

        eintraege = [spaeter, frueher]
        eintraege.sort(key=plan_entry_sort_key)

        self.assertEqual(eintraege, [frueher, spaeter])


if __name__ == "__main__":
    unittest.main()