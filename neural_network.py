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

    model = {}

    def policy_forward(self, input_layer):
        hidden_layer = np.dot(self.model[NeuralNetwork.WEIGHTS_1], input_layer)
        hidden_layer[hidden_layer < 0] = 0  # ReLU nonlinearity
        z = np.dot(hidden_layer.tolist(), self.model[NeuralNetwork.WEIGHTS_2])
        normalized_output_layer = NeuralNetwork.__sigmoid__(z)
        return normalized_output_layer.tolist(), z.tolist(), hidden_layer.tolist()

    @staticmethod
    def __sigmoid__(x):
        return 1.0 / (1.0 + np.exp(-x))

    def update(self, input_layers, hidden_layers, rewards, difference_vector):
        discounted_rewards = NeuralNetwork.__discount_rewards__(rewards, self.gamma)
        normalized_discounted_rewards = NeuralNetwork.__normalize_discounted_rewards__(discounted_rewards)

        gradient = self.__policy_backward__(
            np.vstack(input_layers),
            np.vstack(hidden_layers),
            np.vstack(difference_vector) * np.vstack(normalized_discounted_rewards)
        )

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

        self.model[NeuralNetwork.WEIGHTS_1] -= self.learning_rate * gradient[NeuralNetwork.WEIGHTS_1]
        self.model[NeuralNetwork.WEIGHTS_2] -= self.learning_rate * gradient[NeuralNetwork.WEIGHTS_2]

        self.__save__()

    @staticmethod
    def __discount_rewards__(rewards, gamma):
        discounted_rewards = [0] * len(rewards)
        addend = 0
        for i in reversed(range(0, len(rewards))):
            addend = addend * gamma + rewards[i]
            discounted_rewards[i] = addend
        return discounted_rewards

    @staticmethod
    def __normalize_discounted_rewards__(discounted_rewards):
        result = [float(discounted_reward) for discounted_reward in discounted_rewards]
        result /= np.std(result)
        return result.tolist()

    def __policy_backward__(
            self,
            matrix_input_layers,
            matrix_hidden_layers,
            matrix_difference_vector
    ):
        weights_2 = np.dot(matrix_hidden_layers.T, matrix_difference_vector)
        dhs = []
        for i in range(0, self.output_layer_size):
            dh = np.outer(matrix_difference_vector[:, i], self.model[NeuralNetwork.WEIGHTS_2][:, i])
            dh[dh < 0] = 0
            dhs.append(dh)
        weights_1 = np.sum([np.dot(dh.T, matrix_input_layers) for dh in dhs], axis=0)
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
            batch_size
    ):
        self.file_name = file_name
        self.input_layer_size = input_layer_size
        self.hidden_layer_size = hidden_layer_size
        self.output_layer_size = output_layer_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.delta = delta
        self.batch_size = batch_size

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
                np.random.randn(self.hidden_layer_size, self.output_layer_size) / np.sqrt(self.hidden_layer_size)
        }

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
        print(f'Loaded model from {latest_created_file}')

    def __save__(self):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        pickle.dump(self.model, open(f'{self.file_name}_{str(calendar.timegm(time.gmtime()))}', 'wb'))
