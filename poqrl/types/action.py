from dataclasses import dataclass


@dataclass
class Action:
    value: int
    id: int
    name: str

    def __equal__(self, other):
        return self.id == other.id


RAISE = Action(1, 0, "raise")
CHECK = Action(0, 1, "check")
CALL = Action(0, 2, "call")
FOLD = Action(2, 3, "fold")
