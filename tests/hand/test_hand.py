# pylint: skip-file
from antivir.hand.hand import Hand
from antivir.hand.card import Card


def test_sort():
    hand = Hand(
        [Card(11, 2), Card(0, 0), Card(12, 3), Card(7, 2), Card(7, 1), Card(3, 1)]
    )
    hand.sort()
    assert str(hand) == "2s5d9d9cKcAh"
