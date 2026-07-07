import unittest

from smartmed.hardware.mock_transport import MockArduinoTransport
from smartmed.services.dispense_service import dispense_slot, ping_arduino


class MockArduinoTransportTests(unittest.TestCase):
    def test_ping_returns_pong(self):
        transport = MockArduinoTransport()

        result = ping_arduino(transport)

        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "pong")

    def test_dispense_valid_slot_succeeds(self):
        transport = MockArduinoTransport()

        result = dispense_slot(transport, slot=1, count=2)

        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "dispense")
        self.assertEqual(result["slot"], 1)
        self.assertEqual(result["count"], 2)

    def test_dispense_invalid_slot_returns_device_error(self):
        transport = MockArduinoTransport()

        # build_dispense_command validates slots itself before they ever
        # reach the transport, so drive the transport directly with a raw
        # command to exercise its own slot-validation path.
        response = transport.transact("DISPENSE 9 1\n")

        self.assertFalse(response["ok"])
        self.assertEqual(response["code"], "INVALID_SLOT")

    def test_transact_requires_trailing_newline(self):
        transport = MockArduinoTransport()

        with self.assertRaises(ValueError):
            transport.transact("PING")

    def test_open_close_toggle_is_open(self):
        transport = MockArduinoTransport()

        self.assertFalse(transport.is_open)
        transport.open()
        self.assertTrue(transport.is_open)
        transport.close()
        self.assertFalse(transport.is_open)


if __name__ == "__main__":
    unittest.main()
