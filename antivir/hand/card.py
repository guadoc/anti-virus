from typing import Literal
from dataclasses import dataclass


High = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Color = Literal[0, 1, 2, 3]

HIGH_STR = ["A", "2", "3", "4", "5", "6"]
COLOR_STR = [""]


@dataclass
class Card:
    high: High
    color: Color

    def __str__(self):
        return
