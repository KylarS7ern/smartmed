from datetime import datetime, timedelta


def get_next_medication(plan_eintraege: list, now: datetime | None = None):
    """Gibt (eintrag, datetime) für die nächste geplante Einnahme zurück."""
    if not plan_eintraege:
        return None, None

    jetzt = now or datetime.now()
    wochentage = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    heute_index = jetzt.weekday()

    beste_dt = None
    bester_eintrag = None

    for offset in range(0, 7):
        tag_index = (heute_index + offset) % 7
        tag_kurz = wochentage[tag_index]
        datum = jetzt.date() + timedelta(days=offset)

        for e in plan_eintraege:
            if e.get('tag') != tag_kurz:
                continue

            zeit_str = e.get('zeit', '00:00')
            try:
                stunde, minute = map(int, zeit_str.split(':'))
            except ValueError:
                continue

            dt = datetime(datum.year, datum.month, datum.day, stunde, minute)

            if dt <= jetzt:
                continue

            if beste_dt is None or dt < beste_dt:
                beste_dt = dt
                bester_eintrag = e

    return bester_eintrag, beste_dt
