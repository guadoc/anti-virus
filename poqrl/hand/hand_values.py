from typing import Dict
from pathlib import Path
import pickle


HAND_VALUES_HASH_PATH = Path("hand_values")
HAND_QUANTILE_VALUES_FOLDER = Path("store")


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
        with open(hand_value_file_name, "rb") as hand_value_file:
            hand_value_dict = pickle.load(hand_value_file)
        return hand_value_dict
    return {}


def load_hand_quantiles(n_cards: int, folder: Path):
    filename = f"hand_quantile_{n_cards}cards_of{7}_{10}.pkl"
    filepath = folder / filename
    if filepath.exists():
        with open(filepath, "rb") as file:
            quantile_values = pickle.load(file)
            print(
                f"File {filename} loaded with {len(quantile_values)} values for {n_cards}"
            )
            return quantile_values
    else:
        print(f"Filename {filename} does not exist in {folder}")
        return None


def save_hand_value_dict(n_card_hand: int, value_dict: Dict[str, float]) -> None:
    hand_value_file_name = HAND_VALUES_HASH_PATH / f"{n_card_hand}_card_hand_values.pkl"
    with open(hand_value_file_name, "wb") as hand_value_file:
        pickle.dump(value_dict, hand_value_file)
    # hand_value_file.close()


# HAND_AVG_VALUES = {n_card: load_hand_value_dict(n_card) for n_card in range(2, 7)}
HAND_AVG_VALUES = {n_card: load_hand_value_dict(n_card) for n_card in range(2, 5)}
HAND_7_QUANTILE_10_VALUES = {
    n_card: load_hand_quantiles(n_card, HAND_QUANTILE_VALUES_FOLDER)
    for n_card in [2, 3, 4, 5, 6]
}
