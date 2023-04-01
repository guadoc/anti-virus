from pathlib import Path
from typing import List, Type

from tqdm import tqdm
import tensorflow as tf

from poqrl.table.abstract_table import AbstractTable
from poqrl.player.abstract_player import AbstractPlayer
from poqrl.player.player_tracked import PlayerTracked
from poqrl.types.street import Street


def train_bot(
    bot: PlayerTracked,
    competitors: List[PlayerTracked],
    n_hand: int = 1000,
    saving_folder: Path | None = None,
    checkpoint: int = 100,
):
    print(f"Training {bot.name}")
    for competitor in competitors:
        competitor.reset_player()
        competitor.training = False
    bot.reset_player()
    bot.training = True

    table = AbstractTable(player_list=[bot] + competitors)

    for _ in tqdm(range(n_hand)):
        table.play_hand()
        # if hand % checkpoint == 0:
        #     if saving_folder is not None:
        #         bot.save_data(saving_folder)
    # PlayerTracked.display_tracker(bot.tracker)


def test_bot(bot: PlayerTracked, competitors: List[PlayerTracked], n_hand=1000):
    print(f"Testing {bot.name}")
    for competitor in competitors:
        competitor.reset_player()
        competitor.training = False
    bot.reset_player()
    bot.training = False

    table = AbstractTable(player_list=[bot] + competitors)
    for _ in tqdm(range(n_hand)):
        table.play_hand()
    print(table)
    PlayerTracked.display_tracker(bot.tracker)


def train_loop(
    bot: PlayerTracked,
    init_player_list: List[AbstractPlayer],
    competitor_class: Type[AbstractPlayer],
    bot_name,
    n_training,
    n_testing,
    n_training_loop,
    saving_folder,
):
    try:
        for i in range(1):
            train_bot(bot, init_player_list, n_training)
            test_bot(bot, init_player_list, n_testing)

        bot.save_data(saving_folder)
        print("END OF WARMING")
        competitors = [competitor_class(name=f"Player {i}") for i in range(5)]
        for loop in range(n_training_loop):
            print(f"Loop : {loop}")
            for competitor in competitors:
                competitor.load_data_from_path(saving_folder / bot_name)
            for i in range(2):
                train_bot(bot, competitors, n_training, saving_folder, checkpoint=400)
                bot.save_data(saving_folder)
                test_bot(bot, competitors, n_testing)
    except KeyboardInterrupt:
        bot.save_data(saving_folder)
        return bot, None

    return bot, competitors
