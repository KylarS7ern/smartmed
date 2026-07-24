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

    def transact(self, command: str, *, timeout: float | None = None, retries: int = 2) -> dict:
        if not command.endswith("\n"):
            raise ValueError("Der Befehl muss mit einem Zeilenumbruch enden.")

        last_error: ArduinoSerialError | None = None

        for versuch in range(retries + 1):
            if versuch > 0:
                # Verbindung war zuletzt kaputt (z.B. Kabel kurz raus/rein,
                # USB-Reset) - kurz warten, bis das Gerät sich neu
                # enumeriert hat, bevor der nächste Versuch startet.
                time.sleep(0.5)

            try:
                return self._transact_once(command, timeout=timeout)
            except ArduinoSerialError as exc:
                last_error = exc
                # self._serial bleibt sonst dauerhaft in einem kaputten
                # Zustand hängen (is_open prüft nur, ob das Objekt noch
                # existiert, nicht ob die Verbindung wirklich funktioniert).
                # Schliessen erzwingt beim nächsten Versuch ein frisches
                # open().
                self.close()

        assert last_error is not None
        raise last_error

    def _transact_once(self, command: str, *, timeout: float | None) -> dict:
        self.open()

        assert self._serial is not None

        original_timeout = self._serial.timeout
        try:
            if timeout is not None:
                self._serial.timeout = timeout

            # Verwirft Bytes, die noch von einer vorherigen, zu spät
            # eingetroffenen Antwort im Puffer liegen (z.B. weil ein früherer
            # Befehl knapp getimeoutet ist) - sonst würde diese Antwort hier
            # fälschlich als Antwort auf den JETZT gesendeten Befehl gelesen
            # und der Versatz würde sich von da an dauerhaft fortsetzen.
            self._serial.reset_input_buffer()

            self._serial.write(command.encode("utf-8"))
            self._serial.flush()
            raw = self._serial.readline().decode("utf-8", errors="replace")
        except SerialException as exc:
            raise ArduinoSerialError(
                f"Serielle Kommunikation fehlgeschlagen: {exc!r}"
            ) from exc
        finally:
            if timeout is not None:
                self._serial.timeout = original_timeout

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