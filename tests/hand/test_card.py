# pylint: skip-file

from antivir.hand.card import Card


def test_card_comparison():
    assert Card(2, 2) <= Card(3, 2)
    assert Card(11, 0) <= Card(11, 1)
    assert Card(8, 3) <= Card(8, 3)
    assert Card(5, 3) < Card(8, 3)
    assert Card(5, 1) < Card(5, 3)
    assert not Card(8, 3) < Card(8, 3)
    assert not Card(11, 0) <= Card(0, 0)


def test_card_string():
    assert str(Card(2, 3)) == "4h"
    assert str(Card(12, 0)) == "As"
    assert str(Card(0, 1)) == "2d"
