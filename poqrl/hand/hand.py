from typing import List, Optional, Tuple
from math import comb

import numpy as np

from poqrl.hand.card import Card, High
from poqrl.hand.deck import Deck

import poqrl.hand.utils as util

HAND_MAX_VAL = 2598956
HAND_MIN_VAL = 1020


class Hand:
    """Define a hand"""

    def __init__(
        self, card_list: Optional[List[Card]] = None, hand_hash: Optional[str] = None
    ):
        if card_list:
            self.cards = card_list
        elif hand_hash:
            self.cards = [
                Card(card_hash=hand_hash[i : i + 2])
                for i in range(0, len(hand_hash), 2)
            ]
        else:
            self.cards = []
        self._value = None
        self._avg_value = None

    @property
    def value(self):
        """Return the absolute value of the hand.
        This value indicates the number of hand that are beat by the hand.
        If not computed yet, it calls 'evaluate()' to calculate the value"""
        if self._value is None:
            self._value = self.evaluate()
        return self._value

    @property
    def get_avg_value(self):
        if self._avg_value is None:
            self._avg_value = self.compute_mc_avg_value()
        return self._avg_value

    def compute_7cards_hand_average_value(self):
        avg_value = 0
        hand_number = 0
        for complete_hand in util.all_hands_from_cards(7, self.cards):
            hand_number += 1
            avg_value = (
                avg_value * ((hand_number - 1) / hand_number)
                + complete_hand.value / hand_number
            )
        return avg_value

    def __le__(self, hand):
        return self.value <= hand.value

    def __lt__(self, hand):
        return self.value < hand.value

    def __ge__(self, hand):
        return self.value >= hand.value

    def __gt__(self, hand):
        return self.value > hand.value

    def add_card(self, card: Card):
        """Add a card to the hand.
        When adding a card, the value of the hand should be reevaluated"""
        self.cards.append(card)
        self._value = None
        self._avg_value = None

    def sort(self):
        """Sort the list of cards.
        It is usefull for the scan of the hand and for its hash key"""
        self.cards.sort(reverse=True)

    def hash(self):
        """Compute the hash key of a hand"""
        self.sort()
        return "".join(card.hash() for card in self.cards)

    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards)

    def compute_mc_avg_value(self, n_draw: int = 1000) -> float:
        n_card = len(self.cards)
        avg_value = 0.0
        for draw in range(n_draw):
            cards = list(self.cards)
            deck = Deck(list(cards))
            hand = Hand(cards)
            for _ in range(7 - n_card):
                hand.add_card(deck.distribute_random_card())
            val = hand.value
            avg_value = (avg_value / (draw + 1)) * draw + val / (draw + 1)
        return avg_value

    @staticmethod
    def _scan_sorted_hand(
        card_array,
    ) -> Tuple[List[List[High]], List[High], List[List[High]]]:
        """Scan a sorted hand
        Returns: three lists
        """
        suits = [[], [], [], []]
        same_kind = [[], [], [], []]
        straight = []

        similar = 0
        successive = 1
        previous_high = card_array[0][0]
        suits[card_array[0][1]].append(previous_high)

        for card in card_array[1:]:
            high = card[0]
            suit = card[1]
            suits[suit].append(high)
            if high == previous_high:
                similar += 1
            else:
                if high == previous_high - 1:
                    successive += 1
                else:
                    if successive >= 5:
                        straight.append(previous_high + successive - 1)
                    successive = 1

                same_kind[similar].append(previous_high)
                similar = 0
                previous_high = high

        same_kind[similar].append(high)
        if successive >= 5:
            straight.append(previous_high + successive - 1)
        if successive == 4 and high == 0 and card_array[0][0] == 12:
            straight.append(previous_high + successive - 1)

        return same_kind, straight, suits

    def _scan(self):
        """Scan the hand to get information about
        high and suit occurencies"""
        self.sort()
        card_array = np.array([[card.high, card.suit] for card in self.cards])
        return self._scan_sorted_hand(card_array)

    def get_combination(self):
        "Get the combination name of the hand"
        same_kind, straight, suits = self._scan()
        return self._get_combination_from_scan(same_kind, straight, suits)

    def _get_combination_from_scan(
        self, same_kind: List[List[High]], straight: List[High], suits: List[List[High]]
    ):
        flush = self._biggest_flush(suits)
        if flush:
            if self._is_quinte_from_cards(flush):
                return "quinte flush"
            return "flush"
        if self._is_square(same_kind):
            return "square"
        elif self._is_fullhouse(same_kind):
            return "full house"
        elif self._is_quinte(straight):
            return "quinte"
        elif self._is_set(same_kind):
            return "set"
        elif self._is_twopairs(same_kind):
            return "two pairs"
        elif self._is_pair(same_kind):
            return "pair"
        else:
            return "high"

    def evaluate(self) -> int:
        """Evaluate the relative value of the hand"""
        same_kind, straight, suits = self._scan()
        flush = self._biggest_flush(suits)
        if flush:
            quinte_high = self._is_quinte_from_cards(flush)
            if quinte_high:
                return self._quintflush_value(quinte_high)
            return self._flush_value(flush)  # no better combination with 7 cards
        if self._is_square(same_kind):
            return self._square_value(same_kind)
        elif self._is_fullhouse(same_kind):
            return self._fullhouse_value(same_kind)
        elif self._is_quinte(straight):
            return self._quinte_value(straight[0])
        elif self._is_set(same_kind):
            return self._set_value(same_kind[2][0], same_kind[0])
        elif self._is_twopairs(same_kind):
            return self._twopairs_value(
                same_kind[1][0], same_kind[1][1], same_kind[0][0]
            )
        elif self._is_pair(same_kind):
            return self._pair_value(same_kind[1][0], same_kind[0])
        else:
            return self._high_value(same_kind[0])

    @staticmethod
    def _is_quinte_from_cards(suits: List[High]) -> int:
        previous_high = suits[0]
        successive = 1
        for high in suits[1:]:
            if high == previous_high - 1:
                successive += 1
            else:
                if successive >= 5:
                    return (
                        previous_high + successive - 1
                    )  # no other possibility of straight
                successive = 1
            previous_high = high
        if successive >= 5 or (successive == 4 and high == 0 and suits[0] == 12):
            return high + successive - 1
        return 0

    @staticmethod
    def _quintflush_value(high_value) -> int:
        return 2598920 + 4 * (high_value - 3)

    @staticmethod
    def _is_square(same_kind: List[List[int]]) -> bool:
        return same_kind[3]

    @staticmethod
    def _square_value(same_kind: List[List[int]]) -> int:
        val = 2598296
        val_square = same_kind[3][0]
        val += 48 * val_square
        val_single = 0
        if same_kind[0]:
            val_single = max(val_single, same_kind[0][0])
        if same_kind[1]:
            val_single = max(val_single, same_kind[1][0])
        if same_kind[2]:
            val_single = max(val_single, same_kind[2][0])
        if val_single < val_square:
            val += 4 * val_single
        else:
            val += 4 * (val_single - 1)
        return val

    @staticmethod
    def _biggest_flush(suits: List[List[High]]) -> List[High]:
        if len(suits[0]) >= 5:
            return suits[0]
        elif len(suits[1]) >= 5:
            return suits[1]
        elif len(suits[2]) >= 5:
            return suits[2]
        elif len(suits[3]) >= 5:
            return suits[3]
        else:
            return []

    def _is_flush(self, suits: List[List[High]]) -> bool:
        return len(self._biggest_flush(suits)) > 0

    @staticmethod
    def _flush_value(suits: List[High]) -> int:
        val = 2589444
        for i in range(5):
            val += 4 * comb(suits[i], 5 - i)
        return val

    @staticmethod
    def _is_quinte(straight: List[int]) -> bool:
        return straight

    @staticmethod
    def _quinte_value(quinte_high: High) -> int:
        val = 2579244
        val += (quinte_high - 3) * 1020
        return val

    @staticmethod
    def _is_fullhouse(same_kind: List[List[int]]) -> bool:
        return len(same_kind[2]) and (len(same_kind[1]) or len(same_kind[2]) >= 2)

    @staticmethod
    def _fullhouse_value(same_kind: List[List[int]]) -> int:
        val = 2594552
        val_set = same_kind[2][-1]
        val += 288 * val_set
        val_pair = 0
        if same_kind[1]:
            val_pair = same_kind[1][-1]
        if len(same_kind[2]) > 1:
            val_pair = max(val_pair, same_kind[2][-2])
        if val_set > val_pair:
            val += 6 * val_pair
        else:
            val += 6 * (val_pair - 1)
        return val

    @staticmethod
    def _is_set(same_kind: List[List[High]]) -> bool:
        return len(same_kind[2])

    @staticmethod
    def _set_value(set_high: High, single_highs: List[High]) -> int:
        val = 2524332
        val += set_high * 4224
        val += comb(single_highs[0], 2) * 16
        val += single_highs[1] * 4
        return val

    @staticmethod
    def _is_twopairs(same_kind: List[List[High]]) -> bool:
        return len(same_kind[1]) > 1

    @staticmethod
    def _twopairs_value(
        big_pair_high: int, small_pair_high: int, single_high: int
    ) -> int:
        val = 2400780
        val += comb(big_pair_high, 2) * 1584
        val += small_pair_high * 264
        if single_high < small_pair_high:
            val += 4 * (single_high - 2)
        elif single_high > big_pair_high:
            val += 4 * single_high
        else:
            val += 4 * (single_high - 1)

        return val

    @staticmethod
    def _is_pair(same_kind: List[List[int]]) -> bool:
        return len(same_kind[1])

    @staticmethod
    def _pair_value(pair_value: High, single_highs: List[List[High]]) -> int:
        val = 1302540
        val += pair_value * 84480
        for i in range(3):
            val += comb(single_highs[i], 3 - i) * pow(4, 3 - i)
        return val

    @staticmethod
    def _high_value(reversed_sorted_high: List[High]) -> int:
        val = 0
        for i in range(5):
            val += comb(reversed_sorted_high[i], 5 - i) * 1020
        return val
