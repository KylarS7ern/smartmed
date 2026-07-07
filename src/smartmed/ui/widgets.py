"""Wiederverwendbare, durchgängig gestylte Kivy-Widgets für SmartMediSpender.

Zentralisiert das Aussehen (Farben/Grössen aus theme.py), damit alle Screens
konsistent wirken, statt jedes Mal Button/Label-Eigenschaften einzeln zu setzen.
"""

from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput

from smartmed.ui import theme


def _darken(color, factor=0.78):
    r, g, b, a = color
    return (r * factor, g * factor, b * factor, a)


class _RoundedBackgroundButton(Button):
    """Button mit flacher, farbiger, abgerundeter Fläche statt Kivy-Standardgrafik."""

    def __init__(self, bg_color=theme.PRIMARY, bg_color_down=None, **kwargs):
        kwargs.setdefault("font_size", theme.FONT_LARGE)
        kwargs.setdefault("bold", True)
        kwargs.setdefault("color", theme.TEXT_ON_COLOR)
        # Kivys Standardgrafik bringt eigenes Innen-Padding mit; da wir sie
        # durch eine flache Fläche ersetzen, brauchen wir ein eigenes Padding,
        # sonst klebt v.a. linksbündiger Text am Rand.
        kwargs.setdefault("padding", (theme.SPACING + dp(6), dp(8)))
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self._bg_color_normal = bg_color
        self._bg_color_down = bg_color_down or _darken(bg_color)

        with self.canvas.before:
            self._color_instr = Color(*self._bg_color_normal)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[theme.RADIUS])

        self.bind(pos=self._sync_rect, size=self._sync_rect, state=self._sync_color)

    def _sync_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _sync_color(self, *_args):
        self._color_instr.rgba = (
            self._bg_color_down if self.state == "down" else self._bg_color_normal
        )


# Öffentlicher Name für Einzelfälle mit individueller Farbe (z.B. ein heller
# Button auf einem roten Alarm-Hintergrund). Für alle Standardfälle bitte die
# PrimaryButton/SecondaryButton/... Varianten unten verwenden.
RoundedButton = _RoundedBackgroundButton


class PrimaryButton(_RoundedBackgroundButton):
    """Hauptaktion (z.B. Hauptmenü-Einträge, Speichern)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("bg_color", theme.PRIMARY)
        kwargs.setdefault("bg_color_down", theme.PRIMARY_DARK)
        super().__init__(**kwargs)


class SecondaryButton(_RoundedBackgroundButton):
    """Neutrale/zurück-Aktion."""

    def __init__(self, **kwargs):
        kwargs.setdefault("bg_color", theme.SECONDARY)
        kwargs.setdefault("bg_color_down", theme.SECONDARY_DARK)
        super().__init__(**kwargs)


class SuccessButton(_RoundedBackgroundButton):
    """Bestätigende Aktion (z.B. Einnahme bestätigen)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("bg_color", theme.SUCCESS)
        kwargs.setdefault("bg_color_down", theme.SUCCESS_DARK)
        super().__init__(**kwargs)


class DangerButton(_RoundedBackgroundButton):
    """Kritische/löschende Aktion oder Aktion auf rotem Alarm-Hintergrund."""

    def __init__(self, **kwargs):
        kwargs.setdefault("bg_color", theme.DANGER)
        kwargs.setdefault("bg_color_down", theme.DANGER_DARK)
        super().__init__(**kwargs)


class WarningButton(_RoundedBackgroundButton):
    """Warnende Aktion (z.B. Hardware-Test)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("bg_color", theme.WARNING)
        kwargs.setdefault("bg_color_down", theme.WARNING_DARK)
        super().__init__(**kwargs)


class TitleLabel(Label):
    """Grosser, fetter Screen-/Popup-Titel."""

    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", theme.FONT_TITLE)
        kwargs.setdefault("bold", True)
        kwargs.setdefault("color", theme.TEXT_PRIMARY)
        super().__init__(**kwargs)


class BodyLabel(Label):
    """Standard-Fliesstext mit automatischem Zeilenumbruch innerhalb der Widget-Grösse."""

    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", theme.FONT_BODY)
        kwargs.setdefault("color", theme.TEXT_PRIMARY)
        super().__init__(**kwargs)
        self.bind(size=self._sync_text_size)

    def _sync_text_size(self, _inst, size):
        self.text_size = size


class MutedLabel(BodyLabel):
    """Dezenter Hinweistext (z.B. Feldbeschriftungen)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", theme.TEXT_MUTED)
        kwargs.setdefault("font_size", theme.FONT_SMALL)
        super().__init__(**kwargs)


