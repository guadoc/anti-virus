from pathlib import Path
from typing import List

from tqdm import tqdm

from poqrl.table.abstract_table import AbstractPlayer, AbstractTable


def train_bot(
    bot: AbstractPlayer,
    competitors: List[AbstractPlayer],
    n_hand: int = 1000,
    saving_folder: Path | None = None,
    checkpoint: int = 100,
):
    print(f"Training {bot.name}")
    for competitor in competitors:
        competitor.reset_player()
    bot.reset_player()

    for competitor in competitors:
        competitor.training = False
    bot.training = True

    table = AbstractTable(player_list=[bot] + competitors)

    checkpoint = 100
    for hand in tqdm(range(n_hand)):
        table.play_hand()
        if hand % checkpoint == 0:
            if saving_folder is not None:
                bot.save_data(saving_folder)


def test_bot(bot: AbstractPlayer, competitors: List[AbstractPlayer], n_hand=1000):
    print(f"Testing {bot.name}")
    for competitor in competitors:
        competitor.reset_player()
    bot.reset_player()

    bot.training = False
    table = AbstractTable(player_list=competitors + [bot])
    for _ in tqdm(range(n_hand)):
        table.play_hand()
    print(table)
    bot.display_tracker()
