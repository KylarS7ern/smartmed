def rebuild_fach_medikamente(plan_eintraege):
    """Baut die Fach->Medikament-Zuordnung aus dem aktuellen Plan neu auf."""
    fach_medikamente = {}

    for eintrag in plan_eintraege:
        fach = eintrag.get('fach')
        medikament = eintrag.get('medikament')

        if fach and fach not in fach_medikamente:
            fach_medikamente[fach] = medikament

    return fach_medikamente


def _build_plan_log_text(action, *, tag, zeit, fach, medikament, anzahl):
    return (
        f"Plan-Eintrag {action}: "
        f"{tag} {zeit} | Fach {fach} | {medikament} (x{anzahl})"
    )


def create_plan_entry(
    *,
    plan_eintraege,
    fach_medikamente,
    medikament,
    fach,
    tag,
    zeit,
    anzahl,
):
    """Neuen Plan-Eintrag anlegen, falls das Fach dazu passt."""
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
        'tag': tag,
        'zeit': zeit,
        'anzahl': anzahl,
    }

    plan_eintraege.append(eintrag)

    return {
        'ok': True,
        'eintrag': eintrag,
        'fach_medikamente': fach_medikamente_neu,
        'log_text': _build_plan_log_text(
            'neu',
            tag=tag,
            zeit=zeit,
            fach=fach,
            medikament=medikament,
            anzahl=anzahl,
        ),
    }


def update_plan_entry(
    *,
    plan_eintraege,
    fach_medikamente,
    eintrag,
    medikament,
    fach,
    tag,
    zeit,
    anzahl,
):
    """Bestehenden Plan-Eintrag aktualisieren."""
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
    eintrag['tag'] = tag
    eintrag['zeit'] = zeit
    eintrag['anzahl'] = anzahl

    fach_medikamente_neu = rebuild_fach_medikamente(plan_eintraege)

    return {
        'ok': True,
        'fach_medikamente': fach_medikamente_neu,
        'log_text': _build_plan_log_text(
            'geändert',
            tag=tag,
            zeit=zeit,
            fach=fach,
            medikament=medikament,
            anzahl=anzahl,
        ),
    }


def delete_plan_entry(*, plan_eintraege, eintrag):
    """Plan-Eintrag löschen und Fachbelegung neu berechnen."""
    tag = eintrag.get('tag', '')
    zeit = eintrag.get('zeit', '')
    fach = eintrag.get('fach', '')
    medikament = eintrag.get('medikament', '')
    anzahl = eintrag.get('anzahl', 1)

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
        'log_text': _build_plan_log_text(
            'gelöscht',
            tag=tag,
            zeit=zeit,
            fach=fach,
            medikament=medikament,
            anzahl=anzahl,
        ),
    }