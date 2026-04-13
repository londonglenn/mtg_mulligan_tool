import csv
from datetime import datetime
from pathlib import Path


def save_result(hand: list[str], play_draw: str, decision: str, outfile: Path) -> None:
    outfile.parent.mkdir(parents=True, exist_ok=True)
    file_exists = outfile.exists()

    with open(outfile, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "play_draw",
                "card1", "card2", "card3", "card4", "card5", "card6", "card7",
                "decision"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            play_draw,
            *hand,
            decision
        ])