class StyledTextInput(TextInput):
    """TextInput mit flacher Fläche statt Kivys Standard-Grauverlauf, plus dünnem Rahmen."""

    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", theme.FONT_BODY)
        kwargs.setdefault("background_color", theme.SURFACE)
        kwargs.setdefault("foreground_color", theme.TEXT_PRIMARY)
        kwargs.setdefault("cursor_color", theme.PRIMARY)
        kwargs.setdefault("hint_text_color", theme.TEXT_MUTED)
        kwargs.setdefault("padding", [dp(12), dp(12), dp(12), dp(12)])
        super().__init__(**kwargs)

        # Kivys Standard-Hintergrundbild hat einen eingebackenen Grauverlauf.
        # Leeren, damit background_color eine wirklich flache Fläche ergibt.
        self.background_normal = ""
        self.background_active = ""
        self.background_disabled_normal = ""

        with self.canvas.after:
            Color(*theme.BORDER)
            self._border_line = Line(width=1.2)

        self.bind(pos=self._sync_border, size=self._sync_border)
        self._sync_border()

        # Kivy-Bug/Quirk: Wird .text programmatisch gesetzt (z.B. beim Laden
        # gespeicherter Daten in on_pre_enter), bleibt die Textur manchmal
        # unvollständig/leer, bis das Feld angefasst wird. Nach jeder
        # Text-Änderung explizit einen Refresh erzwingen behebt das zuverlässig.
        self.bind(text=self._force_text_refresh)

    def _sync_border(self, *_args):
        self._border_line.rectangle = (self.x, self.y, self.width, self.height)

    def _force_text_refresh(self, *_args):
        self._trigger_refresh_text()
        self._trigger_update_graphics()


class StyledSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", theme.FONT_BODY)
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color", theme.PRIMARY)
        kwargs.setdefault("color", theme.TEXT_ON_COLOR)
        super().__init__(**kwargs)


class StyledSpinner(Spinner):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", theme.FONT_BODY)
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", theme.SURFACE)
        kwargs.setdefault("color", theme.TEXT_PRIMARY)
        kwargs.setdefault("option_cls", StyledSpinnerOption)
        super().__init__(**kwargs)


class FilledBoxLayout(BoxLayout):
    """BoxLayout mit garantiert deckender Hintergrundfarbe (für Popups/Karten)."""

    def __init__(self, fill_color=theme.SURFACE, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color_instr = Color(*fill_color)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_rect, size=self._sync_rect)

    def _sync_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_fill_color(self, color):
        self._color_instr.rgba = color


def field_row(label_text, input_widget, height=None):
    """Zeile aus Beschriftung + Eingabe-Widget für Formulare (Einstellungs-Screens)."""
    row = BoxLayout(
        orientation="horizontal",
        spacing=theme.SPACING,
        size_hint=(1, None),
        height=height if height is not None else theme.ROW_HEIGHT,
    )
    label = BodyLabel(text=label_text, font_size=theme.FONT_SMALL, size_hint=(0.42, 1))
    row.add_widget(label)
    row.add_widget(input_widget)
    return row


def make_popup(
    *,
    title,
    content,
    size_hint=(0.85, 0.5),
    title_color=None,
    fill_color=None,
    show_separator=True,
    auto_dismiss=False,
):
    """Popup mit einheitlichem, hellem Stil.

    Kivys Standard-Popup-Grafik hat einen fest einprogrammierten dunklen
    Titelbalken. Wir leeren das Hintergrundbild und ersetzen es durch eine
    flache Fläche (fill_color), damit der Titelbalken zum restlichen hellen
    Theme passt statt dunkel/grau hervorzustechen.
    """
    return Popup(
        title=title,
        content=content,
        size_hint=size_hint,
        auto_dismiss=auto_dismiss,
        title_size=theme.FONT_LARGE,
        title_color=title_color or theme.TEXT_PRIMARY,
        title_align="center",
        separator_color=theme.BORDER if show_separator else (0, 0, 0, 0),
        separator_height=1 if show_separator else 0,
        background="",
        background_color=fill_color or theme.SURFACE,
    )
