from smartmed.config import ARDUINO_DISPENSE_TIMEOUT_PER_UNIT
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
        # DISPENSE lässt den Arduino erst den Motor drehen, bevor er
        # antwortet - das dauert je nach Stückzahl mehrere Sekunden, also
        # deutlich länger als das normale (kurze) PING-Timeout.
        timeout = max(count, 1) * ARDUINO_DISPENSE_TIMEOUT_PER_UNIT
        response = transport.transact(command, timeout=timeout)
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
        code = response.get("code", "UNBEKANNT")
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


def dispense_due_entries(transport, due: list) -> dict:
    """Löst für jeden fälligen Plan-Eintrag die Hardware-Ausgabe aus.

    Gibt {"dispensed": [...], "failed": [...]} zurück. Jeder Eintrag enthält
    den ursprünglichen Plan-Eintrag ('eintrag') sowie das Dispense-Ergebnis
    ('result'). Ein Fehler bei einem Fach bricht die übrigen fälligen
    Einträge nicht ab.
    """
    dispensed = []
    failed = []

    for eintrag in due:
        fach_raw = eintrag.get("fach", "")
        anzahl = eintrag.get("anzahl", 1)

        try:
            slot = int(fach_raw)
        except (TypeError, ValueError):
            failed.append({
                "eintrag": eintrag,
                "result": {
                    "ok": False,
                    "kind": "validation_error",
                    "message": f"Ungültiges Fach '{fach_raw}' im Plan-Eintrag.",
                },
            })
            continue

        result = dispense_slot(transport, slot=slot, count=anzahl)

        if result.get("ok"):
            dispensed.append({"eintrag": eintrag, "result": result})
        else:
            failed.append({"eintrag": eintrag, "result": result})

    return {"dispensed": dispensed, "failed": failed}