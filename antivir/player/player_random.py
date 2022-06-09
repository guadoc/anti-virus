import numpy as np
from typing import Optional, List
from antivir.player.abstract_player import AbstractPlayer


from antivir.player.utils import SituationError


class PlayerRandom(AbstractPlayer):
    def __init__(
        self,
        stack: int = 100,
        name="Random Player",
        p_bet: Optional[List[int]] = None,
        p_nobet: Optional[List[int]] = None,
    ):
        super().__init__(stack=stack, name=name)
        if p_bet:
            self.p_bet = p_bet
        else:
            self.p_bet = [0.05, 0.3, 0.65]
        if p_nobet:
            self.p_nobet = p_nobet
        else:
            self.p_nobet = [0.35, 0.65]

    def play_street(self, street_number: int):
        if self.chips_committed < self.table.current_bet:
            action = np.random.choice(["raise", "call", "fold"], p=self.p_bet)
        else:
            action = np.random.choice(["raise", "check"], p=self.p_nobet)
        return self.play_from_action(action)

    def play_from_action(self, action: str):
        if action == "raise":
            if self.stack <= self.table.current_bet:
                return self.call()
            if self.table.current_bet > 0:
                raise_amount = 3 * self.table.current_bet - self.table.previous_bet
            else:
                raise_amount = 2
            return self.raise_pot(raise_amount)
        elif action == "call":
            return self.call()
        elif action == "check":
            return self.check()
        else:
            return self.fold()
