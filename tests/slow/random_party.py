import time
from tqdm import tqdm
import numpy as np

from antivir.table.abstract_table import AbstractTable
from antivir.player.player_random import PlayerRandom


def test_random_player_time():
    np.random.seed(77)
    player_list = [PlayerRandom(100, name=f"player {i}") for i in range(6)]
    table = AbstractTable(player_list)
    n_hand = 1000
    start_time = time.time()
    for _ in tqdm(range(n_hand)):
        table.play_hand()
    print(f"{n_hand} played in  {time.time() - start_time} seconds")
    assert False
