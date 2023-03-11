from abc import abstractmethod
from contextlib import suppress

from poqrl.hand.card import Card
from poqrl.hand.hand import Hand
from poqrl.player.utils import ActionError, SituationError
from poqrl.types.street import Street
from poqrl.types.action import *


class AbstractPlayer:
    """Abstract class that represents the player"""

    def __init__(
        self,
        stack: int = 100,
        name: str = "AbstractPlayer",
    ):
        self.table = None
        self.base_stack = stack
        self.stack = stack
        self.refill = 1
        self.chips_committed = 0
        self.name = name
        self.hand = Hand()
        self.cards = (None, None)  # useful for graphic display
        self.position = -1
        self.is_in_hand = True

    @abstractmethod
    def save(self, folder):
        pass

    @abstractmethod
    def load(self, folder):
        pass

    @abstractmethod
    def play_street(self, street: Street) -> Action:
        """Return the player action for street 'street number'"""
        if self.table.current_bet and self.chips_committed > self.table.current_bet:
            raise SituationError(
                f"{self.name} -- chips_committed ({self.chips_committed}) > \
                    current_bet ({self.table.current_bet})"
            )
        if (
            self.chips_committed == self.table.current_bet
            and self.table.current_bet > 0
            and (self.table.current_bet > 2 or street != 0)
        ):
            raise SituationError(
                f"{self.name} -- chips_committed ({self.chips_committed}) == \
                    current_bet ({self.table.current_bet}) and current_bet > 0"
            )
        return CHECK  # useless

    def get_chips_won(self):
        """Return the amount of chips (in blend) win (or lost) by the player"""
        return self.stack + self.chips_committed - self.refill * self.base_stack

    @abstractmethod
    def close_hand(self):
        """Method called at the end of the hand"""

    def reset_player(self):
        """Prepare the player for coming hand"""
        self.stack = self.base_stack
        self.refill = 1

    def sit_on_table(self, table, position):
        """Set the table configuration for the player"""
        self.position = position
        self.table = table

    def set_hand(self, card1: Card, card2: Card):
        """Set the player hand with the given cards"""
        self.hand.add_card(card1)
        self.hand.add_card(card2)
        self.cards = (card1, card2)  # for graphical interface

    def reset_hand(self):
        """Method called before a new hand"""
        self.hand = Hand()
        self.cards = (None, None)
        self.chips_committed = 0
        self.is_in_hand = True
        if self.stack <= 0:
            self.stack = self.base_stack
            self.refill += 1
        elif self.stack > 10 * self.base_stack:
            self.refill -= 9
            self.stack = self.stack - 9 * self.base_stack

    def commit_chips(self, chips_amount: int):
        """Put chips on the table.
        The amount of chips is removed from the stack to be added to the committed chips"""
        self.stack -= chips_amount
        self.chips_committed += chips_amount

    def call(self) -> Action:
        """Call the last bet. The stack and committed chips are updated accordingly"""
        if (
            self.chips_committed == self.table.current_bet
            and self.table.current_bet != 2  # the blend
        ):
            raise ActionError(
                f"{self.name}-- Call not compatible, as chips committed equal current \
                    bet ({self.chips_committed})"
            )
        amount_to_pay = self.table.current_bet - self.chips_committed
        chips_to_pay = min(amount_to_pay, self.stack)
        self.commit_chips(chips_to_pay)
        if self.stack == 0:
            self.table.player_all_in = True
        return CALL

    def raise_pot(self, bet_amount: int) -> Action:
        """Raise the pot.
        The stack and committed chips are updated accordingly,
         as well as the table variables"""
        current_bet = self.table.current_bet
        previous_bet = self.table.previous_bet
        if self.stack <= current_bet:
            return self.call()

        if (
            bet_amount - current_bet < current_bet - previous_bet
            and bet_amount < self.stack
        ):
            raise ActionError(
                f"{self.name} -- Raise amount ({bet_amount}) not compatible with \
                    precedent bet values ({current_bet} and {previous_bet})"
            )
        chips_to_pay = min(bet_amount - self.chips_committed, self.stack)
        self.commit_chips(chips_to_pay)
        self.table.previous_bet = current_bet
        self.table.current_bet = self.chips_committed
        if self.stack == 0:
            self.table.player_all_in = True
        return RAISE

    def fold(self) -> Action:
        """Fold the hand. The player will not play in the rest of the hand"""
        if self.chips_committed == self.table.current_bet:
            raise ActionError(
                f"{self.name} -- Fold not usefull as chips committed \
                    equals current bet ({self.chips_committed})"
            )
        with suppress(ValueError, AttributeError):
            for _, player_list in self.table.side_pots:
                player_list.remove(self.position)
        self.is_in_hand = False
        return FOLD

    def check(self) -> Action:
        """Check the pot"""
        if self.chips_committed < self.table.current_bet:
            raise ActionError(
                f"{self.name} -- Check not authorized as chips_committed \
                    ({self.chips_committed}) not equal to current_bet ({self.table.current_bet})"
            )
        if self.table.current_bet > 2:
            # TODO this implementation enables to manage the blends case but is not complete
            raise ActionError(
                f"{self.name} -- Cannot check when last bet is {self.table.current_bet}"
            )
        return CHECK

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
