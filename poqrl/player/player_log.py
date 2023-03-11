from poqrl.player.abstract_player import AbstractPlayer
from poqrl.types.action import Action


class PlayerLog(AbstractPlayer):
    """Player that prints its action. It is used for debug for instance"""

    def __init__(
        self,
        stack: int = 100,
        name: str = "Chatty player",
    ):
        super().__init__(stack, name)

    def close_hand(self):
        super().close_hand()

    def play_street(self, street) -> Action:
        return super().play_street(street)

    def call(self) -> str:
        print(
            f"{self.name}({self.stack}) calls \
                {min(self.table.current_bet - self.chips_committed, self.stack)}"
        )
        return super().call()

    def raise_pot(self, bet_amount: int) -> str:
        print(
            f"{self.name}({self.stack}) raises {min(bet_amount - self.chips_committed, self.stack)}"
        )
        return super().raise_pot(bet_amount)

    def fold(self):
        print(f"{self.name}({self.stack}) folds")
        return super().fold()

    def check(self):
        print(f"{self.name}({self.stack}) checks")
        return super().check()
