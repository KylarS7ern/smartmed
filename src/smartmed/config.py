from pathlib import Path
from kivy.config import Config

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "smartmed_plan.json"

# Aktuelles Legacy-Fensterverhalten vorerst beibehalten
LEGACY_WINDOW_WIDTH = 480
LEGACY_WINDOW_HEIGHT = 800
LEGACY_WINDOW_RESIZABLE = False

# Zielgerät-Info für spätere UI-Anpassung
TARGET_SCREEN_WIDTH = 720
TARGET_SCREEN_HEIGHT = 1280
TARGET_SCREEN_ORIENTATION = "portrait"

# Muss vor den restlichen Kivy-Imports angewendet werden
Config.set("graphics", "width", str(LEGACY_WINDOW_WIDTH))
Config.set("graphics", "height", str(LEGACY_WINDOW_HEIGHT))
Config.set("graphics", "resizable", "1" if LEGACY_WINDOW_RESIZABLE else "0")