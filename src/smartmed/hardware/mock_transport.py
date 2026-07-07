from smartmed.hardware.protocol import parse_response
from smartmed.hardware.slot_config import SLOT_IDS


class MockArduinoTransport:
    """Simuliert die serielle Arduino-Verbindung für lokale Entwicklung ohne Hardware.

    Implementiert dasselbe Interface wie ArduinoSerialTransport
    (open/close/is_open/transact), damit beide austauschbar verwendet werden können.
    """

    def __init__(self):
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open

    def open(self) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def transact(self, command: str) -> dict:
        if not command.endswith("\n"):
            raise ValueError("Der Befehl muss mit einem Zeilenumbruch enden.")

        self.open()

        line = command.strip()

        if line == "PING":
            return parse_response("OK PONG\n")

        if line.startswith("DISPENSE "):
            parts = line.split()
            if len(parts) != 3:
                return parse_response("ERR INVALID_FORMAT\n")

            try:
                slot = int(parts[1])
                count = int(parts[2])
            except ValueError:
                return parse_response("ERR INVALID_FORMAT\n")

            if slot not in SLOT_IDS:
                return parse_response("ERR INVALID_SLOT\n")

            if count < 1:
                return parse_response("ERR INVALID_COUNT\n")

            return parse_response(f"OK DISPENSE {slot} {count}\n")

        return parse_response("ERR UNKNOWN_COMMAND\n")
