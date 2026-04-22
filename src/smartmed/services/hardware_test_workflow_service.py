from smartmed.services.dispense_service import dispense_slot, ping_arduino


def run_hardware_test(*, transport, log_callback, fach: int = 1, anzahl: int = 1) -> dict:
    ping_result = ping_arduino(transport)
    if not ping_result.get("ok"):
        message = ping_result.get("message", "Arduino nicht erreichbar.")
        log_callback(f"Hardware-Test fehlgeschlagen: {message}")
        return {
            "ok": False,
            "kind": "ping_failed",
            "message": message,
            "ping_result": ping_result,
        }

    dispense_result = dispense_slot(transport, slot=fach, count=anzahl)
    if dispense_result.get("ok"):
        log_callback(
            f"Hardware-Test erfolgreich: Fach {fach}, Anzahl {anzahl}."
        )
        return {
            "ok": True,
            "kind": "hardware_test_success",
            "message": f"Hardware-Test erfolgreich für Fach {fach}.",
            "ping_result": ping_result,
            "dispense_result": dispense_result,
        }

    message = dispense_result.get("message", "Unbekannter Hardware-Fehler.")
    log_callback(
        f"Hardware-Test fehlgeschlagen bei Fach {fach}, Anzahl {anzahl}: {message}"
    )
    return {
        "ok": False,
        "kind": "dispense_failed",
        "message": message,
        "ping_result": ping_result,
        "dispense_result": dispense_result,
    }