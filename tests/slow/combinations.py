from collections import defaultdict
from antivir.hand.hand import Hand
from antivir.hand.card import Card
from antivir.hand.utils import all_hands


def test_all_hands(n_card):
    combination_occurencies = defaultdict(int)
    for hand in all_hands(n_card):
        combination_occurencies[hand.get_combination()]
    return combination_occurencies


print(test_all_hands(5))
