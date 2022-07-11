from tqdm import tqdm
import typer
from poqrl.hand.utils import all_hands
from poqrl.hand.hand_values import HAND_AVG_VALUES, save_hand_value_dict


def main(n_card_hand: int):

    if not n_card_hand in HAND_AVG_VALUES:
        raise ValueError(f"No hash table for hand of size {n_card_hand}")

    hand_values_hash_table = HAND_AVG_VALUES[n_card_hand]

    try:
        for hand in tqdm(all_hands(n_card_hand)):
            hand_key = hand.hash
            if hand_key not in hand_values_hash_table:
                hand_values_hash_table[
                    hand_key
                ] = hand.compute_7cards_hand_average_value()
        save_hand_value_dict(n_card_hand, hand_values_hash_table)
    except KeyboardInterrupt:
        save_hand_value_dict(n_card_hand, hand_values_hash_table)


if __name__ == "__main__":
    typer.run(main)
