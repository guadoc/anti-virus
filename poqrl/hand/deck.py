import random
from typing import Optional, List
from poqrl.hand.card import Card

random.seed(77)


class Deck:
    def __init__(self, distributed_cards: Optional[List[Card]] = None):
        self.deck = []
        if distributed_cards:
            self.ditributed_cards = distributed_cards
        else:
            self.ditributed_cards = []

        distributed_ids = [card.id for card in self.ditributed_cards]
        for card_id in range(52):
            if card_id not in distributed_ids:
                self.deck.append(Card(id=card_id))
        random.shuffle(self.deck)

    def distribute_random_card(self):
        """Distribute a card randomly chosen in the deck.
        The returned card should not have been distributed previously
        """
        card = self.deck.pop()
        self.ditributed_cards.append(card)
        return card

    def shuffle(self):
        """Reset the deck as if no card has been distributed previously"""
        self.deck += self.ditributed_cards
        random.shuffle(self.deck)
        self.ditributed_cards = []
