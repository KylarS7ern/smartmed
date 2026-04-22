import unittest

from smartmed.hardware.serial_transport import ArduinoSerialError
from smartmed.services.hardware_test_workflow_service import run_hardware_test


class FakeTransport:
    def __init__(self, responses=None, error=None):
        self.responses = responses or []
        self.error = error
        self.commands = []

    def transact(self, command: str):
        self.commands.append(command)

        if self.error is not None:
            raise self.error

        if not self.responses:
            raise AssertionError("Keine Fake-Response mehr vorhanden.")

        return self.responses.pop(0)


class HardwareTestWorkflowServiceTests(unittest.TestCase):
    def test_run_hardware_test_success(self):
        logs = []
        transport = FakeTransport(
            responses=[
                {"ok": True, "kind": "pong", "raw": "OK PONG"},
                {
                    "ok": True,
                    "kind": "dispense",
                    "slot": 1,
                    "count": 1,
                    "raw": "OK DISPENSE 1 1",
                },
            ]
        )

        result = run_hardware_test(
            transport=transport,
            log_callback=logs.append,
            fach=1,
            anzahl=1,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "hardware_test_success")
        self.assertEqual(
            transport.commands,
            ["PING\n", "DISPENSE 1 1\n"],
        )
        self.assertEqual(
            logs,
            ["Hardware-Test erfolgreich: Fach 1, Anzahl 1."],
        )

    def test_run_hardware_test_ping_failed(self):
        logs = []
        transport = FakeTransport(error=ArduinoSerialError("Write timeout"))

        result = run_hardware_test(
            transport=transport,
            log_callback=logs.append,
            fach=1,
            anzahl=1,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "ping_failed")
        self.assertIn("Write timeout", result["message"])
        self.assertEqual(transport.commands, ["PING\n"])
        self.assertEqual(
            logs,
            [f"Hardware-Test fehlgeschlagen: {result['message']}"],
        )

    def test_run_hardware_test_dispense_failed(self):
        logs = []
        transport = FakeTransport(
            responses=[
                {"ok": True, "kind": "pong", "raw": "OK PONG"},
                {
                    "ok": False,
                    "kind": "error",
                    "code": "SLOT_NOT_ENABLED",
                    "message": "",
                    "raw": "ERR SLOT_NOT_ENABLED",
                },
            ]
        )

        result = run_hardware_test(
            transport=transport,
            log_callback=logs.append,
            fach=2,
            anzahl=1,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "dispense_failed")
        self.assertEqual(
            transport.commands,
            ["PING\n", "DISPENSE 2 1\n"],
        )
        self.assertEqual(
            logs,
            [f"Hardware-Test fehlgeschlagen bei Fach 2, Anzahl 1: {result['message']}"],
        )

    def test_run_hardware_test_validation_error(self):
        logs = []
        transport = FakeTransport(
            responses=[
                {"ok": True, "kind": "pong", "raw": "OK PONG"},
            ]
        )

        result = run_hardware_test(
            transport=transport,
            log_callback=logs.append,
            fach=9,
            anzahl=1,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["kind"], "dispense_failed")
        self.assertEqual(transport.commands, ["PING\n"])
        self.assertEqual(
            logs,
            [f"Hardware-Test fehlgeschlagen bei Fach 9, Anzahl 1: {result['message']}"],
        )


if __name__ == "__main__":
    unittest.main()