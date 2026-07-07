from dataclasses import dataclass

import serial
import time
from serial import SerialException

from smartmed.config import (
    ARDUINO_BAUDRATE,
    ARDUINO_PORT,
    ARDUINO_TIMEOUT,
    HARDWARE_MODE,
)
from smartmed.hardware.protocol import parse_response


class ArduinoSerialError(Exception):
    """Fehler bei der seriellen Kommunikation mit dem Arduino."""


@dataclass(frozen=True)
class SerialTransportConfig:
    port: str = ARDUINO_PORT
    baudrate: int = ARDUINO_BAUDRATE
    timeout: float = ARDUINO_TIMEOUT


class ArduinoSerialTransport:
    def __init__(self, config: SerialTransportConfig | None = None):
        self.config = config or SerialTransportConfig()
        self._serial: serial.Serial | None = None

    @property
    def is_open(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def open(self) -> None:
        if self.is_open:
            return

        try:
            self._serial = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout,
                write_timeout=self.config.timeout,
            )

            # Arduino Leonardo resettet oft beim Öffnen der USB-Serial-Verbindung.
            # Deshalb kurz warten, bis der Sketch wieder bereit ist.
            time.sleep(2.0)

            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()

        except SerialException as exc:
            raise ArduinoSerialError(
                f"Serielle Verbindung konnte nicht geöffnet werden: {self.config.port}"
            ) from exc

    def close(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            finally:
                self._serial = None

    def transact(self, command: str) -> dict:
        if not command.endswith("\n"):
            raise ValueError("Der Befehl muss mit einem Zeilenumbruch enden.")

        self.open()

        assert self._serial is not None

        try:
            self._serial.write(command.encode("utf-8"))
            self._serial.flush()
            raw = self._serial.readline().decode("utf-8", errors="replace")
        except SerialException as exc:
            raise ArduinoSerialError(
                f"Serielle Kommunikation fehlgeschlagen: {exc!r}"
            ) from exc
        
        response = parse_response(raw)

        if response["kind"] == "empty":
            raise ArduinoSerialError("Keine Antwort vom Arduino erhalten.")

        return response


def create_arduino_transport():
    """Erzeugt den Hardware-Transport passend zu SMARTMED_HARDWARE_MODE.

    "real" (Standard) -> echte serielle Verbindung zum Arduino.
    "mock" -> simulierte Verbindung für lokale Entwicklung/Tests ohne Hardware.
    """
    if HARDWARE_MODE == "mock":
        from smartmed.hardware.mock_transport import MockArduinoTransport

        return MockArduinoTransport()

    return ArduinoSerialTransport()