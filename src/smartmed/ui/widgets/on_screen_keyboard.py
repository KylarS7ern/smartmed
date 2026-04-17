from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


ALPHA_ROWS = [
    ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
    ["y", "x", "c", "v", "b", "n", "m"],
]

SYMBOL_ROWS = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["@", ".", ",", "-", "_", "!", "?", ":", ";"],
    ["/", "\\", "(", ")", "[", "]", "+", "*"],
]


class OnScreenKeyboardPopup(Popup):
    def __init__(self, target_input: TextInput, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.mode = "alpha"
        self.shift_enabled = False

        self.title = "Tastatur"
        self.size_hint = (0.98, 0.70)
        self.auto_dismiss = False

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8,
        )

        self.preview_label = Label(
            text="",
            size_hint_y=None,
            height=55,
            halign="left",
            valign="middle",
        )
        self.preview_label.bind(size=self._sync_preview_text_size)

        self.key_rows_container = BoxLayout(
            orientation="vertical",
            spacing=8,
        )

        self.root_layout.add_widget(self.preview_label)
        self.root_layout.add_widget(self.key_rows_container)

        self.content = self.root_layout

        self._refresh_preview()
        self._rebuild_keys()

    def _sync_preview_text_size(self, instance, value):
        instance.text_size = (value[0] - 20, value[1])

    def _refresh_preview(self):
        value = self.target_input.text or ""

        if getattr(self.target_input, "password", False):
            preview = "•" * len(value)
        else:
            preview = value

        if not preview:
            preview = "[leer]"

        self.preview_label.text = f"Eingabe: {preview}"

    def _clear_key_rows(self):
        self.key_rows_container.clear_widgets()

    def _make_button(self, text, callback, width=1.0):
        btn = Button(text=text, size_hint_x=width)
        btn.bind(on_press=callback)
        return btn

    def _make_char_button(self, value: str, width=1.0):
        return self._make_button(
            text=value,
            callback=lambda *_: self._insert_text(value),
            width=width,
        )

    def _add_spacer(self, row_layout, width=0.5):
        row_layout.add_widget(Widget(size_hint_x=width))

    def _build_alpha_layout(self):
        # Reihe 1: qwertz...
        row1 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=70,
            spacing=6,
        )
        for key in ALPHA_ROWS[0]:
            visible = key.upper() if self.shift_enabled else key
            row1.add_widget(self._make_char_button(visible))
        self.key_rows_container.add_widget(row1)

        # Reihe 2: leicht eingerückt
        row2 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=70,
            spacing=6,
        )
        self._add_spacer(row2, 0.45)
        for key in ALPHA_ROWS[1]:
            visible = key.upper() if self.shift_enabled else key
            row2.add_widget(self._make_char_button(visible))
        self._add_spacer(row2, 0.45)
        self.key_rows_container.add_widget(row2)

        # Reihe 3: Shift | yxcvbnm | Löschen
        row3 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=70,
            spacing=6,
        )
        row3.add_widget(
            self._make_button("Shift", lambda *_: self._toggle_shift(), width=1.5)
        )

        for key in ALPHA_ROWS[2]:
            visible = key.upper() if self.shift_enabled else key
            row3.add_widget(self._make_char_button(visible))

        row3.add_widget(
            self._make_button("Löschen", lambda *_: self._backspace(), width=1.8)
        )
        self.key_rows_container.add_widget(row3)

    def _build_symbol_layout(self):
        # Reihe 1
        row1 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=70,
            spacing=6,
        )
        for key in SYMBOL_ROWS[0]:
            row1.add_widget(self._make_char_button(key))
        self.key_rows_container.add_widget(row1)

        # Reihe 2 leicht eingerückt
        row2 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=70,
            spacing=6,
        )
        self._add_spacer(row2, 0.45)
        for key in SYMBOL_ROWS[1]:
            row2.add_widget(self._make_char_button(key))
        self._add_spacer(row2, 0.45)
        self.key_rows_container.add_widget(row2)

        # Reihe 3: abc | Symbole | Löschen
        row3 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=70,
            spacing=6,
        )
        row3.add_widget(
            self._make_button("abc", lambda *_: self._toggle_mode(), width=1.5)
        )
        for key in SYMBOL_ROWS[2]:
            row3.add_widget(self._make_char_button(key))
        row3.add_widget(
            self._make_button("Löschen", lambda *_: self._backspace(), width=1.8)
        )
        self.key_rows_container.add_widget(row3)

    def _build_bottom_row(self):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=75,
            spacing=6,
        )

        if self.mode == "alpha":
            row.add_widget(
                self._make_button("123", lambda *_: self._toggle_mode(), width=1.2)
            )
        else:
            row.add_widget(
                self._make_button("#+=", lambda *_: self._noop(), width=1.2)
            )

        if self.target_input.multiline:
            row.add_widget(
                self._make_button("Enter", lambda *_: self._insert_text("\n"), width=1.3)
            )
        else:
            row.add_widget(Widget(size_hint_x=1.3))

        row.add_widget(
            self._make_button("Leerzeichen", lambda *_: self._insert_text(" "), width=4.5)
        )
        row.add_widget(
            self._make_button("Fertig", lambda *_: self._done(), width=1.4)
        )
        row.add_widget(
            self._make_button("Schliessen", lambda *_: self.dismiss(), width=1.6)
        )

        self.key_rows_container.add_widget(row)

    def _rebuild_keys(self):
        self._clear_key_rows()

        if self.mode == "alpha":
            self._build_alpha_layout()
        else:
            self._build_symbol_layout()

        self._build_bottom_row()

    def _insert_text(self, value: str):
        self.target_input.focus = True
        self.target_input.insert_text(value)
        self._refresh_preview()

        if self.mode == "alpha" and self.shift_enabled:
            self.shift_enabled = False
            self._rebuild_keys()

    def _backspace(self):
        self.target_input.focus = True
        self.target_input.do_backspace()
        self._refresh_preview()

    def _toggle_shift(self):
        self.shift_enabled = not self.shift_enabled
        self._rebuild_keys()

    def _toggle_mode(self):
        if self.mode == "alpha":
            self.mode = "symbols"
            self.shift_enabled = False
        else:
            self.mode = "alpha"
        self._rebuild_keys()

    def _done(self):
        self.target_input.focus = False
        self.dismiss()

    def _noop(self):
        pass


class SmartTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard_popup = None
        self.bind(focus=self._handle_focus)

    def _handle_focus(self, instance, value):
        if not value:
            return

        if self._keyboard_popup and self._keyboard_popup.parent:
            return

        self._keyboard_popup = OnScreenKeyboardPopup(target_input=self)

        def _on_dismiss(*_args):
            self.focus = False

        self._keyboard_popup.bind(on_dismiss=_on_dismiss)
        self._keyboard_popup.open()