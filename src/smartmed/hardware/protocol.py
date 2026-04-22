VALID_SLOTS = {1, 2, 3}


def build_ping_command() -> str:
    return "PING\n"


def build_dispense_command(slot: int, count: int = 1) -> str:
    if slot not in VALID_SLOTS:
        raise ValueError(f"Ungültiges Fach: {slot}. Erlaubt sind 1, 2, 3.")

    if count <= 0:
        raise ValueError("count muss >= 1 sein.")

    return f"DISPENSE {slot} {count}\n"


def parse_response(raw: str) -> dict:
    line = raw.strip()

    if not line:
        return {
            "ok": False,
            "kind": "empty",
            "raw": raw,
            "message": "Leere Antwort vom Arduino.",
        }

    parts = line.split()

    if parts[0] == "OK":
        if len(parts) >= 2 and parts[1] == "PONG":
            return {
                "ok": True,
                "kind": "pong",
                "raw": line,
            }

        if len(parts) >= 4 and parts[1] == "DISPENSE":
            try:
                slot = int(parts[2])
                count = int(parts[3])
            except ValueError:
                return {
                    "ok": False,
                    "kind": "invalid_ok_format",
                    "raw": line,
                    "message": "OK-Antwort hat ungültige Zahlenwerte.",
                }

            return {
                "ok": True,
                "kind": "dispense",
                "slot": slot,
                "count": count,
                "raw": line,
            }

        return {
            "ok": True,
            "kind": "ok",
            "raw": line,
        }

    if parts[0] == "ERR":
        code = parts[1] if len(parts) >= 2 else "UNKNOWN"
        message = " ".join(parts[2:]) if len(parts) >= 3 else ""

        return {
            "ok": False,
            "kind": "error",
            "code": code,
            "message": message,
            "raw": line,
        }

    return {
        "ok": False,
        "kind": "unknown",
        "raw": line,
        "message": "Unbekannte Antwort vom Arduino.",
    }