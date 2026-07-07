from collections.abc import Callable
from datetime import datetime

from kivy.metrics import dp

from smartmed.ui import theme
from smartmed.ui.widgets import (
    FilledBoxLayout,
    RoundedButton,
    SuccessButton,
    TitleLabel,
    BodyLabel,
    make_popup,
)


WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def _open_filled_popup(
    *,
    heading: str,
    text: str,
    fill_color,
    text_color,
    button,
    size_hint=(0.88, 0.55),
    on_confirm: Callable[[], None] | None = None,
):
    """Popup mit vollflächig eingefärbtem Inhalt (für maximale Auffälligkeit).

    Der native Kivy-Popup-Titelbalken wird unterdrückt (title=""), die
    Überschrift steht stattdessen gross im eingefärbten Inhalt selbst.
    """
    layout = FilledBoxLayout(
        fill_color=fill_color,
        orientation="vertical",
        padding=theme.PADDING,
        spacing=theme.SPACING,
    )

    heading_label = TitleLabel(
        text=heading,
        color=text_color,
        size_hint=(1, None),
        height=dp(48),
        halign="center",
        valign="middle",
    )
    heading_label.bind(size=lambda inst, val: setattr(inst, "text_size", val))

    body_label = BodyLabel(
        text=text,
        color=text_color,
        halign="center",
        valign="middle",
    )

    layout.add_widget(heading_label)
    layout.add_widget(body_label)
    layout.add_widget(button)

    popup = make_popup(
        title="",
        content=layout,
        size_hint=size_hint,
        fill_color=fill_color,
        show_separator=False,
    )

    def _on_press(_instance):
        if on_confirm is not None:
            on_confirm()
        popup.dismiss()

    button.bind(on_press=_on_press)

    popup.open()
    return popup


def show_due_intake_popup(
    *,
    due: list[dict],
    jetzt: datetime,
    on_confirm: Callable[[], None],
):
    """Freundliche, gut sichtbare Aufforderung zur Einnahme-Bestätigung."""
    tag_kurz = WOCHENTAGE[jetzt.weekday()]
    zeit_str = jetzt.strftime("%H:%M")

    zeilen = []
    for eintrag in due:
        fach = eintrag.get("fach", "")
        med = eintrag.get("medikament", "")
        anzahl = eintrag.get("anzahl", 1)
        zeilen.append(f"Fach {fach} | {med} (x{anzahl})")

    einnahmen_text = "\n".join(zeilen)

    text = (
        f"{tag_kurz} {jetzt.strftime('%d.%m.%Y')} {zeit_str}\n\n"
        f"Folgende Einnahme(n) sind fällig:\n\n"
        f"{einnahmen_text}"
    )

    return _open_filled_popup(
        heading="Einnahme fällig",
        text=text,
        fill_color=theme.PRIMARY,
        text_color=theme.TEXT_ON_COLOR,
        button=SuccessButton(
            text="Einnahme bestätigen",
            font_size=theme.FONT_XLARGE,
            size_hint=(1, None),
            height=dp(72),
        ),
        size_hint=(0.9, 0.6),
        on_confirm=on_confirm,
    )


def show_dispense_error_popup(failed: list[dict]):
    """Zeigt einen Fehler-Hinweis, wenn die automatische Ausgabe fehlgeschlagen ist.

    'failed' enthält Dicts mit 'eintrag' (Plan-Eintrag) und 'result'
    (Dispense-Ergebnis, siehe dispense_service.dispense_due_entries).
    """
    zeilen = []
    for item in failed:
        eintrag = item.get("eintrag", {})
        result = item.get("result", {})
        fach = eintrag.get("fach", "")
        med = eintrag.get("medikament", "")
        grund = result.get("message", "Unbekannter Fehler.")
        zeilen.append(f"Fach {fach} | {med}: {grund}")

    text = (
        "Die automatische Ausgabe ist fehlgeschlagen.\n"
        "Bitte Techniker/Pflegeperson informieren:\n\n"
        + "\n".join(zeilen)
    )

    return _open_filled_popup(
        heading="Ausgabe fehlgeschlagen",
        text=text,
        fill_color=theme.WARNING,
        text_color=theme.TEXT_PRIMARY,
        button=RoundedButton(
            text="OK",
            bg_color=theme.SURFACE,
            color=theme.WARNING_DARK,
            size_hint=(1, None),
            height=dp(64),
        ),
        size_hint=(0.88, 0.55),
    )


def show_alarm_popup(eintrag: dict):
    """Sehr auffälliges (rotes) Alarm-Popup: Einnahme wurde nicht rechtzeitig bestätigt."""
    fach = eintrag.get("fach", "")
    med = eintrag.get("medikament", "")
    anzahl = eintrag.get("anzahl", 1)
    tag = eintrag.get("tag", "")
    zeit = eintrag.get("zeit", "")

    text = (
        "Die Einnahme wurde nicht rechtzeitig bestätigt:\n\n"
        f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})\n\n"
        "Angehörige/Arzt wurden benachrichtigt."
    )

    return _open_filled_popup(
        heading="ALARM",
        text=text,
        fill_color=theme.DANGER,
        text_color=theme.TEXT_ON_COLOR,
        button=RoundedButton(
            text="OK",
            bg_color=theme.SURFACE,
            color=theme.DANGER_DARK,
            size_hint=(1, None),
            height=dp(72),
            font_size=theme.FONT_XLARGE,
        ),
        size_hint=(0.9, 0.6),
    )
