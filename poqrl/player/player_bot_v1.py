from collections import defaultdict
from pathlib import Path

import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense
import numpy as np

# from poqrl.player.abstract_player import AbstractPlayer
from poqrl.player.player_tracked import PlayerTracked
from poqrl.player.player_log import PlayerLog
from poqrl.types.street import Street
from poqrl.types.action import Action, FOLD, CHECK, CALL, RAISE


class PlayerBotV1(PlayerTracked):
    # class PlayerBotV1(PlayerLog):
    """First version of Bot"""

    def __init__(self, stack: int = 400, name: str = "Bot_v1", summary_writer=None):
        super().__init__(stack, name)
        self.qnets = {street: self.get_qvalues_network() for street in Street}
        self.optimizers = {
            street: tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.98)
            for street in Street
        }

        self.training = False
        self.writer = summary_writer
        self.action_qvalues = None
        self.step = 0
        self.is_bot = True

        self.training_streets = Street  # [Street.PREFLOP]
        self.training_street = Street.PREFLOP  # np.random.choice(Street)

        self.target_freq = {"on_bet": [0.6, 0.2, 0.2], "no_bet": [0.7, 0.3]}
        self.action_freq = {
            street: {"on_bet": [0.33, 0.33, 0.34], "no_bet": [0.5, 0.5]}
            for street in Street
        }
        self.total_action = 0

        self.gradient_variables = {}
        for street in Street:
            self.gradient_variables[street] = []
        self.cumulative_gradient = {}
        for street in Street:
            self.cumulative_gradient[street] = []
        self.gradient_step = 0

    def update_action_freq(self, street, action_value, on_bet):
        freq = self.action_freq[street]["on_bet" if on_bet else "no_bet"]
        for action_index, action_freq in enumerate(freq):
            a = 1 if action_value == action_index else 0
            freq[action_index] = 0.99 * action_freq + 0.01 * a

    def close_hand(self):
        super().close_hand()
        if self.training:
            reg_l = 0 * 0.01  # maximum is 0.01 when lr is 0.01
            action_l = 0.001
            n_step = 100
            for street, gradient_variables in self.gradient_variables.items():
                for gradient_data in gradient_variables:
                    estimated_qvalues = gradient_data[2]
                    chosen_action = gradient_data[3].value
                    stack = gradient_data[4]
                    on_bet = gradient_data[5]
                    best_action = tf.argmax(estimated_qvalues).numpy()
                    if estimated_qvalues[best_action] < 0 and on_bet:
                        best_action = 2
                    realized_q_value = tf.cast(self.stack - stack, dtype=tf.float32)

                    self.update_action_freq(street, best_action, on_bet)

                    target_freq = self.target_freq["on_bet" if on_bet else "no_bet"]
                    actual_freq = self.action_freq[street][
                        "on_bet" if on_bet else "no_bet"
                    ]

                    qdiff = tf.sign(
                        tf.squeeze(estimated_qvalues[chosen_action])
                    ) - tf.sign(realized_q_value) * tf.sqrt(tf.abs(realized_q_value))
                    action_coef = action_l * qdiff
                    reg0_coef = reg_l * tf.tanh(actual_freq[0] - target_freq[0])
                    reg1_coef = reg_l * tf.tanh(actual_freq[1] - target_freq[1])

                    variables_gradient = [
                        action_coef * action_grad
                        + reg0_coef * grad_reg0
                        + reg1_coef * grad_reg1
                        for action_grad, grad_reg0, grad_reg1 in zip(
                            gradient_data[chosen_action],
                            gradient_data[0],
                            gradient_data[1],
                        )
                    ]
                    cumm_grad = (
                        [
                            cum_grad + (1 / n_step) * new_grad
                            for cum_grad, new_grad in zip(
                                self.cumulative_gradient[street],
                                variables_gradient,
                            )
                        ]
                        if len(self.cumulative_gradient[street])
                        else variables_gradient
                    )
                    self.cumulative_gradient[street] = cumm_grad

                    if self.step % n_step != 0:
                        self.optimizers[street].apply_gradients(
                            zip(
                                self.cumulative_gradient[street],
                                self.qnets[street].trainable_variables,
                            )
                        )
                        self.cumulative_gradient[street] = []

                    if self.is_bot:
                        with self.writer.as_default():
                            tf.summary.scalar(
                                f"absQ-diff ({self.name})",
                                np.abs(qdiff),
                                self.step,
                            )
                            tf.summary.scalar(
                                f"signQ-diff ({self.name})",
                                tf.sign(qdiff),
                                self.step,
                            )
                    self.step += 1
            self.gradient_step += 1

    def get_action(self, street: Street, on_bet: bool) -> Action:
        current_stack = self.stack
        qnet = self.qnets[street]
        input_tensor = self.get_input(street)

        training = self.training
        if training:
            if street == self.training_street:
                with tf.GradientTape(persistent=True) as tape:
                    qvalues = self.qvalues_from_net_output(
                        qnet(input_tensor, training=training)
                    )[0]
                    action = self.get_decision_from_qvalues(qvalues, on_bet, training)
                    self.gradient_variables[street].append(
                        (
                            tape.gradient(qvalues[0], qnet.trainable_variables),
                            tape.gradient(qvalues[1], qnet.trainable_variables),
                            qvalues,
                            action,
                            current_stack,
                            on_bet,
                        )
                    )
                del tape
                decision = self.get_decision_from_qvalues(qvalues, on_bet, training)
            else:
                if on_bet:
                    return CALL
                else:
                    return CHECK
                # if np.random.choice(
                #     [True, False],
                #     p=[y := np.exp(-self.step / 4000), 1 - y],
                # ):
                #     qvalues = np.ones(2)
                #     qvalues[RAISE.value] = 0
                #     decision = self.get_decision_from_qvalues(qvalues, on_bet, False)
                # else:
                #     qvalues = self.qvalues_from_net_output(
                #         qnet(input_tensor, training=training)
                #     )[0]
                #     decision = self.get_decision_from_qvalues(qvalues, on_bet, training)
        else:
            if street == self.training_street:
                qvalues = self.qvalues_from_net_output(
                    qnet(input_tensor, training=training)
                )[0]
                decision = self.get_decision_from_qvalues(qvalues, on_bet, training)
            else:
                if on_bet:
                    return CALL
                else:
                    return CHECK
            # self.actual_action_proba[street][decision.value] += 1
            # self.total_action += 1

        return decision

    def reset_player(self):
        super().reset_player()
        self.action_freq = {
            street: {"on_bet": [0.33, 0.33, 0.34], "no_bet": [0.5, 0.5]}
            for street in Street
        }
        self.step = 1
        self.gradient_step = 0

    def reset_hand(self):
        super().reset_hand()
        self.gradient_variables = {street: [] for street in Street}
        self.training_street = np.random.choice(self.training_streets)

    def get_qvalues_network(self):
        net = Sequential()
        # net.add(Dense(10, activation="relu", input_dim=2))
        net.add(Dense(4, input_dim=1, activation="relu"))
        net.add(Dense(2, input_dim=4))
        return net

    def get_input(self, street: Street):
        board = self.table.board
        # n_raise = 0
        # for position, action, _ in self.table.history[street]:
        #     if action == RAISE and position != self.position:
        #         n_raise += 1
        # a = n_raise / (len(self.table.history[street]) + 1)

        avg_hand = self.hand.avg_value
        avg_any = 1924980.5
        avg_board = (
            np.mean(self.table.board.quantile_values) if len(board.cards) else avg_any
        )
        intput_value = np.tanh((avg_hand - avg_board) / avg_board)

        return tf.expand_dims(tf.constant([intput_value]), axis=0)

    def qvalues_from_net_output(self, output):
        return tf.math.tanh(output)

    def get_amount_to_raise(self, street, from_bet):
        if from_bet:
            return max(
                2 * self.table.current_bet - self.table.previous_bet,
                self.table.pot,
                2,
            )
        else:
            return max(
                2 * self.table.current_bet - self.table.previous_bet,
                self.table.pot,
                2,
            )

    def get_decision_from_qvalues(self, qvalues, on_bet, training):
        if training:
            choices = [RAISE, CALL] if on_bet else [RAISE, CHECK]
            decision = np.random.choice(choices)
        else:
            best_action_value = tf.argmax(qvalues).numpy()
            max_qval = qvalues[best_action_value]
            if on_bet:
                if max_qval < 0:
                    decision = FOLD
                elif best_action_value == CALL.value:
                    decision = CALL
                else:
                    decision = RAISE
            else:
                if best_action_value == CHECK.value:
                    decision = CHECK
                else:
                    decision = RAISE
        return decision

    def save_data(self, folder_path: Path) -> Path:
        saving_folder = folder_path / self.name
        saving_folder.mkdir(parents=True, exist_ok=True)
        for street, street_net in self.qnets.items():
            # print(street_net.trainable_variables)
            street_net.save(saving_folder / f"model_{street.name}")
        print(f"Model networks saved in {saving_folder}")
        return saving_folder

    def load_data_from_path(self, path: Path):
        self.qnets = {
            street: keras.models.load_model(str(path / f"model_{street.name}"))
            for street in Street
        }
