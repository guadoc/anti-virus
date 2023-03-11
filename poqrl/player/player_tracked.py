from collections import defaultdict
from typing import Dict

from poqrl.player.abstract_player import AbstractPlayer
from poqrl.types.street import Street
from poqrl.types.action import FOLD, RAISE, CALL, CHECK, Action


class PlayerTracked(AbstractPlayer):
    def __init__(
        self,
        stack: int = 100,
        name: str = "AbstractPlayer",
    ):
        super().__init__(stack, name)
        self.tracker = PlayerTracked.empty_tracker()

    @staticmethod
    def empty_tracker() -> Dict:
        return {street: defaultdict(int) for street in Street}

    @staticmethod
    def update_tracker(tracker: Dict, action: Action, street: Street):
        tracker[street][action.id] += 1
        tracker[street]["total"] += 1
        return tracker

    @staticmethod
    def display_tracker(tracker):
        for street, street_tracker in tracker.items():
            print(street.name)
            tot_hand = street_tracker["total"]
            for action in [FOLD, RAISE, CALL, CHECK]:
                print(
                    f"   {action.name}: {100 *street_tracker[action.id] / tot_hand:.2f}"
                )

        print(tracker)

    def reset_player(self):
        super().reset_player()
        self.tracker = self.empty_tracker()

    def play_street(self, street) -> Action:
        action = super().play_street(street)
        self.tracker = self.update_tracker(self.tracker, action, street)
        return action
