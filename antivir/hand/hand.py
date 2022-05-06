from typing import List
from antivir.hand.card import Card


class Hand:
    """Define a hand"""

    def __init__(self, card_list: List[Card]):
        if card_list:
            self.cards = card_list
        else:
            self.cards = []

    def add_card_to_hand(self, card: Card):
        """Add a card to the hand"""
        self.cards.append(card)

    def sort(self):
        """Sort the list of cards.
        It is usefull for the scan of the hand"""
        self.cards.sort()

    def _scan(self) -> List[List[int]]:
        """Scan the hand to get information about
        high and color occurencies"""

    def evaluate(self) -> int:
        """Evaluate the relative value of the hand"""

    def __str__(self) -> str:
        return "".join(str(card) for card in self.cards)
