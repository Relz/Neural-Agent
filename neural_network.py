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

    gamesQ = 0

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
        self.gamesQ += 1

        matrix_reward = np.vstack(rewards).reshape((len(rewards), 1))
        discounted_rewards = NeuralNetwork.__discount_rewards__(matrix_reward, self.gamma)
        normalized_discounted_rewards = NeuralNetwork.__normalize_discounted_rewards__(discounted_rewards)

        # gradient = self.__policy_backward_bias__(
        #     np.vstack(input_layers),
        #     np.vstack(hidden_layers),
        #     np.vstack(difference_vector) * np.vstack(normalized_discounted_rewards)
        # )

        # Алгоритм обратного распространения ошибки с лекции
        #
        # for i in range(len(input_layers)):
        #     difference = difference_vector[i]
        #     hidden_layer = hidden_layers[i]
        #     input_layer = input_layers[i]
        #     z = zs[i]
        #     normalized_discounted_reward = normalized_discounted_rewards[i]
        #
        #     dW2 = ((( difference * self.__sigmoid__(z) * (1 - self.__sigmoid__(z)) ))) ** hidden_layer
        #     difference_hidden_layer = ((( difference * self.__sigmoid__(z) * (1 - self.__sigmoid__(z)) ))) ** dW2
        #     difference_hidden_layer[hidden_layer < 0] = 0
        #     dW1 = difference ** input_layer
        #
        #     W1 += dW1 * normalized_discounted_reward * self.learning_rate
        #     W2 += dW2 * normalized_discounted_reward * self.learning_rate
        #

        # self.r_m_s_prop_cache[NeuralNetwork.WEIGHTS_1] =\
        #     self.decay_rate * self.r_m_s_prop_cache[NeuralNetwork.WEIGHTS_1] +\
        #     (1 - self.decay_rate) * gradient[NeuralNetwork.WEIGHTS_1] ** 2
        # self.r_m_s_prop_cache[NeuralNetwork.WEIGHTS_2] =\
        #     self.decay_rate * self.r_m_s_prop_cache[NeuralNetwork.WEIGHTS_2] +\
        #     (1 - self.decay_rate) * gradient[NeuralNetwork.WEIGHTS_2] ** 2
        #
        # self.model[NeuralNetwork.WEIGHTS_1] -=\
        #     np.nan_to_num(self.learning_rate * gradient[NeuralNetwork.WEIGHTS_1] /
        #                   (np.sqrt(self.r_m_s_prop_cache[NeuralNetwork.WEIGHTS_1]) + 0.00001))
        #
        # self.model[NeuralNetwork.WEIGHTS_2] -=\
        #     np.nan_to_num(self.learning_rate * gradient[NeuralNetwork.WEIGHTS_2] /
        #                   (np.sqrt(self.r_m_s_prop_cache[NeuralNetwork.WEIGHTS_2]) + 0.00001))

        a_xs = np.vstack(input_layers)
        a_hs = np.vstack(hidden_layers)
        a_errs = np.vstack([difference_vectors])
        a_rs = np.vstack(rewards)

        a_zerrs = a_errs * normalized_discounted_rewards

        if self.gamesQ % self.batch_size == 1:  # начинаем накапливать информацию о новом пакете игр
            self.a_xs = a_xs.copy()
            self.a_hs = a_hs.copy()
            self.a_zerrs = a_zerrs.copy()

        else:
            self.a_xs.extend(a_xs)
            self.a_hs.extend(a_hs)
            self.a_zerrs.extend(a_zerrs)

        grad_w = self.__policy_backward_bias__(a_xs, a_hs, a_zerrs)

        for k in self.model:
            self.grad_buffer[k] += grad_w[k]  # accumulate grad over batch

        if self.gamesQ % self.batch_size == 0:  # корректировка весов - метод rmsprop
            for k, v in self.model.items():
                g = self.grad_buffer[k]  # gradient
                self.r_m_s_prop_cache[k] = self.decay_rate * self.r_m_s_prop_cache[k] + (1 - self.decay_rate) * g ** 2
                self.model[k] += self.learning_rate * g / (np.sqrt(self.r_m_s_prop_cache[k]) + 1e-5)
                self.grad_buffer[k] = np.zeros_like(v)  # reset batch gradient buffer

        self.__save__()

    # @staticmethod
    # def __discount_rewards__(rewards, gamma):
    #     discounted_rewards = [0] * len(rewards)
    #     addend = 0
    #     for i in reversed(range(0, len(rewards))):
    #         addend = addend * gamma + np.array(rewards[i])
    #         discounted_rewards[i] = addend
    #     return discounted_rewards

    @staticmethod
    def __discount_rewards__(rewards, gamma):
        discounted_r = np.zeros_like(rewards) * 1.0
        running_add = 0.0
        for t in reversed(range(0, rewards.size)):
            running_add = running_add * gamma + np.array(rewards[t])
            discounted_r[t] = running_add

        return discounted_r

    @staticmethod
    def __normalize_discounted_rewards__(discounted_rewards):
        return discounted_rewards / np.std(discounted_rewards)

    # def __policy_backward__(
    #         self,
    #         matrix_input_layers,
    #         matrix_hidden_layers,
    #         matrix_difference_vector
    # ):
    #     weights_2 = np.dot(matrix_hidden_layers.T, matrix_difference_vector)
    #     dhs = []
    #     for i in range(0, self.output_layer_size):
    #         dh = np.outer(matrix_difference_vector[:, i], self.model[NeuralNetwork.WEIGHTS_2][:, i])
    #         dh[dh < 0] = 0
    #         dhs.append(dh)
    #     weights_1 = np.sum([np.dot(dh.T, matrix_input_layers) for dh in dhs], axis=0)
    #     return {NeuralNetwork.WEIGHTS_1: weights_1, NeuralNetwork.WEIGHTS_2: weights_2}

    def __policy_backward_bias__(self, matrix_input_layers, matrix_hidden_layers, matrix_difference_vector):
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
        self.r_m_s_prop_cache = self.model.copy()
        for k, v in self.model.items():
            self.grad_buffer[k] = np.zeros_like(v)
            self.r_m_s_prop_cache[k] = np.zeros_like(v)

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
        self.r_m_s_prop_cache = self.model.copy()
        for k, v in self.model.items():
            self.grad_buffer[k] = np.zeros_like(v)
            self.r_m_s_prop_cache[k] = np.zeros_like(v)
        print(f'Loaded model from {latest_created_file}')

    def __save__(self):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        pickle.dump(self.model, open(f'{self.file_name}_{str(calendar.timegm(time.gmtime()))}', 'wb'))
