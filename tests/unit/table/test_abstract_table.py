from typing import List, Tuple, Union
import pytest

from poqrl.player.abstract_player import AbstractPlayer
from poqrl.table.abstract_table import AbstractTable
from poqrl.hand.hand import Hand


class PlayerMock(AbstractPlayer):
    def __init__(
        self, stack: int, actions: List[Union[str, Tuple[str, int]]], name: str = None
    ):
        super().__init__(stack, name=name)
        self.actions = actions

    def sit_on_table(self, table, position):
        super().sit_on_table(table, position)
        self.name = f"player {self.position}"

    def play_street(self, street_number: int):
        play = self.actions[0]
        self.actions = self.actions[1:]
        if isinstance(play, tuple):
            return self.raise_pot(play[1])
        else:
            if play == "fold":
                return self.fold()
            elif play == "check":
                return self.check()
            else:
                return self.call()


@pytest.mark.parametrize(
    "chips_committed_list, initial_pot, initial_side_pots, \
        player_all_in, expected_pot, expected_side_pots",
    [
        (
            [10, 10, 10],  # chips_committed_list
            10,  # initial_pot
            [],  # initial_side_pots
            False,  # player_all_in
            40,  # expected_pot
            [],  # expected_side_pots
        ),
        (
            [10, 10, 10, 0],  # chips_committed_list
            12,  # initial_pot
            [[8, [0, 1, 2, 3]]],  # initial_side_pots
            False,  # player_all_in
            42,  # expected_pot
            [[8, [0, 1, 2, 3]]],  # expected_side_pots
        ),
        (
            [10, 10, 8, 0],  # chips_committed_list
            12,  # initial_pot
            [[8, [0, 1, 2, 3]]],  # initial_side_pots
            True,  # player_all_in
            4,  # expected_pot
            [[8, [0, 1, 2, 3]], [36, [0, 1, 2]]],  # expected_side_pots
        ),
        (
            [10, 10, 14, 0],  # chips_committed_list
            12,  # initial_pot
            [[8, [0, 1, 2, 3]]],  # initial_side_pots
            True,  # player_all_in
            4,  # expected_pot
            [[8, [0, 1, 2, 3]], [42, [0, 1, 2]]],  # expected_side_pots
        ),
        (
            [10, 10, 14, 8],  # chips_committed_list
            12,  # initial_pot
            [[8, [0, 1, 2, 3]]],  # initial_side_pots
            True,  # player_all_in
            4,  # expected_pot
            [
                [8, [0, 1, 2, 3]],
                [44, [0, 1, 2, 3]],
                [6, [0, 1, 2]],
            ],  # expected_side_pots
        ),
        (
            [14, 8, 14, 8, 0],  # chips_committed_list
            12,  # initial_pot
            [[8, [0, 1, 2, 3, 4]]],  # initial_side_pots
            True,  # player_all_in
            12,  # expected_pot
            [
                [8, [0, 1, 2, 3, 4]],
                [44, [0, 1, 2, 3]],
            ],  # expected_side_pots
        ),
        # (
        #     [2, 6, 16],  # chips_committed_list
        #     12,  # initial_pot
        #     [],  # initial_side_pots
        #     True,  # player_all_in
        #     12,  # expected_pot
        #     [
        #         [8, [0, 1, 2, 3, 4]],
        #         [44, [0, 1, 2, 3]],
        #     ],  # expected_side_pots
        # ),
    ],
)
def test_gather_pot(
    chips_committed_list,
    initial_pot,
    initial_side_pots,
    player_all_in,
    expected_pot,
    expected_side_pots,
):
    player_list = [AbstractPlayer() for _ in chips_committed_list]
    for player, chips_committed in zip(player_list, chips_committed_list):
        player.chips_committed = chips_committed

    table = AbstractTable(player_list=player_list)
    table.pot = initial_pot
    table.side_pots = initial_side_pots
    table.player_all_in = player_all_in
    table.current_bet = 10
    table.gather_chips_and_continue()
    assert table.side_pots == expected_side_pots
    assert table.pot == expected_pot


