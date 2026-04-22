import unittest

from smartmed.hardware.serial_transport import ArduinoSerialError
from smartmed.services.dispense_service import dispense_slot, ping_arduino


class FakeTransport:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.commands = []

    def transact(self, command: str):
        self.commands.append(command)

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