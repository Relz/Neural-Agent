import numpy as np
import random as rnd

from world_info_visualizer import WorldInfoVisualizer
from world_info import WorldInfo
from action import Action


class Agent:
    neural_network = None

    previous_state_hash = ''
    previous_action_name = ''
    previous_score = 0
    previous_weights_dictionary = {}

    input_layers = []
    hidden_layers = []
    rewards = []
    difference_vectors = []

    all_acts_dict = {
        'none': Action('noAct', 'noAct'),
        'take': Action('noAct', 'Take'),
        'go_forward': Action('noAct', 'Go'),
        'go_backward': Action('upSideDn', 'Go'),
        'go_left': Action('onLeft', 'Go'),
        'go_right': Action('onRight', 'Go'),
        'shoot_forward': Action('noAct', 'Shoot'),
        'shoot_backward': Action('upSideDn', 'Shoot'),
        'shoot_left': Action('onLeft', 'Shoot'),
        'shoot_right': Action('onRight', 'Shoot')
    }

    def play_game(self, server_helper):
        action = self.all_acts_dict['none']
        response = server_helper.make_step(action)

        if response is None:
            return None, 0

        response_code = None
        score = 0

        response_error = response['error']
        world_info = WorldInfo.parse(response['text'])
        print()
        WorldInfoVisualizer.draw_in_console(world_info)
        print()
        state_hash = Agent.__get_state_hash__(world_info)
        self.previous_action_name = 'none'
        self.previous_score = score
        self.previous_state_hash = state_hash

        while self.__game_not_over__(response_error):
            if response is not None:
                action_name = self.__choose_action__(state_hash, world_info.agent_info.direction)
                print(f'Action: {action_name}')
                action = self.all_acts_dict[action_name]
                self.previous_score = score
                self.previous_state_hash = state_hash
                self.previous_action_name = action_name

            response = None
            while response is None:
                try:
                    response = server_helper.make_step(action)
                except ConnectionError:
                    print('WARNING! Server connection failed, retry...')

            response_error = response['error']
            world_info = WorldInfo.parse(response['text'])
            WorldInfoVisualizer.draw_in_console(world_info)
            score = world_info.agent_info.score
            response_code = int(response['text']['code'])
            state_hash = Agent.__get_state_hash__(world_info)
            self.rewards.append(score - self.previous_score)

        print('Код завершения:', response_error)

        self.neural_network.update(self.input_layers, self.hidden_layers, self.rewards, self.difference_vectors)
        self.input_layers = []
        self.hidden_layers = []
        self.rewards = []
        self.difference_vectors = []

        return response_code, score

    def __init__(self, neural_network):
        self.neural_network = neural_network

    @staticmethod
    def __get_state_hash__(world_info):
        agent_direction = world_info.agent_info.direction
        return f'{int(world_info.is_monster_alive)}' \
               f'{world_info.agent_info.arrow_count}' \
               f'{world_info.agent_info.leg_count}' \
               f'{Agent.__get_current_cave_state_hash__(world_info.perception.current_cave)}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_top_cave(agent_direction))}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_top_right_cave(agent_direction))}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_right_cave(agent_direction))}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_bottom_right_cave(agent_direction))}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_bottom_cave(agent_direction))}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_bottom_left_cave(agent_direction))}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_left_cave(agent_direction))}' \
               f'{Agent.__get_near_cave_state_hash__(world_info.perception.get_top_left_cave(agent_direction))}'

    @staticmethod
    def __get_current_cave_state_hash__(cave):
        return f'{int(cave.has_gold if cave.has_gold is not None else 2)}' \
               f'{int(cave.has_wind if cave.has_wind is not None else 2)}' \
               f'{int(cave.has_hole if cave.has_hole is not None else 2)}' \
               f'{int(cave.has_bones if cave.has_bones is not None else 2)}'

    @staticmethod
    def __get_near_cave_state_hash__(cave):
        return f'{Agent.__get_current_cave_state_hash__(cave)}' \
               f'{int(cave.is_wall)}' \
               f'{int(cave.is_visible if cave.is_visible is not None else 2)}'

    @staticmethod
    def __game_not_over__(request_error):
        return request_error is None

    def __choose_action__(self, state_hash, agent_direction):
        input_layer = Agent.__state_hash_to_int_vector__(state_hash)
        output_layer, hidden_layer = self.neural_network.policy_forward(input_layer)

        if rnd.random() < 0.75:
            weights = self.__correct_weights__(output_layer.copy(), input_layer, agent_direction)
        else:
            weights = output_layer.copy()

        difference_vector = (np.array(self.__get_absolute_weights__(weights)) - output_layer)

        self.input_layers.append(input_layer)
        self.hidden_layers.append(hidden_layer)
        self.difference_vectors.append(difference_vector)

        self.previous_weights_dictionary = dict(
            zip(
                [
                    'take',
                    'go_forward',
                    'go_backward',
                    'go_left',
                    'go_right',
                    'shoot_forward',
                    'shoot_backward',
                    'shoot_left',
                    'shoot_right'
                ],
                tuple(weights)
            )
        )

        return Agent.__get_action_by_weight__(self.previous_weights_dictionary)

    # преобразуем символьный хэш в числовой входной вектор для нейросети
    @staticmethod
    def __state_hash_to_int_vector__(state_hash):
        return [int(char) for char in state_hash]

    @staticmethod
    def __correct_weights__(weights, state_hash, agent_direction):
        # 0: 'take',
        # 1: 'go_forward',
        # 2: 'go_backward',
        # 3: 'go_left',
        # 4: 'go_right',
        # 5: 'shoot_forward',
        # 6: 'shoot_backward',
        # 7: 'shoot_left',
        # 8: 'shoot_right'

        result = weights.copy()

        current_cave_has_gold = state_hash[3] == 1
        if current_cave_has_gold:  # надо брать клад
            result = np.ones(len(result)) * 0
            result[0] = 1
        else:  # клада нет => пытаться брать не надо
            result[0] = 0

            is_monster_alive = state_hash[0] == 1
            is_monster_near = state_hash[6] == 1
            has_arrows = state_hash[1] != 0
            if (not is_monster_alive) or (not has_arrows) or (not is_monster_near):
                # монстр мёртв или нет стрел или рядом нет монстра => не стрелять куда-либо
                result[5] = result[6] = result[7] = result[8] = 0

            is_top_cave_wall = state_hash[11] == 1
            is_right_cave_wall = state_hash[11 + 12] == 1
            is_bottom_cave_wall = state_hash[11 + 12 * 2] == 1
            is_left_cave_wall = state_hash[11 + 12 * 3] == 1

            if Agent.__is_forward_cave_wall__(
                    agent_direction,
                    is_top_cave_wall,
                    is_right_cave_wall,
                    is_bottom_cave_wall,
                    is_left_cave_wall
            ):
                result[1] = result[5] = 0

            if Agent.__is_right_cave_wall__(
                    agent_direction,
                    is_top_cave_wall,
                    is_right_cave_wall,
                    is_bottom_cave_wall,
                    is_left_cave_wall
            ):
                result[4] = result[8] = 0

            if Agent.__is_behind_cave_wall__(
                    agent_direction,
                    is_top_cave_wall,
                    is_right_cave_wall,
                    is_bottom_cave_wall,
                    is_left_cave_wall
            ):
                result[2] = result[6] = 0

            if Agent.__is_left_cave_wall__(
                    agent_direction,
                    is_top_cave_wall,
                    is_right_cave_wall,
                    is_bottom_cave_wall,
                    is_left_cave_wall
            ):
                result[3] = result[7] = 0

            is_last_leg = state_hash[2] == 1  # одна нога => не проходим через яму
            if is_last_leg:
                has_top_cave_hole = state_hash[9] == 1
                has_right_cave_hole = state_hash[9 + 12] == 1
                has_bottom_cave_hole = state_hash[9 + 12 * 2] == 1
                has_left_cave_hole = state_hash[9 + 12 * 3] == 1

                if Agent.__has_forward_cave_hole__(
                        agent_direction,
                        has_top_cave_hole,
                        has_right_cave_hole,
                        has_bottom_cave_hole,
                        has_left_cave_hole
                ):
                    result[1] = 0

                if Agent.__has_right_cave_hole__(
                        agent_direction,
                        has_top_cave_hole,
                        has_right_cave_hole,
                        has_bottom_cave_hole,
                        has_left_cave_hole
                ):
                    result[4] = 0

                if Agent.__has_behind_cave_hole__(
                        agent_direction,
                        has_top_cave_hole,
                        has_right_cave_hole,
                        has_bottom_cave_hole,
                        has_left_cave_hole
                ):
                    result[2] = 0

                if Agent.__has_left_cave_hole__(
                        agent_direction,
                        has_top_cave_hole,
                        has_right_cave_hole,
                        has_bottom_cave_hole,
                        has_left_cave_hole
                ):
                    result[3] = 0

                is_top_cave_visible = state_hash[12] == 1
                is_right_cave_visible = state_hash[12 * 2] == 1
                is_bottom_cave_visible = state_hash[12 * 3] == 1
                is_left_cave_visible = state_hash[12 * 4] == 1

                if Agent.__is_forward_cave_visible__(
                        agent_direction,
                        is_top_cave_visible,
                        is_right_cave_visible,
                        is_bottom_cave_visible,
                        is_left_cave_visible
                ):
                    result[1] *= 0.2
                    result[5] = 0

                if Agent.__is_right_cave_visible__(
                        agent_direction,
                        is_top_cave_visible,
                        is_right_cave_visible,
                        is_bottom_cave_visible,
                        is_left_cave_visible
                ):
                    result[4] *= 0.2
                    result[8] = 0

                if Agent.__is_behind_cave_visible__(
                        agent_direction,
                        is_top_cave_visible,
                        is_right_cave_visible,
                        is_bottom_cave_visible,
                        is_left_cave_visible
                ):
                    result[2] *= 0.2
                    result[6] = 0

                if Agent.__is_left_cave_visible__(
                        agent_direction,
                        is_top_cave_visible,
                        is_right_cave_visible,
                        is_bottom_cave_visible,
                        is_left_cave_visible
                ):
                    result[3] *= 0.2
                    result[7] = 0

        return result

    @staticmethod
    def __is_forward_cave_wall__(
            pivot_direction,
            is_top_cave_wall,
            is_right_cave_wall,
            is_bottom_cave_wall,
            is_left_cave_wall
    ):
        return {
            'Up': is_top_cave_wall,
            'Right': is_right_cave_wall,
            'Down': is_bottom_cave_wall,
            'Left': is_left_cave_wall
        }[pivot_direction]

    @staticmethod
    def __is_right_cave_wall__(
            pivot_direction,
            is_top_cave_wall,
            is_right_cave_wall,
            is_bottom_cave_wall,
            is_left_cave_wall
    ):
        return {
            'Up': is_right_cave_wall,
            'Right': is_bottom_cave_wall,
            'Down': is_left_cave_wall,
            'Left': is_top_cave_wall
        }[pivot_direction]

    @staticmethod
    def __is_behind_cave_wall__(
            pivot_direction,
            is_top_cave_wall,
            is_right_cave_wall,
            is_bottom_cave_wall,
            is_left_cave_wall
    ):
        return {
            'Up': is_bottom_cave_wall,
            'Right': is_left_cave_wall,
            'Down': is_top_cave_wall,
            'Left': is_right_cave_wall
        }[pivot_direction]

    @staticmethod
    def __is_left_cave_wall__(
            pivot_direction,
            is_top_cave_wall,
            is_right_cave_wall,
            is_bottom_cave_wall,
            is_left_cave_wall
    ):
        return {
            'Up': is_left_cave_wall,
            'Right': is_top_cave_wall,
            'Down': is_right_cave_wall,
            'Left': is_bottom_cave_wall
        }[pivot_direction]

    @staticmethod
    def __has_forward_cave_hole__(
            pivot_direction,
            has_top_cave_hole,
            has_right_cave_hole,
            has_bottom_cave_hole,
            has_left_cave_hole
    ):
        return {
            'Up': has_top_cave_hole,
            'Right': has_right_cave_hole,
            'Down': has_bottom_cave_hole,
            'Left': has_left_cave_hole
        }[pivot_direction]

    @staticmethod
    def __has_right_cave_hole__(
            pivot_direction,
            has_top_cave_hole,
            has_right_cave_hole,
            has_bottom_cave_hole,
            has_left_cave_hole
    ):
        return {
            'Up': has_right_cave_hole,
            'Right': has_bottom_cave_hole,
            'Down': has_left_cave_hole,
            'Left': has_top_cave_hole
        }[pivot_direction]

    @staticmethod
    def __has_behind_cave_hole__(
            pivot_direction,
            has_top_cave_hole,
            has_right_cave_hole,
            has_bottom_cave_hole,
            has_left_cave_hole
    ):
        return {
            'Up': has_bottom_cave_hole,
            'Right': has_left_cave_hole,
            'Down': has_top_cave_hole,
            'Left': has_right_cave_hole
        }[pivot_direction]

    @staticmethod
    def __has_left_cave_hole__(
            pivot_direction,
            has_top_cave_hole,
            has_right_cave_hole,
            has_bottom_cave_hole,
            has_left_cave_hole
    ):
        return {
            'Up': has_left_cave_hole,
            'Right': has_top_cave_hole,
            'Down': has_right_cave_hole,
            'Left': has_bottom_cave_hole
        }[pivot_direction]

    @staticmethod
    def __is_forward_cave_visible__(
            pivot_direction,
            is_top_cave_visible,
            is_right_cave_visible,
            is_bottom_cave_visible,
            is_left_cave_visible
    ):
        return {
            'Up': is_top_cave_visible,
            'Right': is_right_cave_visible,
            'Down': is_bottom_cave_visible,
            'Left': is_left_cave_visible
        }[pivot_direction]

    @staticmethod
    def __is_right_cave_visible__(
            pivot_direction,
            is_top_cave_visible,
            is_right_cave_visible,
            is_bottom_cave_visible,
            is_left_cave_visible
    ):
        return {
            'Up': is_right_cave_visible,
            'Right': is_bottom_cave_visible,
            'Down': is_left_cave_visible,
            'Left': is_top_cave_visible
        }[pivot_direction]

    @staticmethod
    def __is_behind_cave_visible__(
            pivot_direction,
            is_top_cave_visible,
            is_right_cave_visible,
            is_bottom_cave_visible,
            is_left_cave_visible
    ):
        return {
            'Up': is_bottom_cave_visible,
            'Right': is_left_cave_visible,
            'Down': is_top_cave_visible,
            'Left': is_right_cave_visible
        }[pivot_direction]

    @staticmethod
    def __is_left_cave_visible__(
            pivot_direction,
            is_top_cave_visible,
            is_right_cave_visible,
            is_bottom_cave_visible,
            is_left_cave_visible
    ):
        return {
            'Up': is_left_cave_visible,
            'Right': is_top_cave_visible,
            'Down': is_right_cave_visible,
            'Left': is_bottom_cave_visible
        }[pivot_direction]

    # получить случайное действие с вероятностью, зависящей от его веса-полезности
    @staticmethod
    def __get_action_by_weight__(curr_weights_dict):
        acts = np.array(list(curr_weights_dict.keys()))
        weights = np.array(list(curr_weights_dict.values()), dtype=float)

        limit_weight = 0
        max_weight = np.max(weights)
        if max_weight <= limit_weight:
            limit_weight = weights[weights.argsort()[-2]]  # страхуем себя на случай безвыходной ситуации
        acts = acts[weights >= limit_weight]
        weights = weights[weights >= limit_weight]

        min_weight = np.min(weights)
        weights = weights - min_weight + 0.001
        normalized_weights = weights / np.sum(weights)

        return rnd.choices(population=list(acts), weights=normalized_weights)[0]

    @staticmethod
    def __get_absolute_weights__(weights):
        result = np.zeros_like(weights)
        result[np.array(weights).argmax()] = 1
        return result.tolist()
