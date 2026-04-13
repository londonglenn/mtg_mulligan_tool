from pathlib import Path
import sys

SCRYFALL_NAMED_URL = "https://api.scryfall.com/cards/named"
UPLOAD_URL = "https://mulligan-server.onrender.com/upload"

def get_bundle_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BUNDLE_DIR = get_bundle_dir()
APP_DIR = get_app_dir()

DECKLISTS_DIR = BUNDLE_DIR / "decklists"
CACHE_DIR = APP_DIR / "card_cache"
RESULTS_DIR = APP_DIR / "results"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)