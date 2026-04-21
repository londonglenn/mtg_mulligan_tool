import csv
from datetime import datetime
from pathlib import Path


def save_result(
    hand: list[str],
    play_draw: str,
    decision: str,
    outfile: Path,
    model_feedback: dict | None = None,
) -> None:
    """
    Save one mulligan decision row to CSV.

    Parameters
    ----------
    hand : list[str]
        The 7-card opening hand.
    play_draw : str
        "play" or "draw".
    decision : str
        Human decision, typically "keep" or "mulligan".
    outfile : Path
        Destination CSV path.
    model_feedback : dict | None
        Optional model comparison payload. Expected keys may include:
            - enabled
            - model_version
            - pred_label
            - prob_keep
            - prob_mulligan
            - threshold
            - logit_score
            - reasons
            - run_id
            - dataset_id
    """
    outfile.parent.mkdir(parents=True, exist_ok=True)
    file_exists = outfile.exists()

    # Normalize hand length to exactly 7 columns
    hand = [str(card).strip() for card in hand]
    if len(hand) < 7:
        hand = hand + [""] * (7 - len(hand))
    elif len(hand) > 7:
        hand = hand[:7]

    # Default blank model fields
    model_feedback = model_feedback or {}

    enabled = bool(model_feedback) or bool(model_feedback.get("enabled", False))
    model_version = model_feedback.get("model_version", "")
    run_id = model_feedback.get("run_id", "")
    dataset_id = model_feedback.get("dataset_id", "")
    model_decision = model_feedback.get("pred_label", "")
    prob_keep = model_feedback.get("prob_keep", "")
    prob_mulligan = model_feedback.get("prob_mulligan", "")
    threshold = model_feedback.get("threshold", "")
    logit_score = model_feedback.get("logit_score", "")

    reasons = model_feedback.get("reasons", [])
    if isinstance(reasons, list):
        model_reasons = " | ".join(str(r) for r in reasons)
    else:
        model_reasons = str(reasons) if reasons is not None else ""

    header = [
        "timestamp",
        "play_draw",
        "card1", "card2", "card3", "card4", "card5", "card6", "card7",
        "decision",
        "model_feedback_enabled",
        "model_version",
        "run_id",
        "dataset_id",
        "model_decision",
        "model_keep_probability",
        "model_mulligan_probability",
        "model_threshold",
        "model_score",
        "model_reasons",
    ]

    row = [
        datetime.now().isoformat(),
        play_draw,
        *hand,
        decision,
        enabled,
        model_version,
        run_id,
        dataset_id,
        model_decision,
        prob_keep,
        prob_mulligan,
        threshold,
        logit_score,
        model_reasons,
    ]

    with open(outfile, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(header)

        writer.writerow(row)