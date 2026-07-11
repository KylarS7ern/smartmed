import unittest
from datetime import datetime

from smartmed.services.intake_workflow_service import (
    execute_due_intake_workflow,
    prepare_due_intake_workflow,
)


class QueuedTransport:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.commands = []

    def transact(self, command: str, *, timeout=None):
        self.commands.append(command)
        return self.responses.pop(0)


def _dispense_ok(slot, count):
    return {
        "ok": True,
        "kind": "dispense",
        "slot": slot,
        "count": count,
        "raw": f"OK DISPENSE {slot} {count}",
    }


class IntakeWorkflowServiceTests(unittest.TestCase):
    def test_prepare_due_intake_workflow_finds_due_entries(self):
        plan = [{"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 1}]
        jetzt = datetime(2026, 4, 20, 8, 30, 10)  # ein Montag

        prepared = prepare_due_intake_workflow(
            plan_eintraege=plan,
            offene_einnahmen=[],
            settings={"alarm_delay_min": 20},
            last_popup_minute=None,
            jetzt=jetzt,
        )

        self.assertIsNotNone(prepared)
        self.assertEqual(prepared["due"], plan)
        self.assertEqual(prepared["delay_min"], 20)
        self.assertEqual(prepared["tag_kurz"], "Mo")
        self.assertEqual(prepared["zeit_str"], "08:30")

    def test_prepare_due_intake_workflow_returns_none_for_same_minute_twice(self):
        plan = [{"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 1}]
        jetzt = datetime(2026, 4, 20, 8, 30, 10)

        first = prepare_due_intake_workflow(
            plan_eintraege=plan,
            offene_einnahmen=[],
            settings={},
            last_popup_minute=None,
            jetzt=jetzt,
        )
        second = prepare_due_intake_workflow(
            plan_eintraege=plan,
            offene_einnahmen=[],
            settings={},
            last_popup_minute=first["minute_key"],
            jetzt=jetzt,
        )

        self.assertIsNone(second)

    def test_execute_due_intake_workflow_only_queues_confirmation_for_dispensed(self):
        prepared = {
            "due": [
                {"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 1},
                {"tag": "Mo", "zeit": "08:30", "fach": "2", "medikament": "B", "anzahl": 1},
            ],
            "jetzt": datetime(2026, 4, 20, 8, 30, 0),
            "tag_kurz": "Mo",
            "zeit_str": "08:30",
            "delay_min": 30,
        }
        transport = QueuedTransport(
            responses=[
                _dispense_ok(1, 1),
                {
                    "ok": False,
                    "kind": "error",
                    "code": "SLOT_NOT_ENABLED",
                    "message": "",
                    "raw": "ERR SLOT_NOT_ENABLED",
                },
            ]
        )

        result = execute_due_intake_workflow(
            transport=transport,
            prepared=prepared,
            offene_einnahmen=[],
        )

        self.assertEqual(len(result["dispensed_eintraege"]), 1)
        self.assertEqual(result["dispensed_eintraege"][0]["fach"], "1")
        self.assertEqual(len(result["neue_offene"]), 1)
        self.assertEqual(len(result["failed"]), 1)
        self.assertEqual(result["failed"][0]["eintrag"]["fach"], "2")

    def test_execute_due_intake_workflow_no_offene_when_all_failed(self):
        prepared = {
            "due": [{"tag": "Mo", "zeit": "08:30", "fach": "2", "medikament": "B", "anzahl": 1}],
            "jetzt": datetime(2026, 4, 20, 8, 30, 0),
            "tag_kurz": "Mo",
            "zeit_str": "08:30",
            "delay_min": 30,
        }
        transport = QueuedTransport(
            responses=[
                {
                    "ok": False,
                    "kind": "error",
                    "code": "SLOT_NOT_ENABLED",
                    "message": "",
                    "raw": "ERR SLOT_NOT_ENABLED",
                },
            ]
        )

        result = execute_due_intake_workflow(
            transport=transport,
            prepared=prepared,
            offene_einnahmen=[],
        )

        self.assertEqual(result["dispensed_eintraege"], [])
        self.assertEqual(result["neue_offene"], [])
        self.assertEqual(len(result["failed"]), 1)


if __name__ == "__main__":
    unittest.main()
