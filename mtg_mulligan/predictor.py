from __future__ import annotations

from pathlib import Path
from collections import Counter
import json

import pandas as pd
import requests


# =========================================================
# CONFIG
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CARD_INFO_CACHE_PATH = PROJECT_ROOT / "data" / "processed" / "card_info_cache.json"
SCRYFALL_NAMED_URL = "https://api.scryfall.com/cards/named"
CARD_COUNT = 7


# =========================================================
# CARD INFO HELPERS
# =========================================================
def load_card_info_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_card_info_cache(cache: dict, cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def fetch_card_info(card_name: str) -> dict:
    response = requests.get(
        SCRYFALL_NAMED_URL,
        params={"exact": card_name},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    type_line = data.get("type_line", "")
    return {
        "type_line": type_line,
        "is_land": ("Land" in type_line),
        "cmc": float(data.get("cmc", 0.0)),
    }


def get_card_info(card_name: str, cache: dict) -> dict:
    card_name = str(card_name).strip()

    if not card_name:
        return {
            "type_line": "",
            "is_land": False,
            "cmc": 0.0,
        }

    if card_name not in cache:
        try:
            cache[card_name] = fetch_card_info(card_name)
            save_card_info_cache(cache, CARD_INFO_CACHE_PATH)
        except Exception as e:
            print(f"Warning: could not fetch Scryfall data for '{card_name}': {e}")
            cache[card_name] = {
                "type_line": "",
                "is_land": False,
                "cmc": 0.0,
            }
            save_card_info_cache(cache, CARD_INFO_CACHE_PATH)

    return cache[card_name]


# =========================================================
# FEATURE HELPERS
# =========================================================
def cmc_to_bucket(cmc: float) -> str:
    cmc_int = int(cmc)

    if cmc_int <= 0:
        return "0_drops"
    if cmc_int == 1:
        return "1_drops"
    if cmc_int == 2:
        return "2_drops"
    if cmc_int == 3:
        return "3_drops"
    if cmc_int == 4:
        return "4_drops"
    if cmc_int == 5:
        return "5_drops"
    return "6_plus_drops"


def load_bundle_threshold(bundle: dict, default: float = 0.5) -> float:
    metrics = bundle.get("metrics", {})
    metadata = bundle.get("metadata", {})

    try:
        return float(
            metrics.get(
                "chosen_threshold",
                metrics.get(
                    "threshold",
                    metadata.get(
                        "chosen_threshold",
                        metadata.get("threshold", default)
                    )
                )
            )
        )
    except Exception:
        return float(default)


def build_feature_row(hand, on_play, feature_columns, card_info_cache):
    row = {feature: 0 for feature in feature_columns}

    if "on_play" in row:
        row["on_play"] = int(on_play)

    counts = Counter(hand)
    for card, count in counts.items():
        for k in range(1, count + 1):
            feature_name = f"{card}_{k}"
            if feature_name in row:
                row[feature_name] = 1

    card_infos = []
    for card in hand:
        info = get_card_info(card, card_info_cache)
        card_infos.append((card, info))

    num_lands = sum(1 for _, info in card_infos if info.get("is_land", False))

    if "lands_0_1" in row:
        row["lands_0_1"] = int(num_lands <= 1)
    if "lands_2_4" in row:
        row["lands_2_4"] = int(2 <= num_lands <= 4)
    if "lands_5_plus" in row:
        row["lands_5_plus"] = int(num_lands >= 5)

    mana_counts = {
        "0_drops": 0,
        "1_drops": 0,
        "2_drops": 0,
        "3_drops": 0,
        "4_drops": 0,
        "5_drops": 0,
        "6_plus_drops": 0,
    }

    for _, info in card_infos:
        if info.get("is_land", False):
            continue

        cmc = float(info.get("cmc", 0.0))
        bucket = cmc_to_bucket(cmc)
        mana_counts[bucket] += 1

    for feature_name, value in mana_counts.items():
        if feature_name in row:
            row[feature_name] = value

    return pd.DataFrame([row], columns=feature_columns)


def explain_top_contributors(model, X_row, top_n=10):
    coef = model.coef_[0]
    feature_names = list(X_row.columns)
    values = X_row.iloc[0].values

    contribs = []
    for f, v, c in zip(feature_names, values, coef):
        contribution = float(v) * float(c)
        if v != 0:
            contribs.append((f, v, c, contribution))

    contribs.sort(key=lambda x: x[3], reverse=True)

    top_positive = contribs[:top_n]
    top_negative = sorted(contribs, key=lambda x: x[3])[:top_n]

    return top_positive, top_negative


# =========================================================
# HUMAN-READABLE EXPLANATIONS
# =========================================================
def humanize_feature_name(feature_name: str, value, contribution: float) -> str:
    direction = "supports KEEP" if contribution >= 0 else "supports MULLIGAN"

    if feature_name == "on_play":
        return "You are on the play" if int(value) == 1 else "You are on the draw"

    if feature_name == "lands_0_1":
        return "This hand has 0-1 lands"
    if feature_name == "lands_2_4":
        return "This hand has 2-4 lands"
    if feature_name == "lands_5_plus":
        return "This hand has 5 or more lands"

    if feature_name in {
        "0_drops", "1_drops", "2_drops", "3_drops", "4_drops", "5_drops", "6_plus_drops"
    }:
        bucket_label = feature_name.replace("_", " ")
        return f"{int(value)} cards in the {bucket_label} bucket ({direction})"

    if feature_name.endswith(("_1", "_2", "_3", "_4")):
        parts = feature_name.rsplit("_", 1)
        if len(parts) == 2 and parts[1].isdigit():
            card_name, copies = parts
            if copies == "1":
                return f"Contains {card_name}"
            return f"Contains at least {copies} copies of {card_name}"

    return f"{feature_name} = {value} ({direction})"


def build_reason_strings(top_positive, top_negative, max_reasons: int = 3) -> list[str]:
    reasons = []

    combined = []
    combined.extend(top_positive[:max_reasons])
    combined.extend(top_negative[:max_reasons])
    combined = sorted(combined, key=lambda x: abs(x[3]), reverse=True)

    seen = set()
    for feature_name, value, coef, contribution in combined:
        text = humanize_feature_name(feature_name, value, contribution)
        if text not in seen:
            reasons.append(text)
            seen.add(text)
        if len(reasons) >= max_reasons:
            break

    return reasons


# =========================================================
# MAIN GUI ENTRY POINT
# =========================================================
def predict_hand_for_app(hand, on_play, bundle: dict) -> dict:
    if len(hand) != CARD_COUNT:
        raise ValueError(f"Expected exactly {CARD_COUNT} cards, got {len(hand)}")

    hand = [str(card).strip() for card in hand]

    if int(on_play) not in {0, 1}:
        raise ValueError("on_play must be 1 (play) or 0 (draw)")

    model = bundle["model"]
    feature_columns = bundle["feature_columns"]
    metadata = bundle.get("metadata", {})

    bundle_version = (
        bundle.get("bundle_version")
        or metadata.get("bundle_version")
        or metadata.get("model_version")
        or metadata.get("run_id")
        or "unknown"
    )

    card_info_cache = load_card_info_cache(CARD_INFO_CACHE_PATH)
    X_row = build_feature_row(hand, on_play, feature_columns, card_info_cache)

    prob_keep = float(model.predict_proba(X_row)[0, 1])

    if hasattr(model, "decision_function"):
        logit_score = float(model.decision_function(X_row)[0])
    else:
        logit_score = None

    threshold = load_bundle_threshold(bundle=bundle, default=0.5)
    pred_class = int(prob_keep >= threshold)

    top_positive, top_negative = explain_top_contributors(model, X_row, top_n=5)
    reasons = build_reason_strings(top_positive, top_negative, max_reasons=3)

    return {
        "enabled": True,
        "model_version": bundle_version,
        "run_id": metadata.get("run_id"),
        "experiment_id": metadata.get("experiment_id"),
        "dataset_id": metadata.get("dataset_id"),
        "hand": hand,
        "on_play": int(on_play),
        "threshold": threshold,
        "logit_score": logit_score,
        "prob_keep": prob_keep,
        "prob_mulligan": 1 - prob_keep,
        "pred_class": pred_class,
        "pred_label": "KEEP" if pred_class == 1 else "MULLIGAN",
        "reasons": reasons,
        "top_positive": top_positive,
        "top_negative": top_negative,
    }