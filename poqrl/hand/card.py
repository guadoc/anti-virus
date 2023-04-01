from typing import Literal, Optional, Any
from dataclasses import dataclass


High = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Suit = Literal[0, 1, 2, 3]

HIGH_HASH = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
SUIT_HASH = ["c", "d", "h", "s"]
SUIT_SYMBOL = ["♣", "♦", "♥", "♠"]


@dataclass
class Card:
    """Class representing playing cards"""

    def __init__(
        self,
        id: Optional[int] = None,
        high: Optional[High] = None,
        suit: Optional[Suit] = None,
        card_hash: Optional[str] = None,
    ):
        if id is not None:
            self.id = id
            self.high = id % 13
            self.suit = int(float(id - self.high) / 13)
        elif high is not None and suit is not None:
            self.high = high
            self.suit = suit
            self.id = self.high + self.suit * 13
        elif card_hash is not None:
            self.high = HIGH_HASH.index(card_hash[0])
            self.suit = SUIT_HASH.index(card_hash[1])
            self.id = self.high + self.suit * 13
        else:
            raise ValueError("Wrong arguments for Card object")

    @property
    def hash(self) -> str:
        "Compute a hash of a card"
        return f"{HIGH_HASH[self.high]}{SUIT_HASH[self.suit]}"

    def __str__(self):
        return f"{HIGH_HASH[self.high]}{SUIT_SYMBOL[self.suit]}"

    def __le__(self, card):
        if self.high < card.high or (self.high == card.high and self.suit <= card.suit):
            return True
        return False

    def __lt__(self, card):
        if self.high < card.high or (self.high == card.high and self.suit < card.suit):
            return True
        return False

    def __ge__(self, card):
        if self.high > card.high or (self.high == card.high and self.suit >= card.suit):
            return True
        return False

    def __gt__(self, card):
        if self.high > card.high or (self.high == card.high and self.suit > card.suit):
            return True
        return False

    def __eq__(self, card):
        if self.high == card.high and self.suit == card.suit:
            return True
        return False

    def is_in(self, hand: Any):
        for card in hand.cards:
            if self.id == card.id:
                return True
        return False
