from typing import Literal
from dataclasses import dataclass


High = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Color = Literal[0, 1, 2, 3]

HIGH_STR = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
COLOR_STR = ["s", "d", "c", "h"]


@dataclass
class Card:
    """Class representing playing cards"""

    high: High
    color: Color

    def __str__(self):
        return f"{HIGH_STR[self.high]}{COLOR_STR[self.color]}"

    def __le__(self, card):
        if self.high < card.high or (
            self.high == card.high and self.color <= card.color
        ):
            return True
        return False

    def __lt__(self, card):
        if self.high < card.high or (
            self.high == card.high and self.color < card.color
        ):
            return True
        return False

    def __ge__(self, card):
        if self.high > card.high or (
            self.high == card.high and self.color >= card.color
        ):
            return True
        return False

    def __gt__(self, card):
        if self.high > card.high or (
            self.high == card.high and self.color > card.color
        ):
            return True
        return False
