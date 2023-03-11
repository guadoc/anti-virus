import numpy as np
from typing import Optional, List

from poqrl.player.abstract_player import AbstractPlayer
from poqrl.player.player_log import PlayerLog
from poqrl.player.utils import SituationError
from poqrl.types.street import Street
from poqrl.types.action import *


# class PlayerRandom(PlayerLog):
class PlayerRandom(AbstractPlayer):
    def __init__(
        self,
        stack: int = 100,
        name="Random Player",
        aggressivity: float = 0.1,
        loosiness: float = 0.3,
    ):
        super().__init__(stack=stack, name=name)
        self.p_call_all = [loosiness, 1 - loosiness]
        self.p_aggro_all = [aggressivity, 1 - aggressivity]

        self.call_all = False
        self.aggro_all = False

    def reset_hand(self):
        self.call_all = np.random.choice([True, False], p=self.p_call_all)
        self.aggro_all = np.random.choice([True, False], p=self.p_aggro_all)
        super().reset_hand()

    def play_street(self, street: Street) -> Action:
        # super().play_street(street)
        if self.chips_committed < self.table.current_bet:
            if self.call_all:
                return self.call()
            else:
                return self.fold()
        else:
            if self.aggro_all:
                if self.stack <= self.table.current_bet:
                    return self.call()
                if self.table.current_bet > 0:
                    bet_amount = 3 * self.table.current_bet - self.table.previous_bet
                else:
                    bet_amount = int(self.table.pot / 2)
                return self.raise_pot(bet_amount)
            else:
                return self.check()
