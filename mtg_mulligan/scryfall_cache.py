import requests
from pathlib import Path
from config import CACHE_DIR, SCRYFALL_NAMED_URL

CACHE_DIR.mkdir(exist_ok=True)

def safe_filename(card_name: str) -> str:
    cleaned = "".join(
        c if c.isalnum() or c in (" ", "_", "-") else "_"
        for c in card_name
    ).strip()
    return cleaned.replace(" ", "_") + ".png"

def get_cached_image_path(card_name: str) -> Path:
    return CACHE_DIR / safe_filename(card_name)

def download_card_image(card_name: str) -> Path:
    out_path = get_cached_image_path(card_name)

    if out_path.exists():
        return out_path

    resp = requests.get(
        SCRYFALL_NAMED_URL,
        params={"exact": card_name},
        timeout=20,
        headers={"User-Agent": "MTG-Mulligan-Tool/1.0"}
    )
    resp.raise_for_status()
    card = resp.json()

    image_url = None
    if "image_uris" in card and "png" in card["image_uris"]:
        image_url = card["image_uris"]["png"]
    elif "card_faces" in card:
        for face in card["card_faces"]:
            if "image_uris" in face and "png" in face["image_uris"]:
                image_url = face["image_uris"]["png"]
                break

    if not image_url:
        raise ValueError(f"No PNG image found for {card_name}")

    img_resp = requests.get(
        image_url,
        timeout=30,
        headers={"User-Agent": "MTG-Mulligan-Tool/1.0"}
    )
    img_resp.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(img_resp.content)

    return out_path

def preload_deck_images(decklist: list[str]) -> None:
    unique_cards = sorted(set(decklist))
    missing = [card for card in unique_cards if not get_cached_image_path(card).exists()]

    for i, card_name in enumerate(missing, start=1):
        print(f"Caching {i}/{len(missing)}: {card_name}")
        try:
            download_card_image(card_name)
        except Exception as e:
            print(f"Failed to cache {card_name}: {e}")