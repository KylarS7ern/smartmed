WIEDERHOLUNG_TO_TEXT = {
    'woechentlich': 'Wöchentlich',
    'taeglich': 'Täglich',
    'einmalig': 'Einmalig',
}

TEXT_TO_WIEDERHOLUNG = {text: value for value, text in WIEDERHOLUNG_TO_TEXT.items()}

_WOCHENTAGE_REIHENFOLGE = {
    'Mo': 0, 'Di': 1, 'Mi': 2, 'Do': 3, 'Fr': 4, 'Sa': 5, 'So': 6,
}


def rebuild_fach_medikamente(plan_eintraege):
    """Baut die Fach->Medikament-Zuordnung aus dem aktuellen Plan neu auf."""
    fach_medikamente = {}

    for eintrag in plan_eintraege:
        fach = eintrag.get('fach')
        medikament = eintrag.get('medikament')

        if fach and fach not in fach_medikamente:
            fach_medikamente[fach] = medikament

    return fach_medikamente


def format_repeat_label(eintrag):
    """Baut den Zeit-/Wiederholungs-Teil der Anzeige für einen Plan-Eintrag."""
    wiederholung = eintrag.get('wiederholung', 'woechentlich')
    zeit = eintrag.get('zeit', '')
    bis_datum = eintrag.get('bis_datum', '')

    if wiederholung == 'einmalig':
        datum = eintrag.get('datum', '')
        return f"Einmalig {datum} {zeit}"

    if wiederholung == 'taeglich':
        label = f"Täglich {zeit}"
    else:
        label = f"{eintrag.get('tag', '')} {zeit}"

    if bis_datum:
        label += f" (bis {bis_datum})"

    return label


def format_plan_entry_summary(eintrag):
    """Menschlich lesbare Zusammenfassung eines Plan-Eintrags für Listen/Logs."""
    fach = eintrag.get('fach', '')
    med = eintrag.get('medikament', '')
    anzahl = eintrag.get('anzahl', 1)

    return f"{format_repeat_label(eintrag)} | Fach {fach} | {med} (x{anzahl})"


def _datum_to_sortable(datum_str):
    """Wandelt 'TT.MM.JJJJ' in einen chronologisch sortierbaren String um."""
    try:
        tag, monat, jahr = datum_str.split('.')
        return f"{int(jahr):04d}-{int(monat):02d}-{int(tag):02d}"
    except (ValueError, AttributeError):
        return "9999-99-99"


def plan_entry_sort_key(eintrag):
    """Sortierschlüssel für die Plan-Liste.

    Reihenfolge: zuerst 'Täglich', dann 'Wöchentlich' (nach Wochentag),
    dann 'Einmalig' (chronologisch) - jeweils sekundär nach Uhrzeit.
    """
    wiederholung = eintrag.get('wiederholung', 'woechentlich')
    zeit = eintrag.get('zeit', '')

    if wiederholung == 'taeglich':
        return (0, '', zeit)

    if wiederholung == 'einmalig':
        return (2, _datum_to_sortable(eintrag.get('datum', '')), zeit)

    tag_index = _WOCHENTAGE_REIHENFOLGE.get(eintrag.get('tag', ''), 99)
    return (1, f"{tag_index:02d}", zeit)


ANZAHL_MIN = 1
ANZAHL_MAX = 5


def _validiere_anzahl(anzahl):
    """Prüft die Stückzahl gegen die zulässige Spanne (Lastenheft: bis 5
    Tabletten pro Silo). Gibt bei Fehler einen Meldungstext zurück, sonst None.
    """
    try:
        anzahl_int = int(anzahl)
    except (TypeError, ValueError):
        return 'Anzahl muss eine ganze Zahl sein.'

    if anzahl_int < ANZAHL_MIN or anzahl_int > ANZAHL_MAX:
        return f'Anzahl muss zwischen {ANZAHL_MIN} und {ANZAHL_MAX} liegen.'

    return None


