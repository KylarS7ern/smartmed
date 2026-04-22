import code

from smartmed.hardware.protocol import build_dispense_command, build_ping_command
from smartmed.hardware.serial_transport import ArduinoSerialError
from smartmed.hardware.slot_config import get_slot_label

def _format_device_error(code: str, *, slot: int | None = None, count: int | None = None) -> str:
    if code == "INVALID_SLOT":
        return "Ungültiges Fach."
    if code == "INVALID_COUNT":
        return "Ungültige Anzahl."
    if code == "SLOT_NOT_ENABLED":
        return f"{get_slot_label(slot)} ist auf dem Arduino noch nicht aktiviert."
    if code == "DISPENSE_FAILED":
        return f"Ausgabe für {get_slot_label(slot)} konnte nicht ausgeführt werden."
    if code == "INVALID_FORMAT":
        return "Arduino hat ein ungültiges Befehlsformat erkannt."
    if code == "UNKNOWN_COMMAND":
        return "Arduino kennt diesen Befehl nicht."

    if slot is not None and count is not None:
        return f"Arduino-Fehler {code} bei Fach {slot} mit Anzahl {count}."

    return f"Arduino-Fehler {code}."


def ping_arduino(transport) -> dict:
    try:
        response = transport.transact(build_ping_command())
    except ArduinoSerialError as exc:
        return {
            "ok": False,
            "kind": "communication_error",
            "message": str(exc),
        }

    if response.get("ok") and response.get("kind") == "pong":
        return {
            "ok": True,
            "kind": "pong",
            "message": "Arduino ist erreichbar.",
            "response": response,
        }

    return {
        "ok": False,
        "kind": "unexpected_response",
        "message": "Unerwartete Antwort auf PING.",
        "response": response,
    }


def dispense_slot(transport, *, slot: int, count: int = 1) -> dict:
    try:
        command = build_dispense_command(slot, count)
        response = transport.transact(command)
    except ValueError as exc:
        return {
            "ok": False,
            "kind": "validation_error",
            "message": str(exc),
        }
    except ArduinoSerialError as exc:
        return {
            "ok": False,
            "kind": "communication_error",
            "message": str(exc),
        }

    if (
        response.get("ok")
        and response.get("kind") == "dispense"
        and response.get("slot") == slot
        and response.get("count") == count
    ):
        return {
            "ok": True,
            "kind": "dispense",
            "slot": slot,
            "count": count,
            "message": f"{get_slot_label(slot)} wurde {count}x erfolgreich angesteuert.",
            "response": response,
        }

    if response.get("kind") == "error":
        code = response.get("code", "UNKNOWN")
        return {
            "ok": False,
            "kind": "device_error",
            "code": code,
            "message": _format_device_error(code, slot=slot, count=count),
            "response": response,
        }

    return {
        "ok": False,
        "kind": "unexpected_response",
        "message": "Unerwartete Antwort auf DISPENSE.",
        "response": response,
    }