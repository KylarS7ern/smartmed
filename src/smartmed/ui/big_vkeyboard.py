from kivy.uix.vkeyboard import VKeyboard

from smartmed.debug_file import debug_log


class BigVKeyboard(VKeyboard):
    def __init__(self, **kwargs):
        debug_log("[SmartMed] BigVKeyboard __init__ gestartet")
        super().__init__(**kwargs)
        self.font_size = 30
        self.height = 380
        debug_log(
            f"[SmartMed] BigVKeyboard nach __init__: "
            f"size={self.size}, scale={self.scale}, docked={self.docked}"
        )

    def setup_mode_dock(self, *args):
        debug_log(
            f"[SmartMed] setup_mode_dock VORHER: "
            f"size={self.size}, scale={self.scale}"
        )
        self.height = 380
        super().setup_mode_dock(*args)
        debug_log(
            f"[SmartMed] setup_mode_dock NACHHER: "
            f"size={self.size}, scale={self.scale}, "
            f"effective_height={self.height * self.scale}"
        )