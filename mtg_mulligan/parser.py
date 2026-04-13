def parse_decklist_and_sideboard(decklist_text: str) -> tuple[list[str], list[str]]:
    main_deck = []
    sideboard = []
    current_target = main_deck

    for raw_line in decklist_text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.upper() == "SIDEBOARD:":
            current_target = sideboard
            continue

        parts = line.split(" ", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid decklist line: {line}")

        count_str, card_name = parts
        count = int(count_str)

        current_target.extend([card_name.strip()] * count)

    return main_deck, sideboard