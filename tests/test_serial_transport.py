import unittest
from unittest.mock import MagicMock, patch

from serial import SerialException

from smartmed.hardware.serial_transport import (
    ArduinoSerialError,
    ArduinoSerialTransport,
    SerialTransportConfig,
)


def _make_transport():
    return ArduinoSerialTransport(
        SerialTransportConfig(port="COM_TEST", baudrate=9600, timeout=1.0)
    )


class SerialTransportReconnectTests(unittest.TestCase):
    @patch("smartmed.hardware.serial_transport.time.sleep")
    @patch("smartmed.hardware.serial_transport.serial.Serial")
    def test_transact_reconnects_and_succeeds_after_one_failure(self, mock_serial_cls, mock_sleep):
        broken = MagicMock()
        broken.is_open = True
        broken.write.side_effect = SerialException("Kabel raus")

        working = MagicMock()
        working.is_open = True
        working.readline.return_value = b"OK PONG\r\n"

        mock_serial_cls.side_effect = [broken, working]

        transport = _make_transport()
        result = transport.transact("PING\n")

        self.assertEqual(result["kind"], "pong")
        self.assertEqual(mock_serial_cls.call_count, 2)
        broken.close.assert_called_once()

    @patch("smartmed.hardware.serial_transport.time.sleep")
    @patch("smartmed.hardware.serial_transport.serial.Serial")
    def test_transact_raises_after_exhausting_retries(self, mock_serial_cls, mock_sleep):
        broken = MagicMock()
        broken.is_open = True
        broken.write.side_effect = SerialException("Kabel raus")
        mock_serial_cls.return_value = broken

        transport = _make_transport()

        with self.assertRaises(ArduinoSerialError):
            transport.transact("PING\n", retries=2)

        self.assertEqual(mock_serial_cls.call_count, 3)

    @patch("smartmed.hardware.serial_transport.time.sleep")
    @patch("smartmed.hardware.serial_transport.serial.Serial")
    def test_transact_succeeds_without_reconnect_when_healthy(self, mock_serial_cls, mock_sleep):
        healthy = MagicMock()
        healthy.is_open = True
        healthy.readline.return_value = b"OK PONG\r\n"
        mock_serial_cls.return_value = healthy

        transport = _make_transport()
        result = transport.transact("PING\n")

        self.assertEqual(result["kind"], "pong")
        self.assertEqual(mock_serial_cls.call_count, 1)
        healthy.close.assert_not_called()


if __name__ == "__main__":
    unittest.main()
