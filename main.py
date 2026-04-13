from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
import re

from config import DECKLISTS_DIR, RESULTS_DIR
from mtg_mulligan.parser import parse_decklist_and_sideboard
from mtg_mulligan.scryfall_cache import preload_deck_images
from mtg_mulligan.hand_generator import draw_hand
from mtg_mulligan.results import save_result
from mtg_mulligan.gui import MulliganApp


def safe_name(text: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9_-]+', "_", text.strip())
    return cleaned.strip("_") or "anonymous"


def ask_username() -> str:
    root = tk.Tk()
    root.withdraw()

    username = simpledialog.askstring("Username", "Enter your username:")
    root.destroy()

    if not username or not username.strip():
        return "anonymous"

    return username.strip()


def main():
    deck_filename = "boros_energy.txt"
    deck_name = "boros_energy"

    deck_path = DECKLISTS_DIR / deck_filename
    deck_text = deck_path.read_text(encoding="utf-8")

    main_deck, sideboard = parse_decklist_and_sideboard(deck_text)

    preload_deck_images(main_deck)

    username = ask_username()
    username_for_file = safe_name(username)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results_file = RESULTS_DIR / f"{username_for_file}_{timestamp}.csv"

    app = MulliganApp(
        decklist=main_deck,
        draw_hand_func=draw_hand,
        save_result_func=save_result,
        results_file=results_file,
        username=username,
        deck_name=deck_name,
    )
    app.run()


if __name__ == "__main__":
    main()