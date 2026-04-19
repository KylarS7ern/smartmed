from pathlib import Path


DEBUG_FILE = Path("logs/keyboard_debug.txt")


def debug_log(message: str) -> None:
    DEBUG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DEBUG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def debug_log_reset() -> None:
    DEBUG_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEBUG_FILE.write_text("", encoding="utf-8")