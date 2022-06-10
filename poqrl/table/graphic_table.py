from pathlib import Path
import time
from typing import List
from tkinter import Tk, Label, Text
from PIL import ImageTk, Image

from poqrl.table.abstract_table import AbstractTable
from poqrl.player.abstract_player import AbstractPlayer

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
    (815, 460),
    (380, 425),
    (125, 415),
]


class GraphicTable(AbstractTable):
    """Table with graphical interface"""

    def __init__(self, player_list: List[AbstractPlayer]):
        self.window = Tk()
        super().__init__(player_list=player_list)
        self.graphic_utils = Path("graphism")
        self.window.geometry("1000x990")
        self.player_labels = [{} for _ in range(self.n_players)]
        self.labels = {}
        self.labels["table"] = self.place_label(0, 0)
        self.labels["button"] = self.place_label(500, 350)
        for i in range(5):
            self.labels[f"board_card{i}"] = self.place_label(x=300 + i * 60, y=270)
        self.labels["total_pot"] = self.place_label(460, 355)
        for i in range(self.n_players - 1):
            self.labels[f"pot{i}"] = self.place_label(x=460, y=400 + i * 45)
        for player in self.players:
            self.place_player_labels(player)
        self.update_image(self.labels["table"], self.graphic_utils / "table2.png")
        self.update_image(
            self.labels["button"], self.graphic_utils / "button.jpeg", 25, 25
        )
        self.window.update()

    def get_player_action(self, player: AbstractPlayer, street_number: int):
        self.update_player(player, player.position)
        self.window.update()
        time.sleep(1.5)
        play = super().get_player_action(player, street_number)
        self.update_player(player, -1)
        if not player.is_in_hand:
            self.reset_player_hand(player)
        self.update_pots()
        self.window.update()
        return play

    def update_button(self):
        x, y = BUTTON_COORDS[self.button]
        self.labels["button"].place(x=x, y=y)

    def init_new_hand(self):
        time.sleep(1.0)
        print("-----------NEW HAND----------")
        super().init_new_hand()
        self.reset_board()
        self.reset_pot()
        for player in self.players:
            self.update_player(player, -1)
        self.update_button()
        self.window.update()
        time.sleep(0.8)

    def gather_chips_and_continue(self, one_player):
        one_player = super().gather_chips_and_continue(one_player)
        self.update_pots()
        for player in self.players:
            self.update_player(player, -1)

        self.window.update()
        return one_player

    def update_pots(self):
        self.update_text(self.labels["total_pot"], f"total pot: {self.pot}")
        for i, pot_n_players in enumerate(self.side_pots):
            self.update_text(self.labels[f"pot{i}"], str(pot_n_players[0]))

    def reset_pot(self):
        self.reset_text(self.labels["total_pot"])
        for i in range(self.n_players - 1):
            self.reset_text(self.labels[f"pot{i}"])

    def yield_pot_to_player(self, pot: int, player: AbstractPlayer):
        print(f"{player.name} wins {pot}")
        super().yield_pot_to_player(pot, player)

    def distribute_board_card(self):
        super().distribute_board_card()
        self.update_board()
        time.sleep(0.25)

    def distribute_hands(self):
        super().distribute_hands()
        self.window.update()
        time.sleep(0.25)

    def assign_pots(self):
        super().assign_pots()
        time.sleep(0.5)

    def reset_board(self):
        for i in range(5):
            self.reset_image(self.labels[f"board_card{i}"])

    def update_board(self):
        for i, card in enumerate(self.board.cards):
            self.update_image(
                self.labels[f"board_card{i}"],
                self.graphic_utils / "cards" / f"{card}.bmp",
            )

    def reset_player_hand(self, player):
        player_labels = self.player_labels[player.position]
        self.reset_image(player_labels["card1"])
        self.reset_image(player_labels["card2"])

    def get_blends(self):
        super().get_blends()
        self.update_player(self.players[(self.button + 1) % self.n_players], -1)
        self.update_player(self.players[(self.button + 2) % self.n_players], -1)
        self.window.update()
        time.sleep(0.5)

    def update_player(self, player, playing_player):
        position = player.position
        player_labels = self.player_labels[position]
        if position == playing_player:
            path_to_sit = self.graphic_utils / "sit_active.png"
        else:
            path_to_sit = self.graphic_utils / "sit.png"
        self.update_image(player_labels["sit"], path_to_sit, 100, 100)
        self.update_text(player_labels["stack"], str(player.stack))
        self.update_text(player_labels["name"], player.name)
        card1, card2 = player.cards
        if card1 and card2 and player.is_in_hand:
            self.update_image(
                player_labels["card1"],
                self.graphic_utils / "cards" / f"{card1}.bmp",
            )
            self.update_image(
                player_labels["card2"],
                self.graphic_utils / "cards" / f"{card2}.bmp",
            )
        if player.chips_committed:
            self.update_text(player_labels["chips"], str(player.chips_committed))
        else:
            self.reset_text(player_labels["chips"])

    def place_player_labels(self, player: AbstractPlayer):
        """Add the player and its information on the window"""
        position = player.position
        sit_coord_x, sit_coord_y = SIT_COORDINATES[position]
        self.player_labels[position]["sit"] = self.place_label(sit_coord_x, sit_coord_y)
        self.player_labels[position]["stack"] = self.place_label(
            x=sit_coord_x + 40, y=sit_coord_y + 50
        )

        self.player_labels[position]["name"] = self.place_label(
            x=sit_coord_x + 40, y=sit_coord_y + 20
        )

        self.player_labels[position]["chips"] = self.place_label(
            x=CHIPS_COORDS[position][0], y=CHIPS_COORDS[position][1]
        )

        self.player_labels[position]["card1"] = self.place_label(
            sit_coord_x,
            sit_coord_y - 45,
        )
        self.player_labels[position]["card2"] = self.place_label(
            sit_coord_x + 40,
            sit_coord_y - 45,
        )

    def place_label(self, x, y, x_size=None, y_size=None):
        label = Label(self.window)
        label.pack()
        label.place(x=x, y=y)
        return label

    def update_image(self, label, image_path, x_size=None, y_size=None):
        pil_image = Image.open(image_path)
        if x_size and y_size:
            pil_image = pil_image.resize((x_size, y_size))
        tk_image = ImageTk.PhotoImage(pil_image)
        label.config(image=tk_image)
        label.photo = tk_image

    def update_text(self, label, text):
        label.config(text=text)

    def reset_image(self, label):
        label.config(image="")
        # label.pack_forget()

    def reset_text(self, label):
        label.config(text="")
        # label.pack_forget()
