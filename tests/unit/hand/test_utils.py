from poqrl.hand.utils import all_hands, all_hands_from_cards
from poqrl.hand.card import Card


def test_all_hands():
    hand_dict = {}
    for hand in all_hands(3):
        hand_dict[hand.hash] = 1
    assert len(hand_dict) == 22100


def test_all_hands_from_cards():
    hand_dict = {}
    cards = [Card(id=7), Card(id=35), Card(id=51), Card(id=3)]
    for hand in all_hands_from_cards(7, cards):
        hand_dict[hand.hash] = 1
    assert len(hand_dict) == 17296