@pytest.mark.parametrize(
    "player_config_list, side_pots, expected_stacks",
    [
        (
            [(100, "Ks9hJdKdQs4h3d"), (90, "Jh8s9cTc8c7s5d"), (70, "8d9dTd8h7c5s6d")],
            [[16, [0, 1, 2]], [4, [1, 2]]],
            [100, 110, 70],
        ),
        (
            [
                (100, "Ks9hJdKdQs4h3d"),
                (90, "Ks9hJdKdQs4d3h"),
                (70, "8d9dTd8h7c5s6d"),
                (30, "8d5dTd8h7c3s6d"),
            ],
            [[16, [0, 1, 2, 3]], [5, [0, 1, 3]]],
            [102, 93, 86, 30],
        ),
    ],
)
def test_assign_pots(player_config_list, side_pots, expected_stacks):
    player_list = []
    for stack, hand_hash in player_config_list:
        player = AbstractPlayer()
        player.hand = Hand(hand_hash=hand_hash)
        player.stack = stack
        player_list.append(player)

    table = AbstractTable(player_list=player_list)
    table.side_pots = side_pots
    table.assign_pots()
    stacks = [player.stack for player in table.players]
    assert stacks == expected_stacks


@pytest.mark.parametrize(
    "player_conf_list, expected_chips_committeds, expected_stacks, \
    expected_is_in_hands",
    [
        (
            [(100, ["check"]), (80, ["call"])],  # player_conf_list
            [2, 2],  # expected_chips_committeds
            [98, 78],  # expected_stacks
            [True, True],  # expected_is_in_hands
        ),
        (
            [
                (100, [("raise", 10)]),
                (80, ["fold"]),
                (70, ["call"]),
            ],  # player_conf_list
            [10, 1, 10],  # expected_chips_committeds
            [90, 79, 60],  # expected_stacks
            [True, False, True],  # expected_is_in_hands
        ),
        (
            [
                (100, ["fold"]),
                (80, ["call", "call"]),
                (15, [("raise", 5), "fold"]),
                (10, ["call", "fold"]),
                (15, ["call", ("raise", 15)]),
            ],  # player_conf_list
            [0, 15, 5, 2, 15],  # expected_chips_committeds
            [100, 65, 10, 8, 0],  # expected_stacks
            [False, True, False, False, True],  # expected_is_in_hands
        ),
        (
            [
                (100, [("raise", 100)]),
                (120, ["call"]),
                (90, ["call"]),
            ],  # player_conf_list
            [100, 100, 90],  # expected_chips_committeds
            [0, 20, 0],  # expected_stacks
            [True, True, True],  # expected_is_in_hands
        ),
        (
            [
                (100, ["call", ("raise", 100)]),
                (80, ["fold"]),
                (80, [("raise", 40), "fold"]),
                (101, ["fold"]),
                (110, [("raise", 20), "call", "call"]),
            ],  # player_conf_list
            [100, 1, 40, 0, 100],  # expected_chips_committeds
            [0, 79, 40, 101, 10],  # expected_stacks
            [True, False, False, False, True],  # expected_is_in_hands
        ),
        (
            [
                (100, ["fold", ("raise", 100)]),
                (80, ["call"]),
                (81, ["call"]),
                (101, ["call", "fold"]),
                (110, [("raise", 6)]),
            ],  # player_conf_list
            [0, 6, 6, 2, 6],  # expected_chips_committeds
            [100, 74, 75, 99, 104],  # expected_stacks
            [False, True, True, False, True],  # expected_is_in_hands
        ),
    ],
)
def test_play_preflop(
    player_conf_list,
    expected_chips_committeds,
    expected_stacks,
    expected_is_in_hands,
):
    player_list = []
    for stack, actions in player_conf_list:
        player = PlayerMock(stack, actions)
        player_list.append(player)

    table = AbstractTable(player_list=player_list)
    table.button = 0
    table.init_new_hand()
    table.play_preflop()
    chips_committed = [player.chips_committed for player in table.players]
    stacks = [player.stack for player in table.players]
    is_in_hands = [player.is_in_hand for player in table.players]

    assert chips_committed == expected_chips_committeds
    assert stacks == expected_stacks
    assert is_in_hands == expected_is_in_hands


