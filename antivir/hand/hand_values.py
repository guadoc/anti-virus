from typing import Dict
from pathlib import Path
import pickle


HAND_VALUES_HASH_PATH = Path("hand_values")


def load_hand_value_dict(n_card_hand: int) -> Dict[str, float]:
    """Load a hash table (dictionnary) with hand values.
        The hand concerned are not complete (< 7 cards),
        and the value are the average value when completed into a 7 cards hand
    Args:
        n_card_hand: the number of card in the hands
    Returns:
        a hash table with
            key: the hand hash_key
            value: the average value of the hand when completed to 7 cards
            if the file do not exist, an empty dictionnary is returned"""

    hand_value_file_name = HAND_VALUES_HASH_PATH / f"{n_card_hand}_card_hand_values.pkl"
    if hand_value_file_name.exists():
        hand_value_file = open(hand_value_file_name, "rb")
        return pickle.load(hand_value_file)
    return {}


HAND_2CARDS_VALUES = load_hand_value_dict(2)
HAND_3CARDS_VALUES = load_hand_value_dict(3)
HAND_4CARDS_VALUES = load_hand_value_dict(4)
HAND_5CARDS_VALUES = load_hand_value_dict(5)
HAND_6CARDS_VALUES = load_hand_value_dict(6)


def save_hand_value_dict(n_card_hand: int, value_dict: Dict[str, float]) -> None:
    hand_value_file_name = HAND_VALUES_HASH_PATH / f"{n_card_hand}_card_hand_values.pkl"
    hand_value_file = open(hand_value_file_name, "wb")
    pickle.dump(value_dict, hand_value_file)
    hand_value_file.close()
