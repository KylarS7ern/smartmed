from datetime import datetime, timedelta

WOCHENTAGE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']


def berechne_naechste_einnahme(plan_eintraege, jetzt=None):
    """Gibt (eintrag, datetime) für die nächste geplante Einnahme zurück."""
    if not plan_eintraege:
        return None, None

    if jetzt is None:
        jetzt = datetime.now()

    heute_index = jetzt.weekday()
    beste_dt = None
    bester_eintrag = None

    for offset in range(0, 7):
        tag_index = (heute_index + offset) % 7
        tag_kurz = WOCHENTAGE[tag_index]
        datum = jetzt.date() + timedelta(days=offset)

        for eintrag in plan_eintraege:
            if eintrag.get('tag') != tag_kurz:
                continue

            zeit_str = eintrag.get('zeit', '00:00')

            try:
                stunde, minute = map(int, zeit_str.split(':'))
            except (ValueError, AttributeError):
                continue

            kandidat_dt = datetime(
                datum.year,
                datum.month,
                datum.day,
                stunde,
                minute,
            )

            if kandidat_dt <= jetzt:
                continue

            if beste_dt is None or kandidat_dt < beste_dt:
                beste_dt = kandidat_dt
                bester_eintrag = eintrag

    return bester_eintrag, beste_dt
