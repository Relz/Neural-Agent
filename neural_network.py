import os
import pickle
import numpy as np
import calendar
import time
import glob


class NeuralNetwork:
    WEIGHTS_1 = 'Weights 1'
    WEIGHTS_2 = 'Weights 2'
    file_name = ''
    input_layer_size = 0
    hidden_layer_size = 0
    output_layer_size = 0
    learning_rate = 0
    gamma = 0
    delta = 0
    batch_size = 0
    decay_rate = 0

    model = {}
    r_m_s_prop_cache = {}

    a_xs = []
    a_hs = []
    a_errs = []
    a_rs = []
    a_zerrs = []
    grad_buffer = {}

    games_count = 0

    def policy_forward(self, input_layer):
        hidden_layer = np.dot(self.model[NeuralNetwork.WEIGHTS_1], np.array(input_layer))
        hidden_layer[hidden_layer < 0] = 0
        z = np.dot(self.model[NeuralNetwork.WEIGHTS_2], hidden_layer)
        normalized_output_layer = NeuralNetwork.__sigmoid__(z)
        return normalized_output_layer.tolist(), hidden_layer.tolist()

    @staticmethod
    def __sigmoid__(x):
        return 1.0 / (1.0 + np.exp(-x))

    def update(self, input_layers, hidden_layers, rewards, difference_vectors):
        self.games_count += 1

        matrix_rewards = np.vstack(rewards).reshape((len(rewards), 1))
        discounted_rewards = NeuralNetwork.__discount_rewards__(matrix_rewards, self.gamma)
        normalized_discounted_rewards = NeuralNetwork.__normalize_discounted_rewards__(discounted_rewards)

        a_xs = np.vstack(input_layers)
        a_hs = np.vstack(hidden_layers)
        a_errs = np.vstack([difference_vectors])

        a_zerrs = a_errs * normalized_discounted_rewards

        if self.games_count % self.batch_size == 1:  # начинаем накапливать информацию о новом пакете игр
            self.a_xs = a_xs.copy()
            self.a_hs = a_hs.copy()
            self.a_zerrs = a_zerrs.copy()

        else:
            self.a_xs = np.vstack((self.a_xs, a_xs))
            self.a_hs = np.vstack((self.a_hs, a_hs))
            self.a_zerrs = np.vstack((self.a_zerrs, a_zerrs))

        grad_w = self.__policy_backward__(a_xs, a_hs, a_zerrs)

        for k in self.model:
            self.grad_buffer[k] += grad_w[k]

        if self.games_count % self.batch_size == 0:  # корректировка весов - метод SGD
            print('Update neural network')
            for k, v in self.model.items():
                g = self.grad_buffer[k]
                self.model[k] -= self.learning_rate * g
                self.grad_buffer[k] = np.zeros_like(v)

            self.__save__()

    @staticmethod
    def __discount_rewards__(rewards, gamma):
        discounted_rewards = np.zeros_like(rewards) * 1.0
        addend = 0.0
        for i in reversed(range(0, rewards.size)):
            addend = addend * gamma + np.array(rewards[i])
            discounted_rewards[i] = addend

        return discounted_rewards

    @staticmethod
    def __normalize_discounted_rewards__(discounted_rewards):
        return discounted_rewards / np.std(discounted_rewards)

    def __policy_backward__(self, matrix_input_layers, matrix_hidden_layers, matrix_difference_vector):
        weights_2 = np.dot(matrix_difference_vector.T, matrix_hidden_layers)
        dh = np.dot(matrix_difference_vector, self.model[NeuralNetwork.WEIGHTS_2])
        dh[matrix_hidden_layers <= 0] = 0
        weights_1 = np.dot(dh.T, matrix_input_layers)
        return {NeuralNetwork.WEIGHTS_1: weights_1, NeuralNetwork.WEIGHTS_2: weights_2}

    def __init__(
            self,
            file_name,
            input_layer_size,
            hidden_layer_size,
            output_layer_size,
            learning_rate,
            gamma,
            delta,
            batch_size,
            decay_rate
    ):
        self.file_name = file_name
        self.input_layer_size = input_layer_size
        self.hidden_layer_size = hidden_layer_size
        self.output_layer_size = output_layer_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.delta = delta
        self.batch_size = batch_size
        self.decay_rate = decay_rate

        try:
            self.__try_load__()
        except OSError:
            self.__create__()
        pass

    def __create__(self):
        self.model = {
            NeuralNetwork.WEIGHTS_1:
                np.random.randn(self.hidden_layer_size, self.input_layer_size) / np.sqrt(self.input_layer_size),
            NeuralNetwork.WEIGHTS_2:
                np.random.randn(self.output_layer_size, self.hidden_layer_size) / np.sqrt(self.hidden_layer_size)
        }
        for k, v in self.model.items():
            self.grad_buffer[k] = np.zeros_like(v)

    @staticmethod
    def __get_latest_created_file__(file_name):
        directory = os.path.dirname(file_name)
        paths = glob.glob(f'{directory}/*')
        if paths:
            return max(paths, key=os.path.getctime)
        else:
            return file_name

    def __try_load__(self):
        latest_created_file = NeuralNetwork.__get_latest_created_file__(self.file_name)
        self.model = pickle.load(open(latest_created_file, 'rb'))
        for k, v in self.model.items():
            self.grad_buffer[k] = np.zeros_like(v)
        print(f'Loaded model from {latest_created_file}')

    def __save__(self):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        pickle.dump(self.model, open(f'{self.file_name}_{str(calendar.timegm(time.gmtime()))}', 'wb'))
