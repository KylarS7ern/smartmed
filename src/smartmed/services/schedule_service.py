from datetime import datetime, timedelta

WOCHENTAGE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

# Wie weit in die Zukunft nach der nächsten Einnahme gesucht wird (Tage).
# Grosszügig bemessen, damit auch weit vorausgeplante "einmalig"-Einträge
# gefunden werden. Die Suche bricht ohnehin ab, sobald ein Kandidat gefunden
# wurde (siehe berechne_naechste_einnahme).
NAECHSTE_EINNAHME_LOOKAHEAD_TAGE = 366


def ist_eintrag_faellig_am(eintrag, ziel_datum):
    """Prüft, ob ein Plan-Eintrag an einem bestimmten Kalendertag fällig ist.

    Berücksichtigt die Wiederholungsart:
    - 'woechentlich' (Standard/Fallback für alte Einträge ohne dieses Feld):
      fällig jede Woche am gespeicherten Wochentag ('tag').
    - 'taeglich': fällig an jedem Tag.
    - 'einmalig': fällig nur genau am gespeicherten 'datum'.

    Bei 'woechentlich' und 'taeglich' wird ein optionales 'bis_datum' beachtet:
    ist ziel_datum danach, gilt der Eintrag nicht mehr als fällig.
    """
    wiederholung = eintrag.get('wiederholung', 'woechentlich')

    if wiederholung == 'einmalig':
        datum_str = eintrag.get('datum', '')
        try:
            eintrag_datum = datetime.strptime(datum_str, '%d.%m.%Y').date()
        except (ValueError, TypeError):
            return False
        return eintrag_datum == ziel_datum

    bis_datum_str = eintrag.get('bis_datum', '')
    if bis_datum_str:
        try:
            bis_datum = datetime.strptime(bis_datum_str, '%d.%m.%Y').date()
            if ziel_datum > bis_datum:
                return False
        except ValueError:
            pass

    if wiederholung == 'taeglich':
        return True

    tag_kurz = WOCHENTAGE[ziel_datum.weekday()]
    return eintrag.get('tag') == tag_kurz


def berechne_naechste_einnahme(plan_eintraege, jetzt=None):
    """Gibt (eintrag, datetime) für die nächste geplante Einnahme zurück."""
    if not plan_eintraege:
        return None, None

    if jetzt is None:
        jetzt = datetime.now()

    beste_dt = None
    bester_eintrag = None

    for offset in range(0, NAECHSTE_EINNAHME_LOOKAHEAD_TAGE):
        datum = jetzt.date() + timedelta(days=offset)

        for eintrag in plan_eintraege:
            if not ist_eintrag_faellig_am(eintrag, datum):
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

        # Ein an Tag N gefundener Kandidat ist immer früher als jeder
        # mögliche Kandidat an einem späteren Tag - weitere Tage prüfen ist
        # dann unnötig.
        if beste_dt is not None:
            break

    return bester_eintrag, beste_dt


def finde_faellige_einnahmen(plan_eintraege, jetzt=None):
    """Gibt (due, jetzt, minute_key, tag_kurz, zeit_str) für aktuell fällige Einnahmen zurück."""
    if jetzt is None:
        jetzt = datetime.now()

    jetzt = jetzt.replace(second=0, microsecond=0)
    minute_key = jetzt.strftime('%Y-%m-%d %H:%M')
    tag_kurz = WOCHENTAGE[jetzt.weekday()]
    zeit_str = jetzt.strftime('%H:%M')
    heute = jetzt.date()

    due = [
        eintrag for eintrag in plan_eintraege
        if eintrag.get('zeit') == zeit_str and ist_eintrag_faellig_am(eintrag, heute)
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

        # jetzt.date() macht den Schlüssel auch für 'taeglich'-Einträge (die
        # keinen festen Wochentag haben) an unterschiedlichen Tagen eindeutig.
        key = (tag, zeit, fach, med, jetzt.strftime('%Y-%m-%d'))

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


def bereinige_offene_einnahmen(offene_einnahmen, jetzt=None, tage=2):
    """Entfernt bereits abgeschlossene (bestätigte oder alarmierte) offene
    Einnahmen, die älter als 'tage' Tage sind, damit die Liste bei täglich
    wiederkehrenden Einträgen nicht unbegrenzt wächst. Noch offene
    (unbestätigte, nicht alarmierte) Einträge bleiben immer erhalten.
    """
    grenze = (jetzt or datetime.now()) - timedelta(days=tage)
    behalten = []

    for eintrag in offene_einnahmen:
        abgeschlossen = eintrag.get('bestaetigt') or eintrag.get('alarm_verschickt')
        faellige_zeit = eintrag.get('faellige_zeit')

        if abgeschlossen and isinstance(faellige_zeit, datetime) and faellige_zeit < grenze:
            continue

        behalten.append(eintrag)

    return behalten


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


def markiere_ueberfaellige_offene_einnahmen(ueberfaellige):
    """Markiert überfällige offene Einnahmen als alarmiert und bereitet Ausgabetexte vor."""
    verarbeitete = []

    for off in ueberfaellige:
        eintrag = off.get('eintrag', {})

        fach = eintrag.get('fach', '')
        med = eintrag.get('medikament', '')
        anzahl = eintrag.get('anzahl', 1)
        tag = eintrag.get('tag', '')
        zeit = eintrag.get('zeit', '')

        off['alarm_verschickt'] = True

        verarbeitete.append({
            'eintrag': eintrag,
            'console_text': (
                f"[ALARM] Einnahme NICHT bestätigt: "
                f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
            ),
            'log_text': (
                f"ALARM: Einnahme NICHT bestätigt: "
                f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
            ),
        })

    return verarbeitete


def bestaetige_offene_einnahmen(due, offene_einnahmen, zeitpunkt):
    """Markiert passende offene Einnahmen als bestätigt.

    Gibt {'log_texte': [...], 'verspaetet_bestaetigt': [...]} zurück.
    'verspaetet_bestaetigt' enthält die Plan-Einträge, für die bereits ein
    Alarm ausgelöst wurde, bevor die Bestätigung eintraf (Pflicht-Anforderung:
    eine nachträgliche Bestätigung löst eine zweite Benachrichtigung aus).
    """
    ts = zeitpunkt.strftime('%Y-%m-%d %H:%M')
    log_texte = []
    verspaetet_bestaetigt = []

    for eintrag in due:
        tag = eintrag.get('tag', '')
        zeit = eintrag.get('zeit', '')
        fach = eintrag.get('fach', '')
        med = eintrag.get('medikament', '')
        anzahl = eintrag.get('anzahl', 1)

        key = (tag, zeit, fach, med, zeitpunkt.strftime('%Y-%m-%d'))

        for offene_einnahme in offene_einnahmen:
            if offene_einnahme.get('key') == key and not offene_einnahme.get('bestaetigt'):
                war_bereits_alarmiert = offene_einnahme.get('alarm_verschickt', False)
                offene_einnahme['bestaetigt'] = True

                if war_bereits_alarmiert:
                    verspaetet_bestaetigt.append(eintrag)

        log_texte.append(
            f"Einnahme bestätigt ({ts}): {tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
        )

    return {
        'log_texte': log_texte,
        'verspaetet_bestaetigt': verspaetet_bestaetigt,
    }
