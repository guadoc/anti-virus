from typing import List

# from poqrl.hand.hand import Hand
import poqrl.hand.hand as hand_lib
from poqrl.hand.card import Card


def all_hands(n_cards: int):
    all_cards = [Card(id=id) for id in range(52)]
    max_per_index = [52 - n_cards + i for i in range(n_cards)]
    hand_ids = list(range(n_cards))

    while hand_ids:
        while len(hand_ids) != n_cards:
            hand_ids.append(hand_ids[-1] + 1)
        yield hand_lib.Hand(card_list=[all_cards[id] for id in hand_ids])
        while hand_ids and hand_ids[-1] == max_per_index[len(hand_ids) - 1]:
            hand_ids.pop()
        if hand_ids:
            hand_ids[-1] += 1


def all_hands_from_cards(n_cards: int, card_list: List[Card]):
    n_cards -= len(card_list)
    card_ids = [card.id for card in card_list]
    all_cards = [Card(id=id) for id in range(52)]
    max_per_index = [52 - n_cards + i for i in range(n_cards)]
    hand_ids = list(range(n_cards))
    while hand_ids:
        while len(hand_ids) != n_cards:
            hand_ids.append(hand_ids[-1] + 1)
        if all([card_id not in hand_ids for card_id in card_ids]):
            yield hand_lib.Hand(
                card_list=[all_cards[id] for id in hand_ids] + list(card_list)
            )
        while hand_ids and hand_ids[-1] == max_per_index[len(hand_ids) - 1]:
            hand_ids.pop()
        if hand_ids:
            hand_ids[-1] += 1
