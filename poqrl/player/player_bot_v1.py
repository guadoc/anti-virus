from typing import Optional, List

import tensorflow as tf

# import keras
from keras.models import Sequential
from keras.layers import Dense
import numpy as np

from poqrl.player.abstract_player import AbstractPlayer


class PlayerBotV1(AbstractPlayer):
    def __init__(
        self, stack: int = 100, name: str = "Bot v1", net=None, summary_writer=None
    ):
        super().__init__(stack, name)
        if net:
            self.qvalues_network = net
        else:
            self.qvalues_network = self.get_qvalues_network()

        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
        self.gradient_variables = []
        self.training = False

        self.writer = summary_writer
        self.training_street = -1

        self.step = 0

    def reset_hand(self):
        super().reset_hand()
        self.gradient_variables = []

    def get_qvalues_network(self):
        net = Sequential()
        net.add(Dense(10, activation="relu", input_dim=5))
        net.add(Dense(2, input_dim=10))
        return net

    def get_state_input(self, street_number: int):
        avg_hand = self.hand.value
        if street_number:
            avg_board = self.table.board.compute_mc_avg_value()
        else:
            avg_board = 1288103.28
        intput_tensor = (
            (avg_hand - 1288103.28) / 1288103.28,
            (avg_board - 1288103.28) / 1288103.28,
            self.table.pot / self.stack,
            street_number,
            self.table.current_bet / self.stack,
        )
        return tf.expand_dims(tf.constant(intput_tensor), axis=0)

    def get_qvalue_from_net_output(self, output):
        return 2 * self.table.pot * tf.sigmoid(output) - self.table.pot

    def play_street(self, street_number):

        from_bet = self.table.current_bet > self.chips_committed

        if street_number < self.training_street:
            if from_bet:
                return self.call()
            else:
                return self.check()
        elif street_number == self.training_street:
            if street_number == self.training_street:
                input = self.get_state_input(street_number)
                if self.training:
                    with tf.GradientTape() as tape:
                        qvalues = self.get_qvalue_from_net_output(
                            self.qvalues_network(input, training=True)
                        )
                        decision = np.random.choice([0, 1])
                        qvalue = qvalues[0][decision]
                    grad = tape.gradient(
                        qvalue, self.qvalues_network.trainable_variables
                    )
                    self.gradient_variables.append((grad, qvalue, self.stack))
                    return self.get_decision(decision, from_bet)
        input = self.get_state_input(street_number)
        qvalues = self.get_qvalue_from_net_output(
            self.qvalues_network(input, training=False)
        )
        decision = tf.argmax(qvalues)[0].numpy()
        if qvalues[decision][0].numpy() < 0 and from_bet:
            return self.fold()
        return self.get_decision(decision, from_bet)

    def get_decision(self, decision, from_bet):
        if from_bet:
            if decision == 0:
                return self.raise_pot(
                    max(
                        2 * self.table.current_bet - self.table.previous_bet,
                        self.table.pot,
                        2,
                    )
                )
            else:
                return self.call()
        else:
            if decision == 0:
                return self.raise_pot(
                    max(
                        2 * self.table.current_bet - self.table.previous_bet,
                        self.table.pot,
                        2,
                    )
                )
            else:
                return self.check()

    def close_hand(self):
        super().close_hand()
        if self.training:
            for gradient, estimated_qvalue, stack in self.gradient_variables:
                realized_q_value = self.stack - stack
                g = [
                    (
                        (tf.squeeze(estimated_qvalue) - realized_q_value)
                        / realized_q_value
                    )
                    * grad
                    for grad in gradient
                ]

                variables = self.qvalues_network.trainable_variables

                self.optimizer.apply_gradients(zip(g, variables))
                with self.writer.as_default():
                    tf.summary.scalar(
                        "loss",
                        np.abs(estimated_qvalue - realized_q_value),
                        self.step,
                    )
                    self.step += 1
                # print(np.square(estimated_qvalue - realized_q_value))
