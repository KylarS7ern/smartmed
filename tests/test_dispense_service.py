import unittest

from smartmed.hardware.serial_transport import ArduinoSerialError
from smartmed.services.dispense_service import (
    dispense_due_entries,
    dispense_slot,
    ping_arduino,
)


class QueuedTransport:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.commands = []
        self.timeouts = []

    def transact(self, command: str, *, timeout=None):
        self.commands.append(command)
        self.timeouts.append(timeout)
        return self.responses.pop(0)


class FakeTransport:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.commands = []
        self.timeouts = []

    def transact(self, command: str, *, timeout=None):
        self.commands.append(command)
        self.timeouts.append(timeout)

        if self.error is not None:
            raise self.error

        return self.response


class DispenseServiceTests(unittest.TestCase):
    def test_ping_arduino_success(self):
        transport = FakeTransport(response={"ok": True, "kind": "pong", "raw": "OK PONG"})

        result = ping_arduino(transport)

        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "pong")
        self.assertEqual(transport.commands, ["PING\n"])

    def test_ping_arduino_communication_error(self):
        transport = FakeTransport(error=ArduinoSerialError("Port nicht erreichbar."))

        result = ping_arduino(transport)

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "communication_error")
        self.assertIn("Port nicht erreichbar", result["message"])

    def test_dispense_slot_success(self):
        transport = FakeTransport(
            response={
                "ok": True,
                "kind": "dispense",
                "slot": 1,
                "count": 1,
                "raw": "OK DISPENSE 1 1",
            }
        )

        result = dispense_slot(transport, slot=1, count=1)

        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "dispense")
        self.assertEqual(result["slot"], 1)
        self.assertEqual(result["count"], 1)
        self.assertEqual(transport.commands, ["DISPENSE 1 1\n"])

    def test_dispense_slot_validation_error_for_invalid_slot(self):
        transport = FakeTransport()

        result = dispense_slot(transport, slot=9, count=1)

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "validation_error")
        self.assertIn("Ungültiges Fach", result["message"])
        self.assertEqual(transport.commands, [])

    def test_dispense_slot_validation_error_for_invalid_count(self):
        transport = FakeTransport()

        result = dispense_slot(transport, slot=1, count=0)

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "validation_error")
        self.assertIn("count", result["message"])
        self.assertEqual(transport.commands, [])

    def test_dispense_slot_communication_error(self):
        transport = FakeTransport(error=ArduinoSerialError("Write timeout"))

        result = dispense_slot(transport, slot=1, count=1)

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "communication_error")
        self.assertIn("Write timeout", result["message"])

    def test_dispense_slot_device_error(self):
        transport = FakeTransport(
            response={
                "ok": False,
                "kind": "error",
                "code": "SLOT_NOT_ENABLED",
                "message": "",
                "raw": "ERR SLOT_NOT_ENABLED",
            }
        )

        result = dispense_slot(transport, slot=2, count=1)

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "device_error")
        self.assertEqual(result["code"], "SLOT_NOT_ENABLED")
        self.assertIn("Fach 2", result["message"])

    def test_dispense_due_entries_splits_dispensed_and_failed(self):
        due = [
            {"tag": "Mo", "zeit": "08:00", "fach": "1", "medikament": "A", "anzahl": 1},
            {"tag": "Mo", "zeit": "08:00", "fach": "2", "medikament": "B", "anzahl": 2},
        ]
        transport = QueuedTransport(
            responses=[
                {
                    "ok": True,
                    "kind": "dispense",
                    "slot": 1,
                    "count": 1,
                    "raw": "OK DISPENSE 1 1",
                },
                {
                    "ok": False,
                    "kind": "error",
                    "code": "SLOT_NOT_ENABLED",
                    "message": "",
                    "raw": "ERR SLOT_NOT_ENABLED",
                },
            ]
        )

        result = dispense_due_entries(transport, due)

        self.assertEqual(len(result["dispensed"]), 1)
        self.assertEqual(result["dispensed"][0]["eintrag"]["fach"], "1")
        self.assertEqual(len(result["failed"]), 1)
        self.assertEqual(result["failed"][0]["eintrag"]["fach"], "2")
        self.assertEqual(result["failed"][0]["result"]["code"], "SLOT_NOT_ENABLED")

    def test_dispense_due_entries_handles_invalid_fach_without_calling_transport(self):
        due = [
            {"tag": "Mo", "zeit": "08:00", "fach": "keins", "medikament": "A", "anzahl": 1},
        ]
        transport = QueuedTransport(responses=[])

        result = dispense_due_entries(transport, due)

        self.assertEqual(result["dispensed"], [])
        self.assertEqual(len(result["failed"]), 1)
        self.assertEqual(result["failed"][0]["result"]["kind"], "validation_error")
        self.assertEqual(transport.commands, [])

    def test_dispense_due_entries_empty_due_list(self):
        transport = QueuedTransport(responses=[])

        result = dispense_due_entries(transport, [])

        self.assertEqual(result, {"dispensed": [], "failed": []})

    def test_dispense_slot_uses_a_longer_timeout_than_ping(self):
        ping_transport = FakeTransport(response={"ok": True, "kind": "pong", "raw": "OK PONG"})
        ping_arduino(ping_transport)

        dispense_transport = FakeTransport(
            response={
                "ok": True,
                "kind": "dispense",
                "slot": 1,
                "count": 1,
                "raw": "OK DISPENSE 1 1",
            }
        )
        dispense_slot(dispense_transport, slot=1, count=1)

        self.assertIsNone(ping_transport.timeouts[0])
        self.assertIsNotNone(dispense_transport.timeouts[0])
        self.assertGreater(dispense_transport.timeouts[0], 2.0)

    def test_dispense_slot_timeout_scales_with_count(self):
        transport = FakeTransport(
            response={
                "ok": True,
                "kind": "dispense",
                "slot": 1,
                "count": 3,
                "raw": "OK DISPENSE 1 3",
            }
        )

        dispense_slot(transport, slot=1, count=3)

        self.assertGreater(transport.timeouts[0], 3 * 2.0)

    def test_dispense_slot_unexpected_response(self):
        transport = FakeTransport(
            response={
                "ok": True,
                "kind": "ok",
                "raw": "OK SOMETHING_ELSE",
            }
        )

        result = dispense_slot(transport, slot=1, count=1)

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "unexpected_response")


if __name__ == "__main__":
    unittest.main()