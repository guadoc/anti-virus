# pylint: skip-file
import pytest
from antivir.hand.card import Card


def test_card_from_hash():
    assert Card(card_hash="3s").high == 1
    assert Card(card_hash="Ac").high == 12
    assert Card(card_hash="Qh").high == 10
    assert Card(card_hash="2s").suit == 3
    assert Card(card_hash="Ac").suit == 0
    assert Card(card_hash="Qh").suit == 2


@pytest.mark.parametrize(
    "id, card_hash",
    [(14, "3d"), (12, "Ac"), (51, "As"), (0, "2c"), (35, "Jh")],
)
def test_card_from_id(id: int, card_hash: str):
    assert Card(id=id).hash() == card_hash


def test_card_to_string():
    assert str(Card(high=2, suit=3)) == "4♠"
    assert str(Card(high=12, suit=0)) == "A♣"
    assert str(Card(high=0, suit=1)) == "2♦"
    assert str(Card(high=11, suit=2)) == "K♥"


def test_card_comparison():
    assert Card(high=2, suit=2) <= Card(high=3, suit=2)
    assert not Card(high=11, suit=0) > Card(high=11, suit=1)
    assert Card(high=8, suit=3) <= Card(high=8, suit=3)
    assert not Card(high=5, suit=3) >= Card(high=8, suit=3)
    assert Card(high=5, suit=1) < Card(high=5, suit=3)
    assert not Card(high=8, suit=3) < Card(high=8, suit=3)
    assert not Card(high=11, suit=0) <= Card(high=0, suit=0)
    assert not Card(high=3, suit=2) == Card(high=2, suit=3)
    assert not Card(id=13) == Card(id=14)
