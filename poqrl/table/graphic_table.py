from pathlib import Path
import time
from typing import List
from tkinter import Tk, Label, Text
from PIL import ImageTk, Image

from poqrl.table.abstract_table import AbstractTable
from poqrl.player.abstract_player import AbstractPlayer
from poqrl.hand.card import Card
from poqrl.types.street import Street

SIT_COORDINATES = [
    (20, 100),
    (400, 50),
    (800, 100),
    (800, 500),
    (400, 550),
    (20, 500),
]

CHIPS_COORDS = [
    (20 + 100, 100 + 100),
    (400, 50 + 100),
    (800 - 10, 100 + 100),
    (800 - 40, 500 - 40),
    (400, 550 - 70),
    (20 + 100, 500 - 40),
]

BUTTON_COORDS = [
    (170, 200),
    (420, 200),
    (770, 255),
    (750, 460),
    (380, 425),
    (125, 415),
]

POTS_COORDS = (460, 355)


class GraphicTable(AbstractTable):
    """Table with graphical interface"""

    def __init__(self, player_list: List[AbstractPlayer]):
        self.window = Tk()
        super().__init__(player_list=player_list)
        self.graphic_utils = Path("graphism")
        self.window.geometry("1000x990")
        self.player_labels = [{} for _ in range(self.n_players)]
        self.labels = {
            label: Label(self.window)
            for label in ["pot"]
            + [f"pot{i}" for i in range(self.n_players)]
            + [f"board_card{i}" for i in range(5)]
        }
        self.labels["table"] = self.place_label(0, 0)
        self.update_image(self.labels["table"], self.graphic_utils / "table2.png")
        for player in self.players:
            self.place_player_labels(player)
        self.labels["button"] = self.place_label(500, 350)
        self.update_image(
            self.labels["button"], self.graphic_utils / "button.jpeg", 25, 25
        )
        self.window.update()

    def update_button(self):
        super().update_button()
        x, y = BUTTON_COORDS[self.button]
        self.labels["button"].place(x=x, y=y)

    def init_new_hand(self):
        time.sleep(0.5)
        print("-----------NEW HAND----------")
        super().init_new_hand()
        self.reset_board()
        for player in self.players:
            self.update_player(player, -1)
        self.window.update()
        time.sleep(0.8)

    def gather_chips_and_continue(self):
        outs = super().gather_chips_and_continue()
        self.update_pots()
        for player in self.players:
            self.update_player(player, -1)
        self.window.update()
        return outs

    def update_pots(self):
        coord_x, coord_y = POTS_COORDS
        self.labels["pot"].destroy()
        self.labels["pot"] = self.place_label(coord_x, coord_y)
        self.labels["pot"].config(text=f"Pot: {self.pot}")
        for i, pot_n_players in enumerate(self.side_pots):
            self.labels[f"pot{i}"].destroy()
            self.labels[f"pot{i}"] = self.place_label(x=coord_x, y=coord_y + i * 45)
            self.labels[f"pot{i}"].config(text=str(pot_n_players[0]))

    def reset_pots(self):
        self.labels["pot"].destroy()
        for i, _ in enumerate(self.side_pots):
            self.labels[f"pot{i}"].destroy()

    def yield_pot_to_player(self, pot: int, player: AbstractPlayer):
        print(f"{player.name} wins {pot}")
        super().yield_pot_to_player(pot, player)

    def distribute_board_card(self, card: Card):
        super().distribute_board_card(card)
        self.update_board()
        self.window.update()
        time.sleep(0.5)

    def distribute_hands(self):
        super().distribute_hands()
        for player in self.players:
            self.update_player(player, -1)
        time.sleep(0.25)
        print("---- Distribute hand")
        print(self)

    def assign_pots(self):
        print("---- Assigning pot")
        print(self)
        time.sleep(1.5)
        super().assign_pots()
        time.sleep(0.5)
        self.reset_pots()
        print("---- Pot assigned")
        time.sleep(0.5)

    def reset_board(self):
        for i in range(5):
            self.labels[f"board_card{i}"].destroy()

    def update_board(self):
        for i, card in enumerate(self.board.cards):
            self.labels[f"board_card{i}"].destroy()
            self.labels[f"board_card{i}"] = self.place_label(x=300 + i * 60, y=270)
            self.update_image(
                self.labels[f"board_card{i}"],
                self.graphic_utils / "cards" / f"{card.hash}.bmp",
            )

    def get_blends(self):
        super().get_blends()
        self.update_player(self.players[(self.button + 1) % self.n_players], -1)
        time.sleep(0.5)
        self.update_player(self.players[(self.button + 2) % self.n_players], -1)
        time.sleep(0.5)

    def get_player_action(self, player: AbstractPlayer, street: Street):
        self.update_player(player, player.position)
        time.sleep(0.6)
        play = super().get_player_action(player, street)
        self.update_pots()
        self.update_player(player, -1)
        time.sleep(1)
        print("---- Get player action")
        print(self)
        return play

    def update_player(self, player, playing_player):
        position = player.position
        player_labels = self.player_labels[position]
        if position == playing_player:
            path_to_sit = self.graphic_utils / "sit_active.png"
        else:
            path_to_sit = self.graphic_utils / "sit.png"
        self.update_image(player_labels["sit"], path_to_sit, 100, 100)
        player_labels["stack"].config(text=str(player.stack))

        player_labels["card1"].destroy()
        player_labels["card2"].destroy()

        card1, card2 = player.cards
        if card1 and card2 and player.is_in_hand:
            sit_coord_x, sit_coord_y = SIT_COORDINATES[position]
            player_labels["card1"] = self.place_label(
                sit_coord_x,
                sit_coord_y - 45,
            )
            player_labels["card2"] = self.place_label(
                sit_coord_x + 40,
                sit_coord_y - 45,
            )
            self.update_image(
                player_labels["card1"],
                self.graphic_utils / "cards" / f"{card1.hash}.bmp",
            )
            self.update_image(
                player_labels["card2"],
                self.graphic_utils / "cards" / f"{card2.hash}.bmp",
            )
            self.window.update()

        player_labels["chips"].destroy()
        if player.chips_committed:
            player_labels["chips"] = self.place_label(
                x=CHIPS_COORDS[position][0], y=CHIPS_COORDS[position][1]
            )
            player_labels["chips"].config(text=str(player.chips_committed))
        self.window.update()

    def place_player_labels(self, player: AbstractPlayer):
        """Add the player and its information on the window"""
        position = player.position
        sit_coord_x, sit_coord_y = SIT_COORDINATES[position]
        player_labels = self.player_labels[position]
        player_labels["sit"] = self.place_label(sit_coord_x, sit_coord_y)
        player_labels["stack"] = self.place_label(
            x=sit_coord_x + 40, y=sit_coord_y + 50
        )
        player_labels["name"] = self.place_label(x=sit_coord_x + 40, y=sit_coord_y + 20)
        player_labels["name"].config(text=f"{player.name} ({player.position})")
        player_labels["card1"] = Label(self.window)
        player_labels["card2"] = Label(self.window)
        player_labels["chips"] = Label(self.window)

    def place_label(self, x, y):
        label = Label(self.window)
        label.pack()
        label.place(x=x, y=y)
        return label

    # @staticmethod
    def update_image(self, label, image_path, x_size=None, y_size=None):
        pil_image = Image.open(image_path)
        if x_size and y_size:
            pil_image = pil_image.resize((x_size, y_size))
        tk_image = ImageTk.PhotoImage(pil_image)
        label.config(image=tk_image)
        label.photo = tk_image