@pytest.mark.parametrize(
    "player_conf_list, \
    expected_chips_committeds, expected_stacks, \
    expected_is_in_hands",
    [
        (
            [(100, True, ["check"]), (80, True, ["check"])],  # player_conf_list
            [0, 0],  # expected_chips_committeds
            [100, 80],  # expected_stacks
            [True, True],  # expected_is_in_hands
        ),
        (
            [
                (80, True, ["check", "call"]),
                (70, True, [("raise", 10)]),
                (100, True, ["fold"]),
            ],  # player_conf_list
            [10, 10, 0],  # expected_chips_committeds
            [70, 60, 100],  # expected_stacks
            [True, True, False],  # expected_is_in_hands
        ),
        (
            [
                (100, True, [("raise", 5), ("raise", 20)]),
                (80, True, ["fold"]),
                (15, True, ["call", "call"]),
                (10, True, [("raise", 10)]),
                (10, True, ["call"]),
            ],  # player_conf_list
            [20, 0, 15, 10, 10],  # expected_chips_committeds
            [80, 80, 0, 0, 0],  # expected_stacks
            [True, False, True, True, True],  # expected_is_in_hands
        ),
        (
            [
                (100, True, [("raise", 1)]),
                (80, False, ["call"]),
                (101, True, ["call"]),
            ],  # player_conf_list
            [1, 0, 1],  # expected_chips_committeds
            [99, 80, 100],  # expected_stacks
            [True, False, True],  # expected_is_in_hands
        ),
        (
            [
                (100, True, [("raise", 1)]),
                (80, False, ["check"]),
                (0, True, ["check"]),
                (101, True, ["call"]),
            ],  # player_conf_list
            [1, 0, 0, 1],  # expected_chips_committeds
            [99, 80, 0, 100],  # expected_stacks
            [True, False, True, True],  # expected_is_in_hands
        ),
    ],
)
def test_play_street(
    player_conf_list,
    expected_chips_committeds,
    expected_stacks,
    expected_is_in_hands,
):
    player_list = []
    for stack, is_in_hand, plays in player_conf_list:
        player = PlayerMock(stack, plays)
        player.is_in_hand = is_in_hand
        player_list.append(player)

    table = AbstractTable(player_list=player_list)
    table.button = table.n_players - 1
    table.history = {i: [] for i in range(4)}
    table.play_street(
        1, table.get_players_to_play((table.button + 1) % table.n_players)
    )
    chips_committed = [player.chips_committed for player in table.players]
    stacks = [player.stack for player in table.players]
    is_in_hands = [player.is_in_hand for player in table.players]

    assert chips_committed == expected_chips_committeds
    assert stacks == expected_stacks
    assert is_in_hands == expected_is_in_hands


@pytest.mark.parametrize(
    "player_conf_list, expected_stacks",
    [
        (
            [(100, ["fold"]), (2, []), (100, ["fold"])],  # player_conf_list
            [99, 3, 100],  # expected_stacks
        )
    ],
)
def test_play_hand(player_conf_list, expected_stacks):
    player_list = []
    for stack, actions in player_conf_list:
        player = PlayerMock(stack, actions)
        player_list.append(player)

    table = AbstractTable(player_list)
    table.button = table.n_players - 2

    table.play_hand()
    assert [player.stack for player in player_list] == expected_stacks
