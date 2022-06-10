from typing import Optional, List, Dict
from collections import deque


from poqrl.player.abstract_player import AbstractPlayer
from poqrl.hand.deck import Deck
from poqrl.hand.hand import Hand


class AbstractTable:
    def __init__(
        self,
        player_list: List[AbstractPlayer],
    ):
        self.players = deque(player_list)
        self.n_players = len(self.players)
        self.button = self.n_players - 1
        self.set_players(player_list)
        self.deck = Deck()
        self.board = Hand()
        self.previous_bet = 0
        self.current_bet = 0
        self.player_all_in = False
        self.pot = 0
        self.side_pots = []
        self.total_pot = 0

    def sit_player(self, player: AbstractPlayer, position: int):
        self.players[position] = player
        player.sit_on_table(self, position)

    def set_players(self, player_list: List[AbstractPlayer]):
        for position, player in enumerate(player_list):
            self.sit_player(player, position)

    def close_hand(self):
        self.assign_pots()
        for player in self.players:
            player.close_hand()

    def distribute_hands(self):
        """Distribute two cards to the players"""
        for player in self.players:
            card1 = self.deck.distribute_random_card()
            card2 = self.deck.distribute_random_card()
            player.set_hand(card1, card2)

    def distribute_board_card(self):
        random_card = self.deck.distribute_random_card()
        self.board.add_card(random_card)
        for player in self.players:
            player.hand.add_card(random_card)

    def distribute_flop(self):
        self.distribute_board_card()
        self.distribute_board_card()
        self.distribute_board_card()

    def distribute_turn(self):
        self.distribute_board_card()

    def distribute_river(self):
        self.distribute_board_card()

    def get_player_action(self, player: AbstractPlayer, street_number: int):
        play = player.play_street(street_number)
        return play

    def assign_pots(self):
        self.assign_pot(self.pot, self.get_player_in_hand())
        for pot_and_player in self.side_pots:
            self.assign_pot(
                pot_and_player[0],
                [self.players[position] for position in pot_and_player[1]],
            )

    def assign_pot(self, pot: int, players: List[AbstractPlayer]):
        if len(players) == 1:
            players[0].stack += pot
            return
        max_players = [players[0]]
        max_value = players[0].hand.value
        for player in players[1:]:
            player_hand_value = player.hand.value
            if player_hand_value >= max_value:
                if player_hand_value == max_value:
                    max_players.append(player)
                else:
                    max_value = player_hand_value
                    max_players = [player]
        pot_per_player = int(pot / len(max_players))
        res = pot - len(max_players) * pot_per_player
        for player in max_players:
            self.yield_pot_to_player(pot_per_player, player)
        self.yield_pot_to_player(res, max_players[-1])

    def yield_pot_to_player(self, pot: int, player: AbstractPlayer()):
        player.stack += pot

        # @staticmethod
        # def fill_side_pots(side_pots, committed_amounts, player):
        #     player_commitment = player.chips_committed
        #     player_position = player.position
        #     is_in_hand = player.is_in_hand
        #     index_side_pot = 0
        #     while (
        #         index_side_pot < len(committed_amounts)
        #         and player_commitment >= committed_amounts[index_side_pot]
        #     ):
        #         commitment = committed_amounts[index_side_pot]
        #         player_commitment -= commitment
        #         side_pots[index_side_pot][0] += commitment
        #         if is_in_hand:
        #             side_pots[index_side_pot][1].append(player_position)
        #         index_side_pot += 1
        #     if player_commitment:
        #         if index_side_pot == len(committed_amounts):
        #             if is_in_hand:
        #                 side_pots.append([player_commitment, [player_position]])
        #             else:
        #                 side_pots.append([player_commitment, []])
        #             committed_amounts.append(player_commitment)
        #         else:
        #             committed_amounts.insert(index_side_pot, player_commitment)
        #             player_in_pot = list(side_pots[index_side_pot][1])
        #             if is_in_hand:
        #                 player_in_pot.append(player_position)
        #             side_pots.insert(
        #                 index_side_pot,
        #                 [player_commitment * len(player_in_pot), player_in_pot],
        #             )
        #             index_side_pot += 1
        #             committed_amounts[index_side_pot] -= player_commitment
        #             side_pots[index_side_pot][0] -= player_commitment * len(
        #                 side_pots[index_side_pot][1]
        #             )

        # return side_pots, committed_amounts

    def gather_chips_and_continue(self) -> bool:
        if self.current_bet:
            n_in_hand = 0
            if self.player_all_in:
                side_amount = set([0])
                for player in self.players:
                    side_amount.add(player.chips_committed)
                    if player.is_in_hand:
                        n_in_hand += 1
                side_amount = list(side_amount)
                side_amount.sort()
                vals = [
                    side_amount[i] - side_amount[i - 1]
                    for i in range(1, len(side_amount))
                ]
                side_pots = [[0, []] for _ in range(len(vals))]

                for player in self.players:
                    i = 0
                    while player.chips_committed:
                        side_pots[i][0] += vals[i]
                        player.chips_committed -= vals[i]
                        if player.is_in_hand:
                            side_pots[i][1].append(player.position)
                        i += 1

                side_pots[0][0] += self.pot
                self.pot, _ = side_pots.pop()
                self.side_pots += side_pots
                self.total_pot = self.pot
                for side_pot in self.side_pots:
                    self.total_pot += side_pot[0]

            else:
                for player in self.players:
                    self.pot += player.chips_committed
                    player.chips_committed = 0
                    if player.is_in_hand:
                        n_in_hand += 1
            return n_in_hand, self.get_players_to_play(self.button + 1)
        return 2, self.get_players_to_play(self.button + 1)

    def update_button(self):
        self.button = (self.button + 1) % self.n_players

    def init_new_hand(self):
        # gather distributed card and shuffle the deck
        for player in self.players:
            player.reset_hand()
        self.board = Hand()
        self.deck.shuffle()
        # update bet status
        self.current_bet = 0
        self.previous_bet = 0
        # empty the pots
        self.player_all_in = False
        self.side_pots = []
        self.pot = 0
        # distribute the hand to players
        self.distribute_hands()

    def get_blends(self):
        self.players[(self.button + 1) % self.n_players].raise_pot(1)
        self.players[(self.button + 2) % self.n_players].raise_pot(2)

    def get_players_to_play(self, starting_position: int = 0, exclude_starter: int = 0):
        player_stack = []
        for i in range(exclude_starter, self.n_players):
            player = self.players[(starting_position + i) % self.n_players]
            if player.is_in_hand and player.stack:
                player_stack.append(player)
        return player_stack

    def get_player_in_hand(self):
        return [player for player in self.players if player.is_in_hand]

    def play_rounds(self, player_stack, street_number):
        while player_stack:
            player = player_stack.pop(0)
            action = self.get_player_action(player, street_number)
            if action == "raise":
                player_stack = self.get_players_to_play(player.position, 1)

    def play_preflop(self):
        self.get_blends()
        player_stack = self.get_players_to_play((self.button + 3) % self.n_players)
        self.play_rounds(player_stack, street_number=0)

    def play_street(self, street_number: int, player_to_play):
        # print(f"--street {street_number}")
        self.current_bet = 0
        self.previous_bet = 0
        self.play_rounds(player_to_play, street_number)

    def play_hand(self):
        self.update_button()
        self.init_new_hand()
        self.play_preflop()
        n_in_hand, player_to_play = self.gather_chips_and_continue()
        if n_in_hand <= 1:
            return self.close_hand()
        else:
            self.distribute_flop()
            if len(player_to_play) > 1:
                self.play_street(1, player_to_play)
                n_in_hand, player_to_play = self.gather_chips_and_continue()
            else:
                self.distribute_turn()
                self.distribute_river()
                return self.close_hand()

        if n_in_hand <= 1:
            return self.close_hand()
        else:
            self.distribute_turn()
            if len(player_to_play) > 1:
                self.play_street(2, player_to_play)
                n_in_hand, player_to_play = self.gather_chips_and_continue()
            else:
                self.distribute_river()
                return self.close_hand()

        if n_in_hand <= 1:
            return self.close_hand()
        else:
            self.distribute_river()
            if len(player_to_play) > 1:
                self.play_street(3, player_to_play)
                n_in_hand, player_to_play = self.gather_chips_and_continue()

        return self.close_hand()

    def __str__(self):
        table_string = ""
        for player in self.players:
            table_string += str(player) + "\n"
        table_string += f"pot: {self.pot}\n"
        for pot in self.side_pots:
            table_string += f"{pot[0]}: {pot[1]}\n"
        return table_string
