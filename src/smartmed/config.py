import math
import os
import sys
from pathlib import Path
from kivy.config import Config

if sys.platform == "win32":
    # Windows skaliert das Fenster sonst per eigener Anzeigeskalierung
    # (z.B. 250%) über die angeforderte Pixelgrösse hinaus - auf dem Pi
    # gibt es das nicht. Ohne diesen Aufruf sieht die App auf einem
    # Windows-Entwicklungslaptop unrealistisch gross/anders proportioniert
    # aus als später auf dem echten Gerät.
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
    except (AttributeError, OSError):
        pass


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default
    
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "smartmed_plan.json"

EXPORT_DIR = PROJECT_ROOT / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Benachrichtigung / Alarm
TELEGRAM_BOT_TOKEN = os.getenv("SMARTMED_TELEGRAM_BOT_TOKEN", "")
EMAIL_SMTP_SERVER = os.getenv("SMARTMED_EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = _env_int("SMARTMED_EMAIL_SMTP_PORT", 587)
EMAIL_USERNAME = os.getenv("SMARTMED_EMAIL_USERNAME", "smartmedispender@gmail.com")
EMAIL_PASSWORT = os.getenv("SMARTMED_EMAIL_PASSWORT", "")

# Zielgerät: Raspberry Pi Touch Display 2
TARGET_SCREEN_WIDTH = 720
TARGET_SCREEN_HEIGHT = 1280
TARGET_SCREEN_ORIENTATION = "portrait"
TARGET_SCREEN_DIAGONAL_INCH = 7.9

APP_WINDOW_WIDTH = TARGET_SCREEN_WIDTH
APP_WINDOW_HEIGHT = TARGET_SCREEN_HEIGHT
APP_WINDOW_RESIZABLE = False

# Reale Punktdichte (DPI) des Zielgeräts, aus Auflösung + Bildschirmdiagonale
# berechnet - wird unten fest vorgegeben statt sie raten zu lassen: Sowohl
# SDL2/X11 auf dem Pi (kleine, hochauflösende DSI-Touchscreens werden dort
# öfters falsch erkannt) als auch Windows' Anzeigeskalierung auf dem
# Entwicklungs-Laptop würden sonst zu falschen Werten führen.
TARGET_SCREEN_DPI = math.hypot(TARGET_SCREEN_WIDTH, TARGET_SCREEN_HEIGHT) / TARGET_SCREEN_DIAGONAL_INCH

# Kivys dp()/sp()-Einheiten (Schrift- und Touch-Zielgrössen) skalieren NICHT
# mit KIVY_DPI, sondern ausschliesslich mit der "density" (1dp = density px).
# dp ist als Vielfaches von 160 DPI definiert (Android-Konvention), daher
# muss density = eigene_dpi / 160 sein, damit z.B. dp(64) auf dem Zielgerät
# wirklich die beabsichtigten ~10mm physische Grösse ergibt - unabhängig
# davon, was das jeweilige Betriebssystem selbst an Skalierung annimmt.
# Beide Variablen müssen gesetzt sein, bevor irgendwo kivy.metrics
# importiert wird (z.B. via smartmed.ui.theme unten).
os.environ.setdefault("KIVY_DPI", str(TARGET_SCREEN_DPI))
os.environ.setdefault("KIVY_METRICS_DENSITY", str(TARGET_SCREEN_DPI / 160))

# Arduino / serielle Kommunikation
ARDUINO_PORT = os.getenv("SMARTMED_ARDUINO_PORT", "/dev/ttyACM0")
ARDUINO_BAUDRATE = _env_int("SMARTMED_ARDUINO_BAUDRATE", 115200)
# Timeout für einfache Befehle wie PING (soll bei nicht erreichbarem Arduino
# zügig einen Fehler melden).
ARDUINO_TIMEOUT = _env_float("SMARTMED_ARDUINO_TIMEOUT", 2.0)
# DISPENSE lässt den Arduino den Motor drehen, bevor er antwortet - das
# dauert je nach Kalibrierung/Stückzahl mehrere Sekunden. Die Python-Seite
# kennt die genaue Arduino-Kalibrierung bewusst nicht (siehe .ino), wartet
# hier pro Einheit aber grosszügig lang, damit ein normales Timeout nicht
# faelschlich als "Antwort kam nicht" gewertet wird, während der Arduino in
# Wirklichkeit nur noch am Drehen ist.
ARDUINO_DISPENSE_TIMEOUT_PER_UNIT = _env_float("SMARTMED_ARDUINO_DISPENSE_TIMEOUT_PER_UNIT", 8.0)

# "real" (Standard, Pi mit angeschlossenem Arduino) oder "mock"
# (lokale Entwicklung/Tests am Laptop ohne Hardware).
HARDWARE_MODE = os.getenv("SMARTMED_HARDWARE_MODE", "real").strip().lower()

# Kiosk-Modus: 1 = Vollbild/randlos/fixe Grösse wie am echten Gerät (Standard,
# unverändertes Pi-Verhalten). 0 = normales, verschiebbares Fenster für die
# lokale Entwicklung z.B. in VS Code auf dem Laptop.
KIOSK_MODE = _env_int("SMARTMED_KIOSK", 1) == 1

# Muss vor den restlichen Kivy-Imports angewendet werden
Config.set("graphics", "width", str(APP_WINDOW_WIDTH))
Config.set("graphics", "height", str(APP_WINDOW_HEIGHT))

if KIOSK_MODE:
    # Verhalten am echten Gerät: fixe Grösse, randlos, Vollbild.
    Config.set("graphics", "resizable", "1" if APP_WINDOW_RESIZABLE else "0")
    Config.set("graphics", "fullscreen", "1")
    Config.set("graphics", "borderless", "1")
    Config.set("input", "mouse", "mouse,disable_on_activity")
else:
    # Lokale Entwicklung: normales, verschiebbares/schliessbares Fenster.
    Config.set("graphics", "resizable", "1")
    Config.set("graphics", "fullscreen", "0")
    Config.set("graphics", "borderless", "0")

Config.set("kivy", "keyboard_mode", "dock")
Config.set("kivy", "keyboard_layout", "qwertz")

from kivy.core.window import Window
from smartmed.ui import theme

Window.clearcolor = theme.BACKGROUND