from collections.abc import Callable
from datetime import datetime

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def _open_text_popup(
    *,
    title: str,
    text: str,
    button_text: str = "OK",
    size_hint=(0.85, 0.5),
    on_confirm: Callable[[], None] | None = None,
) -> Popup:
    layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

    label = Label(
        text=text,
        halign="center",
        valign="middle",
    )
    label.bind(size=lambda inst, val: setattr(inst, "text_size", val))

    btn_ok = Button(
        text=button_text,
        size_hint=(1, 0.3),
    )

    layout.add_widget(label)
    layout.add_widget(btn_ok)

    popup = Popup(
        title=title,
        content=layout,
        size_hint=size_hint,
        auto_dismiss=False,
    )

    def _on_press(_instance):
        if on_confirm is not None:
            on_confirm()
        popup.dismiss()

    btn_ok.bind(on_press=_on_press)

    popup.open()
    return popup


def show_due_intake_popup(
    *,
    due: list[dict],
    jetzt: datetime,
    on_confirm: Callable[[], None],
) -> Popup:
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

    return _open_text_popup(
        title="Einnahme fällig",
        text=text,
        button_text="Einnahme bestätigen",
        size_hint=(0.85, 0.5),
        on_confirm=on_confirm,
    )


def show_alarm_popup(eintrag: dict) -> Popup:
    fach = eintrag.get("fach", "")
    med = eintrag.get("medikament", "")
    anzahl = eintrag.get("anzahl", 1)
    tag = eintrag.get("tag", "")
    zeit = eintrag.get("zeit", "")

    text = (
        "ALARM wurde gesendet!\n\n"
        "Die Einnahme wurde nicht rechtzeitig bestätigt:\n\n"
        f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
    )

    return _open_text_popup(
        title="Alarm",
        text=text,
        button_text="OK",
        size_hint=(0.85, 0.5),
    )