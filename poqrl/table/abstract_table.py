from typing import Optional, List, Dict
from collections import deque


from poqrl.player.abstract_player import AbstractPlayer
from poqrl.hand.deck import Deck
from poqrl.hand.hand import Hand
from poqrl.hand.card import Card
from poqrl.types.street import Street
from poqrl.types.action import *


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
        self.history = None

    def sit_player(self, player: AbstractPlayer, position: int):
        """Anchor one player to the table"""
        self.players[position] = player
        player.sit_on_table(self, position)

    def set_players(self, player_list: List[AbstractPlayer]):
        """Anchor players to the table"""
        for position, player in enumerate(player_list):
            self.sit_player(player, position)

    def close_hand(self):
        """Called at the end of the RIVER"""
        self.assign_pots()
        for player in self.players:
            player.close_hand()

    def distribute_hands(self):
        """Distribute two cards to the players"""
        for player in self.players:
            card1 = self.deck.distribute_random_card()
            card2 = self.deck.distribute_random_card()
            player.set_hand(card1, card2)

    def distribute_board_card(self, card: Card):
        """ "Distribute a card to the board"""
        self.board.add_card(card)
        for player in self.players:
            player.hand.add_card(card)

    def distribute_flop(self):
        """Distribute three cards to the board.
        This method is called when flop needs to be distributed"""
        self.distribute_board_card(self.deck.distribute_random_card())
        self.distribute_board_card(self.deck.distribute_random_card())
        self.distribute_board_card(self.deck.distribute_random_card())

    def distribute_turn(self):
        """Distribute one card to the board.
        This method is called when turn needs to be distributed"""
        self.distribute_board_card(self.deck.distribute_random_card())

    def distribute_river(self):
        """Distribute one cards to the board.
        This method is called when river needs to be distributed"""
        self.distribute_board_card(self.deck.distribute_random_card())

    def get_player_action(self, player: AbstractPlayer, street: Street) -> Action:
        play = player.play_street(street)
        self.history[street].append((player.position, play, self.current_bet))
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
        # clear the precedent hand histroy
        self.history = {i: [] for i in range(4)}

    def get_blends(self):
        self.players[(self.button + 1) % self.n_players].raise_pot(1)
        self.players[(self.button + 2) % self.n_players].raise_pot(2)

    def get_players_to_play(self, starting_position: int = 0, exclude_starter: int = 0):
        player_queue = []
        for i in range(exclude_starter, self.n_players):
            player = self.players[(starting_position + i) % self.n_players]
            if player.is_in_hand and player.stack:
                player_queue.append(player)
        return player_queue

    def get_player_in_hand(self):
        return [player for player in self.players if player.is_in_hand]

    def play_rounds(self, player_queue: List[AbstractPlayer], street: Street):
        while player_queue:
            player = player_queue.pop(0)
            action = self.get_player_action(player, street)
            if action == RAISE:
                player_queue = self.get_players_to_play(player.position, 1)

    def play_preflop(self):
        self.get_blends()
        player_queue = self.get_players_to_play((self.button + 3) % self.n_players)
        self.play_rounds(player_queue, Street.PREFLOP)

    def play_street(self, player_to_play, street: Street):
        self.current_bet = 0
        self.previous_bet = 0
        self.play_rounds(player_to_play, street)

    def play_hand(self):
        self.update_button()
        self.init_new_hand()
        self.distribute_hands()
        self.play_preflop()
        n_in_hand, player_to_play = self.gather_chips_and_continue()
        if n_in_hand <= 1:
            return self.close_hand()
        else:
            self.distribute_flop()
            if len(player_to_play) > 1:
                self.play_street(player_to_play, Street.FLOP)
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
                self.play_street(player_to_play, Street.TURN)
                n_in_hand, player_to_play = self.gather_chips_and_continue()
            else:
                self.distribute_river()
                return self.close_hand()

        if n_in_hand <= 1:
            return self.close_hand()
        else:
            self.distribute_river()
            if len(player_to_play) > 1:
                self.play_street(player_to_play, Street.RIVER)
                n_in_hand, player_to_play = self.gather_chips_and_continue()

        return self.close_hand()

    def __str__(self):
        table_string = "---------------------------------------\n"
        for position, player in enumerate(self.players):
            table_string += str(player)
            if self.button == position:
                table_string += " B"
            table_string += "\n"
        table_string += f"{self.board}\n"
        table_string += f"pot: {self.pot}\n"
        for pot in self.side_pots:
            table_string += f"side pot {pot[0]}: {pot[1]}\n"
        table_string += f"bets: {self.previous_bet}\{self.current_bet}\n"
        table_string += "---------------------------------------\n"
        return table_string
