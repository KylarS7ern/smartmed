import unittest

from smartmed.services.plan_service import create_plan_entry, delete_plan_entry


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


if __name__ == "__main__":
    unittest.main()