from pathlib import Path
from kivy.config import Config

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "smartmed_plan.json"

# Zielgerät: Raspberry Pi Touch Display 2
TARGET_SCREEN_WIDTH = 720
TARGET_SCREEN_HEIGHT = 1280
TARGET_SCREEN_ORIENTATION = "portrait"

APP_WINDOW_WIDTH = TARGET_SCREEN_WIDTH
APP_WINDOW_HEIGHT = TARGET_SCREEN_HEIGHT
APP_WINDOW_RESIZABLE = False

# Muss vor den restlichen Kivy-Imports angewendet werden
Config.set("graphics", "width", str(APP_WINDOW_WIDTH))
Config.set("graphics", "height", str(APP_WINDOW_HEIGHT))
Config.set("graphics", "resizable", "1" if APP_WINDOW_RESIZABLE else "0")
Config.set("graphics", "fullscreen", "1")
Config.set("graphics", "borderless", "1")

Config.set("input", "mouse", "mouse,disable_on_activity")

Config.set("kivy", "keyboard_mode", "dock")
Config.set("kivy", "keyboard_layout", "qwertz")