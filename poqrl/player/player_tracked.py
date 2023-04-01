from collections import defaultdict
from typing import Dict

from poqrl.player.abstract_player import AbstractPlayer
from poqrl.types.street import Street
from poqrl.types.action import FOLD, RAISE, CALL, CHECK, Action


class PlayerTracked(AbstractPlayer):
    """Player that incorporate a self tracker. It is used to check the player statistics"""

    def __init__(
        self,
        stack: int = 100,
        name: str = "AbstractPlayer",
    ):
        super().__init__(stack, name)
        self.tracker = PlayerTracked.empty_tracker()

    @staticmethod
    def empty_tracker() -> Dict:
        """return a virgin tracker"""
        return {street.name: defaultdict(int) for street in Street}

    @staticmethod
    def update_tracker(tracker: Dict, action: Action, street: Street):
        """update the tracker figure, from the player current action"""
        tracker[street.name][action.id] += 1
        tracker[street.name]["total"] += 1
        return tracker

    @staticmethod
    def display_tracker(tracker):
        """print the tracked statistics"""
        for street_name, street_tracker in tracker.items():
            print(street_name)
            if "total" in street_tracker:
                print(f"   total: {street_tracker['total']}")
                tot_hand = street_tracker["total"]
                for action in [FOLD, RAISE, CALL, CHECK]:
                    print(
                        f"   {action.name}: {100 *street_tracker[action.id] / tot_hand:.2f}%"
                    )

    def reset_player(self):
        super().reset_player()
        self.tracker = self.empty_tracker()

    def play_action(self, street, action, from_bet) -> Action:
        self.tracker = self.update_tracker(self.tracker, action, street)
        return super().play_action(street, action, from_bet)
