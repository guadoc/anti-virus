from tkinter import Button, StringVar, Entry
from poqrl.player.abstract_player import AbstractPlayer
from poqrl.player.player_log import PlayerLog

from poqrl.types.street import Street
from poqrl.types.action import *

# class PlayerIHM(AbstractPlayer):
class PlayerIHM(PlayerLog):
    """Player that can play through the IHM"""

    def __init__(self, name="ihm_player"):
        super().__init__(name=name)
        self.waiting_condition = None

    def sit_on_table(self, table, position):
        super().sit_on_table(table, position)
        self.waiting_condition = StringVar()

    def check(self):
        self.waiting_condition.set("check")
        return super().check()

    def call(self):
        self.waiting_condition.set("call")
        return super().call()

    def fold(self):
        self.waiting_condition.set("fold")
        return super().fold()

    def raise_pot(self, bet_amount: int):
        self.waiting_condition.set("raise")
        return super().raise_pot(bet_amount)

    def play_street(self, street: Street):
        current_bet = self.table.current_bet
        # if street_number < 3:
        #     if current_bet > self.chips_committed:
        #         return self.call()
        #     else:
        #         return self.check()
        button_raise = Button(
            self.table.window,
            text="RAISE",
            command=lambda: self.raise_pot(int(bet_amount.get())),
        )
        button_check = Button(self.table.window, text="CHECK", command=self.check)
        button_call = Button(self.table.window, text="CALL", command=self.call)
        button_fold = Button(self.table.window, text="FOLD", command=self.fold)

        labels = []
        if current_bet <= self.chips_committed:
            button_check.pack()
            button_check.place(x=50, y=700)
            button_raise.pack()
            button_raise.place(x=300, y=700)
            labels = [button_check, button_raise]
        else:
            button_fold.pack()
            button_fold.place(x=50, y=700)
            button_call.pack()
            button_call.place(x=175, y=700)
            button_raise.pack()
            button_raise.place(x=300, y=700)
            labels = [button_call, button_fold, button_raise]

        bet_amount = StringVar()
        bet_amount.set("0")
        bet_amount_entree = Entry(self.table.window, textvariable=bet_amount, width=20)
        bet_amount_entree.pack()
        bet_amount_entree.place(x=50, y=750)

        self.table.window.update()
        self.table.window.wait_variable(self.waiting_condition)
        for label in labels:
            label.destroy()
        bet_amount_entree.destroy()
        self.table.window.update()
        return self.play_from_str(self.waiting_condition.get())

    def play_from_str(self, value):
        if value == "raise":
            return RAISE
        elif value == "check":
            return CHECK
        elif value == "call":
            return CALL
        elif value == "fold":
            return FOLD
