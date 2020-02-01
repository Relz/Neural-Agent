from agent import Agent
from neural_network import NeuralNetwork


class AgentManager:
    server_helper_creators = []
    attempt_count = 0
    alpha = 0
    gamma = 0
    delta = 0
    batch_size = 0

    def check(self, iteration_count):
        print('Кол-во итераций:', iteration_count)
        print('Кол-во попыток:', self.attempt_count)

        agent = Agent(
            NeuralNetwork(
                file_name=self.file_name,
                input_layer_size=self.input_layer_size,
                hidden_layer_size=self.hidden_layer_size,
                output_layer_size=self.output_layer_size,
                alpha=self.alpha,
                gamma=self.gamma,
                delta=self.delta,
                batch_size=self.batch_size
            )
        )

        for server_helper_creator in self.server_helper_creators:
            for iteration_number in range(1, iteration_count + 1):
                iteration_game_count = 0
                iteration_win_count = 0
                iteration_score_count = 0

                for attempt_number in range(1, self.attempt_count + 1):
                    code, score = agent.play_game(server_helper_creator())

                    if code is None:
                        print('Неудачное подключение для попытки №:', attempt_number)
                    else:
                        iteration_game_count += 1
                        if code == 2:
                            iteration_score_count += score
                            iteration_win_count += 1

                print('Закончилась итерация №' + str(iteration_number))
                print('\tИгр в итерации:', iteration_game_count)
                print('\tWin rate:', self.__calculate_win_rate__(iteration_win_count, iteration_game_count))
                print('\tScore rate:', self.__calculate_score_rate__(iteration_score_count, iteration_game_count))

    def __init__(
            self,
            server_helper_creators,
            attempts_count,
            file_name,
            input_layer_size,
            hidden_layer_size,
            output_layer_size,
            alpha,
            gamma,
            delta,
            batch_size
    ):
        self.server_helper_creators = server_helper_creators
        self.attempt_count = attempts_count
        self.file_name = file_name
        self.input_layer_size = input_layer_size
        self.hidden_layer_size = hidden_layer_size
        self.output_layer_size = output_layer_size
        self.alpha = alpha
        self.gamma = gamma
        self.delta = delta
        self.batch_size = batch_size

    @staticmethod
    def __calculate_win_rate__(win_count, game_count):
        return AgentManager.__calculate_rate__(win_count * 100, game_count)

    @staticmethod
    def __calculate_score_rate__(score_count, game_count):
        return AgentManager.__calculate_rate__(score_count, game_count)

    @staticmethod
    def __calculate_rate__(x, total):
        return x / total if total > 0 else 0

