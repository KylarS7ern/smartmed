"""Zentrales Design-System für SmartMediSpender.

Helle, hochkontrastige Optik mit grosszügigen Schriftgrössen/Touch-Zielen –
das Gerät wird primär von älteren Menschen bedient.
"""

from kivy.metrics import dp

# Farben (RGBA, 0..1)
BACKGROUND = (0.95, 0.96, 0.97, 1)
SURFACE = (1, 1, 1, 1)

TEXT_PRIMARY = (0.10, 0.12, 0.16, 1)
TEXT_MUTED = (0.42, 0.46, 0.50, 1)
TEXT_ON_COLOR = (1, 1, 1, 1)

PRIMARY = (0.09, 0.42, 0.71, 1)
PRIMARY_DARK = (0.06, 0.30, 0.52, 1)

SECONDARY = (0.55, 0.58, 0.62, 1)
SECONDARY_DARK = (0.42, 0.45, 0.49, 1)

SUCCESS = (0.16, 0.58, 0.35, 1)
SUCCESS_DARK = (0.11, 0.44, 0.27, 1)

DANGER = (0.82, 0.15, 0.16, 1)
DANGER_DARK = (0.60, 0.09, 0.10, 1)

WARNING = (0.88, 0.55, 0.10, 1)
WARNING_DARK = (0.70, 0.42, 0.06, 1)

BORDER = (0.82, 0.85, 0.88, 1)

# Schriftgrössen – grosszügig für ältere Anwender.
# TITLE/XLARGE für täglich genutzte Kernaktionen, BODY/SMALL für
# Einstellungs-Formulare mit vielen Feldern.
FONT_TITLE = "30sp"
FONT_XLARGE = "26sp"
FONT_LARGE = "22sp"
FONT_BODY = "20sp"
FONT_SMALL = "17sp"

SPACING = dp(14)
PADDING = dp(24)

RADIUS = dp(14)

# Standardhöhen (dp-skaliert). Wichtig: sp-Schriftgrössen skalieren
# automatisch mit der System-DPI/Anzeigeskalierung - reine Pixelzahlen
# (z.B. "height=52") tun das NICHT und würden bei hoher Skalierung zu eng
# für den Text werden. Daher hier konsequent dp() statt roher Zahlen.
# Auf dem Zielgerät (Raspberry Pi Touch Display 2, ~186dpi) entspricht
# 1dp ca. 1/160 Zoll - alle drei Werte liegen damit bei ca. 10-11.5mm
# physischer Höhe, also über der üblichen Mindestempfehlung für
# Touch-Ziele (ca. 9-10mm), was für ältere Anwender bewusst grosszügig ist.
ROW_HEIGHT = dp(64)
BUTTON_HEIGHT = dp(64)
BUTTON_HEIGHT_LARGE = dp(72)
