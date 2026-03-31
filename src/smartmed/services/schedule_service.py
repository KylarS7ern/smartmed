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


def finde_faellige_einnahmen(plan_eintraege, jetzt=None):
    """Gibt (due, jetzt, minute_key, tag_kurz, zeit_str) für aktuell fällige Einnahmen zurück."""
    if jetzt is None:
        jetzt = datetime.now()

    jetzt = jetzt.replace(second=0, microsecond=0)
    minute_key = jetzt.strftime('%Y-%m-%d %H:%M')
    tag_kurz = WOCHENTAGE[jetzt.weekday()]
    zeit_str = jetzt.strftime('%H:%M')

    due = [
        eintrag for eintrag in plan_eintraege
        if eintrag.get('tag') == tag_kurz and eintrag.get('zeit') == zeit_str
    ]

    return due, jetzt, minute_key, tag_kurz, zeit_str


def berechne_alarm_delay_minuten(delay_wert, standard=30):
    """Liest die Alarm-Verzögerung robust aus den Settings."""
    try:
        delay_min = int(delay_wert)
        if delay_min <= 0:
            return standard
        return delay_min
    except (TypeError, ValueError):
        return standard


def erstelle_offene_einnahmen(due, offene_einnahmen, jetzt, delay_min, tag_kurz=None, zeit_str=None):
    """Erzeugt neue offene Einnahmen für aktuell fällige Einträge."""
    deadline = jetzt + timedelta(minutes=delay_min)
    neue_offene = []

    for eintrag in due:
        tag = eintrag.get('tag', tag_kurz or '')
        zeit = eintrag.get('zeit', zeit_str or '')
        fach = eintrag.get('fach', '')
        med = eintrag.get('medikament', '')

        key = (tag, zeit, fach, med)

        schon_drin = any(
            (off.get('key') == key) and (not off.get('bestaetigt'))
            for off in (offene_einnahmen + neue_offene)
        )
        if schon_drin:
            continue

        neue_offene.append({
            'key': key,
            'eintrag': eintrag,
            'faellige_zeit': jetzt,
            'deadline': deadline,
            'bestaetigt': False,
            'alarm_verschickt': False,
        })

    return neue_offene


def finde_ueberfaellige_offene_einnahmen(offene_einnahmen, jetzt=None):
    """Gibt (ueberfaellige, jetzt) für offene überfällige Einnahmen zurück."""
    if jetzt is None:
        jetzt = datetime.now()

    ueberfaellige = []

    for offene_einnahme in offene_einnahmen:
        if offene_einnahme.get('bestaetigt'):
            continue

        if offene_einnahme.get('alarm_verschickt'):
            continue

        deadline = offene_einnahme.get('deadline')
        if deadline and jetzt > deadline:
            ueberfaellige.append(offene_einnahme)

    return ueberfaellige, jetzt

def bestaetige_offene_einnahmen(due, offene_einnahmen, zeitpunkt):
    """Markiert passende offene Einnahmen als bestätigt und gibt Log-Texte zurück."""
    ts = zeitpunkt.strftime('%Y-%m-%d %H:%M')
    log_texte = []

    for eintrag in due:
        tag = eintrag.get('tag', '')
        zeit = eintrag.get('zeit', '')
        fach = eintrag.get('fach', '')
        med = eintrag.get('medikament', '')
        anzahl = eintrag.get('anzahl', 1)

        key = (tag, zeit, fach, med)

        for offene_einnahme in offene_einnahmen:
            if offene_einnahme.get('key') == key and not offene_einnahme.get('bestaetigt'):
                offene_einnahme['bestaetigt'] = True

        log_texte.append(
            f"Einnahme bestätigt ({ts}): {tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
        )

    return log_texte

    