from tqdm import tqdm
import typer
from poqrl.hand.utils import all_hands
from poqrl.hand.hand_values import (
    save_hand_value_dict,
    HAND_2CARDS_VALUES,
    HAND_3CARDS_VALUES,
    HAND_4CARDS_VALUES,
    HAND_5CARDS_VALUES,
    HAND_6CARDS_VALUES,
)


def main(n_card_hand: int):
    if n_card_hand == 2:
        hand_values_hash_table = HAND_2CARDS_VALUES
    elif n_card_hand == 3:
        hand_values_hash_table = HAND_3CARDS_VALUES
    elif n_card_hand == 4:
        hand_values_hash_table = HAND_4CARDS_VALUES
    elif n_card_hand == 5:
        hand_values_hash_table = HAND_5CARDS_VALUES
    elif n_card_hand == 6:
        hand_values_hash_table = HAND_6CARDS_VALUES
    else:
        raise ValueError(f"No hash table for hand of size {n_card_hand}")

    try:
        for hand in tqdm(all_hands(n_card_hand)):
            hand_key = hand.hash()
            if hand_key not in hand_values_hash_table:
                hand_values_hash_table[
                    hand_key
                ] = hand.compute_7cards_hand_average_value()
    except KeyboardInterrupt:
        save_hand_value_dict(n_card_hand, hand_values_hash_table)


if __name__ == "__main__":
    typer.run(main)
