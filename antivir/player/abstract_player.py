from abc import abstractmethod
from contextlib import suppress

from antivir.hand.card import Card
from antivir.hand.hand import Hand
from antivir.player.utils import ActionError
from antivir.player.utils import SituationError


# from antivir.table.abstract_table import AbstractTable


class AbstractPlayer:
    """Abstract class that represents the decision maker as a player"""

    def __init__(
        self,
        stack: int = 100,
        name: str = "AbstractPlayer",
    ):
        self.table = None
        self.stack = stack
        self.base_stack = stack
        self.chips_committed = 0
        self.name = name
        self.hand = Hand()
        self.cards = (None, None)  # useful for graphic display
        self.position = -1
        self.is_in_hand = True
        self.refill = 1

    @abstractmethod
    def play_street(self, street_number: int) -> str:
        if self.table.current_bet and self.chips_committed > self.table.current_bet:
            raise SituationError(
                f"{self.name} -- chips_committed ({self.chips_committed}) > current_bet ({self.table.current_bet})"
            )
        if (
            self.chips_committed == self.table.current_bet
            and self.table.current_bet > 0
            and (self.table.current_bet > 2 or street_number != 0)
        ):
            raise SituationError(
                f"{self.name} -- chips_committed ({self.chips_committed}) == current_bet ({self.table.current_bet})\
                     and current_bet > 0"
            )

    def get_chips_won(self):
        return self.stack + self.chips_committed - self.refill * self.base_stack

    @abstractmethod
    def close_hand(self):
        pass

    def sit_on_table(self, table, position):
        self.position = position
        self.table = table

    def set_hand(self, card1: Card, card2: Card):
        self.hand.add_card(card1)
        self.hand.add_card(card2)
        self.cards = (card1, card2)  # for graphical interface

    def reset_hand(self):
        self.hand = Hand()
        self.cards = (None, None)
        self.chips_committed = 0
        self.is_in_hand = True
        if self.stack <= 0:
            self.stack = self.base_stack
            self.refill += 1

    def commit_chips(self, chips_amount: int):
        self.stack -= chips_amount
        self.chips_committed += chips_amount

    def call(self):
        if (
            self.chips_committed == self.table.current_bet
            and self.table.current_bet != 2  # the blend
        ):
            raise ActionError(
                f"{self.name}--Call not compatible, as chips committed equal current bet ({self.chips_committed})"
            )
        amount_to_pay = self.table.current_bet - self.chips_committed
        chips_to_pay = min(amount_to_pay, self.stack)
        self.commit_chips(chips_to_pay)
        if self.stack == 0:
            self.table.player_all_in = True
        # print(f"{self.name}({self.stack}) calls {chips_to_pay}")
        return "call"

    def raise_pot(self, bet_amount: int):
        current_bet = self.table.current_bet
        previous_bet = self.table.previous_bet
        print("--------")
        print(self.position)
        print(current_bet)
        print(previous_bet)
        if self.stack <= current_bet:
            return self.call()

        if (
            bet_amount - current_bet < current_bet - previous_bet
            and bet_amount < self.stack
        ):
            raise ActionError(
                f"{self.name}--Raise amount ({bet_amount}) not compatible with precedent bet values ({current_bet} and {previous_bet})"
            )
        chips_to_pay = min(bet_amount - self.chips_committed, self.stack)
        self.commit_chips(chips_to_pay)
        self.table.previous_bet = current_bet
        self.table.current_bet = self.chips_committed
        if self.stack == 0:
            self.table.player_all_in = True
        # print(f"{self.name}({self.stack}) raises {chips_to_pay}")
        return "raise"

    def fold(self):
        if self.chips_committed == self.table.current_bet:
            raise ActionError(
                f"{self.name}--Fold not usefull as chips committed equals current bet ({self.chips_committed})"
            )
        with suppress(ValueError, AttributeError):
            for _, player_list in self.table.side_pots:
                player_list.remove(self.position)
        self.is_in_hand = False
        # print(f"{self.name}({self.stack}) folds")
        return "fold"

    def check(self):
        # print(f"{self.name}({self.stack}) checks")
        if self.chips_committed < self.table.current_bet:
            raise ActionError(
                f"{self.name}--Check not authorized as chips_committed ({self.chips_committed}) not equal to current_bet ({self.table.current_bet})"
            )
        if self.table.current_bet > 2:
            # TODO this implementation enables to manage the blends case but is not complete
            raise ActionError(
                f"{self.name}--Cannot check when last bet is {self.table.current_bet}"
            )
        return "check"

    def __str__(self):
        player_string = (
            f"{self.name} - stack({self.refill}): {self.stack}({self.chips_committed})"
        )
        if self.is_in_hand:
            player_string += " -- in hand"
        else:
            player_string += " -- not in hand"

        if self.cards[0] and self.cards[0]:
            player_string += f" -- {str(self.cards[0])}{str(self.cards[1])}"

        return player_string
