import random

def draw_hand(decklist: list[str], hand_size: int = 7) -> list[str]:
    deck = decklist[:]
    random.shuffle(deck)
    return deck[:hand_size]