def create_plan_entry(
    *,
    plan_eintraege,
    fach_medikamente,
    medikament,
    fach,
    zeit,
    anzahl,
    wiederholung='woechentlich',
    tag=None,
    datum=None,
    bis_datum=None,
):
    """Neuen Plan-Eintrag anlegen, falls das Fach dazu passt."""
    anzahl_fehler = _validiere_anzahl(anzahl)
    if anzahl_fehler:
        return {'ok': False, 'message': anzahl_fehler}

    vorhandenes_med = fach_medikamente.get(fach)

    if vorhandenes_med is None:
        fach_medikamente_neu = dict(fach_medikamente)
        fach_medikamente_neu[fach] = medikament
    elif vorhandenes_med != medikament:
        return {
            'ok': False,
            'message': (
                f"Fach {fach} ist bereits mit '{vorhandenes_med}' belegt.\n\n"
                "Bitte zuerst die Einträge / Belegung ändern, bevor ein anderes "
                "Medikament für dieses Fach verwendet wird."
            ),
            'prefill_medikament': vorhandenes_med,
        }
    else:
        fach_medikamente_neu = dict(fach_medikamente)

    eintrag = {
        'medikament': medikament,
        'fach': fach,
        'zeit': zeit,
        'anzahl': anzahl,
        'wiederholung': wiederholung,
        'tag': tag,
        'datum': datum,
        'bis_datum': bis_datum,
    }

    plan_eintraege.append(eintrag)

    return {
        'ok': True,
        'eintrag': eintrag,
        'fach_medikamente': fach_medikamente_neu,
        'log_text': f"Plan-Eintrag neu: {format_plan_entry_summary(eintrag)}",
    }


def update_plan_entry(
    *,
    plan_eintraege,
    fach_medikamente,
    eintrag,
    medikament,
    fach,
    zeit,
    anzahl,
    wiederholung='woechentlich',
    tag=None,
    datum=None,
    bis_datum=None,
):
    """Bestehenden Plan-Eintrag aktualisieren."""
    anzahl_fehler = _validiere_anzahl(anzahl)
    if anzahl_fehler:
        return {'ok': False, 'message': anzahl_fehler}

    vorhandenes_med = fach_medikamente.get(fach)

    if (
        vorhandenes_med
        and vorhandenes_med != medikament
        and fach != eintrag.get('fach')
    ):
        return {
            'ok': False,
            'message': (
                f"Fach {fach} ist bereits mit '{vorhandenes_med}' belegt.\n"
                'Bitte zuerst dort den Eintrag ändern oder löschen.'
            ),
        }

    eintrag['medikament'] = medikament
    eintrag['fach'] = fach
    eintrag['zeit'] = zeit
    eintrag['anzahl'] = anzahl
    eintrag['wiederholung'] = wiederholung
    eintrag['tag'] = tag
    eintrag['datum'] = datum
    eintrag['bis_datum'] = bis_datum

    fach_medikamente_neu = rebuild_fach_medikamente(plan_eintraege)

    return {
        'ok': True,
        'fach_medikamente': fach_medikamente_neu,
        'log_text': f"Plan-Eintrag geändert: {format_plan_entry_summary(eintrag)}",
    }


def delete_plan_entry(*, plan_eintraege, eintrag):
    """Plan-Eintrag löschen und Fachbelegung neu berechnen."""
    zusammenfassung = format_plan_entry_summary(eintrag)

    try:
        plan_eintraege.remove(eintrag)
    except ValueError:
        return {
            'ok': False,
            'message': 'Eintrag wurde nicht gefunden.',
            'fach_medikamente': rebuild_fach_medikamente(plan_eintraege),
        }

    return {
        'ok': True,
        'fach_medikamente': rebuild_fach_medikamente(plan_eintraege),
        'log_text': f"Plan-Eintrag gelöscht: {zusammenfassung}",
    }
