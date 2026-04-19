from kivy.core.window import Window

from smartmed.debug_file import debug_log, debug_log_reset
from smartmed.ui.big_vkeyboard import BigVKeyboard
from smartmed.app import create_app


debug_log_reset()
debug_log("[SmartMed] main.py gestartet")
debug_log("[SmartMed] set_vkeyboard_class(BigVKeyboard)")
Window.set_vkeyboard_class(BigVKeyboard)


def main() -> None:
    debug_log("[SmartMed] create_app() wird aufgerufen")
    app = create_app()
    debug_log("[SmartMed] app.run() startet")
    app.run()
    debug_log("[SmartMed] app.run() beendet")


if __name__ == "__main__":
    main()