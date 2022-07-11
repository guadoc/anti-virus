from collections import defaultdict
from pathlib import Path

import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense
import numpy as np

from poqrl.player.abstract_player import AbstractPlayer


class PlayerBotV1(AbstractPlayer):
    def __init__(
        self, stack: int = 100, name: str = "Bot_v1", net=None, summary_writer=None
    ):
        super().__init__(stack, name)
        if net:
            self.qvalues_network = net
        else:
            self.qvalues_network = self.get_qvalues_network()

        # self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
        self.optimizer = tf.keras.optimizers.SGD(learning_rate=0.001)
        self.gradient_variables = []
        self.training = False

        self.writer = summary_writer
        self.training_street = -1

        self.action_frequency = None
        self.action_qvalues = None
        self.histograms = None
        self.reset_tracking()
        self.step = 0

        self.is_bot = True

    def reset_tracking(self):
        self.action_frequency = {i: defaultdict(int) for i in range(4)}
        self.action_qvalues = {i: defaultdict(list) for i in range(4)}
        self.histograms = {i: defaultdict(list) for i in range(4)}

    def get_input(self, street_number: int):
        n_raise = 0
        for position, action, _ in self.table.history[street_number]:
            if action == "raise" and position != self.position:
                n_raise += 1
        avg_hand = self.hand.avg_value
        avg_any = 1924980.5
        if street_number:
            avg_board = self.table.board.avg_value
        else:
            avg_board = avg_any
        intput_tensor = (
            n_raise / (len(self.table.history[street_number]) + 1),
            (avg_hand - avg_board) / avg_any,
        )
        return tf.expand_dims(tf.constant(intput_tensor), axis=0)

    def get_qvalues_network(self):
        net = Sequential()
        net.add(Dense(20, activation="relu", input_dim=2))
        net.add(Dense(20, activation="relu", input_dim=20))
        net.add(Dense(2, input_dim=20))
        print(net.summary())
        return net

    def get_qvalue_from_net_output(self, output):
        return tf.math.tanh(output)

    def save_data(self, folder_path: Path) -> Path:
        saving_folder = folder_path / self.name
        saving_folder.mkdir(parents=True, exist_ok=True)
        self.qvalues_network.save(saving_folder / "model")
        return saving_folder

    def load_data_from_path(self, path: Path):
        self.qvalues_network = keras.models.load_model(str(path / "model"))

    def reset_player(self):
        super().reset_player()
        self.step = 1
        self.reset_tracking()

    def reset_hand(self):
        super().reset_hand()
        self.gradient_variables = []

    def get_decision_from_input(self, input, training=False):
        qvalues = self.get_qvalue_from_net_output(
            self.qvalues_network(input, training=training)
        )[0]
        if training:
            decision = np.random.choice([0, 1])
        else:
            decision = tf.argmax(qvalues).numpy()
        return decision, qvalues[decision]

    def play_street(self, street_number):
        from_bet = self.table.current_bet > self.chips_committed
        current_stack = self.stack

        if street_number < self.training_street:
            if from_bet:
                action = self.call()
            else:
                action = self.check()
        else:
            input = self.get_input(street_number)
            if self.training:
                with tf.GradientTape() as tape:
                    decision, qvalue = self.get_decision_from_input(
                        input, training=True
                    )

                grad = tape.gradient(qvalue, self.qvalues_network.trainable_variables)
                self.gradient_variables.append((grad, qvalue, current_stack))
            else:
                decision, qvalue = self.get_decision_from_input(input, training=False)

            if qvalue < 0 and from_bet and not self.training:
                action = self.fold()
            else:
                action = self.get_decision(decision, from_bet)
        self.action_frequency[street_number][action] += 1
        if street_number == 3:
            self.histograms[street_number][action].append(self.hand.value)
            self.action_qvalues[street_number][action].append(qvalue)
        return action

    def get_decision(self, decision, from_bet):
        if decision == 0:
            if from_bet:
                raise_amount = max(
                    2 * self.table.current_bet - self.table.previous_bet,
                    self.table.pot,
                    2,
                )
            else:
                raise_amount = max(
                    2 * self.table.current_bet - self.table.previous_bet,
                    self.table.pot,
                    2,
                )
            return self.raise_pot(raise_amount)
        elif decision == 1:
            if from_bet:
                return self.call()
            return self.check()
        else:
            return self.fold()

    def close_hand(self):
        super().close_hand()
        if self.training:

            for gradient, estimated_qvalue, stack in self.gradient_variables:
                realized_q_value = tf.cast(self.stack - stack, dtype=tf.float32)
                qdiff = tf.squeeze(estimated_qvalue) - realized_q_value
                # qdiff = tf.sign(tf.squeeze(estimated_qvalue) * realized_q_value)
                g = [qdiff * grad for grad in gradient]

                self.optimizer.apply_gradients(
                    zip(g, self.qvalues_network.trainable_variables)
                )

                if self.is_bot:
                    with self.writer.as_default():
                        tf.summary.scalar(
                            f"Q-diff ({self.name})",
                            np.abs(qdiff),
                            self.step,
                        )
                        tf.summary.scalar(
                            f"RegQ-diff ({self.name})",
                            np.abs(qdiff)
                            / (tf.abs(realized_q_value) + tf.abs(estimated_qvalue)),
                            self.step,
                        )
                        tf.summary.scalar(
                            f"SignQ-diff ({self.name})",
                            tf.sign(qdiff),
                            self.step,
                        )
                        self.step += 1

    def print_stats(self):
        print(self.name)
        for street, street_freq in self.action_frequency.items():
            print(f"-- street {street}:")
            for action, freq in street_freq.items():
                print(f"     {action}: {freq}")
