from enum import IntEnum, unique


@unique
class Street(IntEnum):
    """Define the different street order"""

    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
