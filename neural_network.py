import pickle
import numpy as np


class NeuralNetwork:
    WEIGHTS_1 = 'Weights 1'
    WEIGHTS_2 = 'Weights 2'
    file_name = ''
    input_layer_size = 0
    hidden_layer_size = 0
    output_layer_size = 0
    alpha = 0
    gamma = 0
    delta = 0
    batch_size = 0

    model = {}

    def policy_forward(self, x):
        h = np.dot(self.model[NeuralNetwork.WEIGHTS_1], x)
        h[h < 0] = 0  # ReLU nonlinearity
        logp = np.dot(self.model[NeuralNetwork.WEIGHTS_2], h)
        p = NeuralNetwork.__sigmoid__(logp)
        return p, h  # return probability of taking action 2, and hidden state

    def policy_backward(model, epx, eph, epdlogp):
        """ backward pass. (eph is array of intermediate hidden states) """
        dW2 = np.dot(eph.T, epdlogp).ravel()
        dh = np.outer(epdlogp, model[NeuralNetwork.WEIGHTS_2])
        dh[eph <= 0] = 0  # backpro prelu
        dW1 = np.dot(dh.T, epx)
        return {NeuralNetwork.WEIGHTS_1: dW1, NeuralNetwork.WEIGHTS_2: dW2}

    def save(self):
        pickle.dump(self.model, open(self.file_name, 'wb'))

    def __init__(
            self,
            file_name,
            input_layer_size,
            hidden_layer_size,
            output_layer_size,
            alpha,
            gamma,
            delta,
            batch_size
    ):
        self.file_name = file_name
        self.input_layer_size = input_layer_size
        self.hidden_layer_size = hidden_layer_size
        self.output_layer_size = output_layer_size
        self.alpha = alpha
        self.gamma = gamma
        self.delta = delta
        self.batch_size = batch_size

        try:
            self.__try_load__()
        except OSError:
            self.__create__()

    def __create__(self):
        self.model = {
            NeuralNetwork.WEIGHTS_1:
                np.random.randn(self.hidden_layer_size, self.input_layer_size) / np.sqrt(self.input_layer_size),
            NeuralNetwork.WEIGHTS_2:
                np.random.randn(self.output_layer_size, self.hidden_layer_size) / np.sqrt(self.hidden_layer_size)
        }

    def __try_load__(self):
        self.model = pickle.load(open(self.file_name, 'rb'))

    # логистическая функция активации
    @staticmethod
    def __sigmoid__(x):
        return 1.0 / (1.0 + np.exp(-x))  # sigmoid "squashing" function to interval [0,1]
