# pylint: skip-file
from typing import List
import pytest
from poqrl.hand.hand import Hand
from poqrl.hand.card import Card


# class HandS(Hand):
#     def __init__(self, hand_hash: str):
#         super().__init__(hand_hash=hand_hash)


def test_sort():
    hand = Hand(
        [
            Card(high=11, suit=2),
            Card(high=0, suit=0),
            Card(high=12, suit=3),
            Card(high=7, suit=2),
            Card(high=7, suit=1),
            Card(high=3, suit=1),
        ]
    )
    hand.sort()
    assert hand.hash() == "AsKh9h9d5d2c"


@pytest.mark.parametrize(
    "hand_hash, expected_same_kind, expected_straight, expected_suits",
    [
        (
            "2s5d9d9cKcAh",
            [[12, 11, 3, 0], [7], [], []],
            [],
            [[11, 7], [7, 3], [12], [0]],
        ),
        ("KsKd9d9cKcAh", [[12], [7], [11], []], [], [[11, 7], [11, 7], [12], [11]]),
        ("2s2dTd2cTc2h5s", [[3], [8], [], [0]], [], [[8, 0], [8, 0], [0], [3, 0]]),
        (
            "5s5dQdQcKcAh4s",
            [[12, 11, 2], [10, 3], [], []],
            [],
            [[11, 10], [10, 3], [12], [3, 2]],
        ),
        (
            "AsAd3d3c3hAh4s",
            [[2], [], [12, 1], []],
            [],
            [[1], [12, 1], [12, 1], [12, 2]],
        ),
        (
            "5s3d2d4c3cAh4s",
            [[12, 3, 0], [2, 1], [], []],
            [3],
            [[2, 1], [1, 0], [12], [3, 2]],
        ),
        (
            "Ts9d8d3c3hJh7s",
            [[9, 8, 7, 6, 5], [1], [], []],
            [9],
            [[1], [7, 6], [9, 1], [8, 5]],
        ),
        (
            "AsKd9dTcQcAhJs",
            [[11, 10, 9, 8, 7], [12], [], []],
            [12],
            [[10, 8], [11, 7], [12], [12, 9]],
        ),
        (
            "AsTd9d8cJc4h5s",
            [[12, 9, 8, 7, 6, 3, 2], [], [], []],
            [],
            [[9, 6], [8, 7], [2], [12, 3]],
        ),
        (
            "AsTd9dQcJc4h8s",
            [[12, 10, 9, 8, 7, 6, 2], [], [], []],
            [10],
            [[10, 9], [8, 7], [2], [12, 6]],
        ),
        (
            "AsTs9dQsJs4h8s",
            [[12, 10, 9, 8, 7, 6, 2], [], [], []],
            [10],
            [[], [7], [2], [12, 10, 9, 8, 6]],
        ),
        (
            "AdTd9dQdJd4d8d",
            [[12, 10, 9, 8, 7, 6, 2], [], [], []],
            [10],
            [[], [12, 10, 9, 8, 7, 6, 2], [], []],
        ),
        (
            "AsTd9dQdJd4h8d",
            [[12, 10, 9, 8, 7, 6, 2], [], [], []],
            [10],
            [[], [10, 9, 8, 7, 6], [2], [12]],
        ),
        (
            "AsAd9dKdKc4h4c",
            [[7], [12, 11, 2], [], []],
            [],
            [[11, 2], [12, 11, 7], [2], [12]],
        ),
    ],
)
def test_scan_same_kind_and_straight(
    hand_hash: str,
    expected_same_kind: List[List[int]],
    expected_straight: List[int],
    expected_suits: List[List[int]],
):
    hand = Hand(hand_hash=hand_hash)
    same_kind, straight, suits = hand._scan()
    assert same_kind == expected_same_kind
    assert straight == expected_straight
    assert suits == expected_suits


@pytest.mark.parametrize(
    "hand_hash, hand_combination",
    [
        ("Ks7d9c9d8sKhQh", "two pairs"),
        ("KsKd9c9d8sKhQh", "full house"),
        ("Ks7h9c9h8hKhQh", "flush"),
        ("Ks7d9c9d8sThQh", "pair"),
        ("Js7d9c9d8sThQh", "quinte"),
        ("As7d5c4d2s3hQh", "quinte"),
        ("KsKd9c9d9sKhQh", "full house"),
        ("KsKd9cKd8sKhQh", "square"),
        ("7s7d9c9d8s8h8h", "full house"),
        ("KsTs9s9d8sJsQs", "quinte flush"),
        ("7s8s9h4s7d4hKh", "two pairs"),
    ],
)
def test_combination(hand_hash: str, hand_combination: str):
    assert Hand(hand_hash=hand_hash).get_combination() == hand_combination


@pytest.mark.parametrize(
    "hand_hash1, hand_hash2",
    [
        ("KsJd9h5h6h2s3d", "QsJd9h5h6h2s3d"),
        ("KsJd9h5h6h5s3d", "QsJd8h5h6h5s3d"),
        ("KsJd9h5h6h5s3d", "QsJd9h5h6h5s2d"),
        ("Ts8c9h7c5s4d3h", "2s8c9h7c5s4d3h"),
        ("Ts8s9h7s5s4s3h", "Ts8c9h7cJs4d3h"),
    ],
)
def test_hand_values(hand_hash1, hand_hash2):
    assert Hand(hand_hash=hand_hash1) > Hand(hand_hash=hand_hash2)
