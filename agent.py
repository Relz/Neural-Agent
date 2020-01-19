import numpy as np
import random as rnd

from world_info import WorldInfo


class Agent:
    state_hash = 0

    all_acts_dict = {
        'none': ['noAct', 'noAct'],
        'take': ['noAct', 'Take'],
        'go_forward': ['noAct', 'Go'],
        'go_back': ['upSideDn', 'Go'],
        'go_left': ['onLeft', 'Go'],
        'go_right': ['onRight', 'Go'],
        'shoot_forward': ['noAct', 'Shoot'],
        'shoot_back': ['upSideDn', 'Shoot'],
        'shoot_left': ['onLeft', 'Shoot'],
        'shoot_right': ['onRight', 'Shoot']
    }

    def play_game(self, server_helper):
        actions = self.all_acts_dict['none']
        response = server_helper.make_step(actions[0], actions[1])

        response_code = None
        score = 0

        if response is not None:
            response_error = response['error']
            world_info = WorldInfo.parse(response['text'])

            while self.__game_not_over__(response_error):
                if response is not None:
                    actions = self.__chooseAct__(world_info)

                response = server_helper.make_step(actions[0], actions[1])

                if response is not None:
                    response_error = response['error']
                    world_info = WorldInfo.parse(response['text'])
                    score = world_info.agent_info.score
                    response_code = int(response['text']['code'])
                else:
                    print('WARNING! Server was not responded.')

            print('Код завершения:', response_error)

        return response_code, score

    @staticmethod
    def __game_not_over__(request_error):
        return request_error is None

    def __chooseAct__(self, world_info):
        weights_dict = self.__calcWeights__(world_info)
        curr_act, acts = self.__getActionByWeight__(weights_dict)

        return acts

    # оценить веса-полезности ходов, используя состояние мира
    def __calcWeights__(self, world_info):
        current_cave = world_info.current_cave
        front_cave = world_info.perception.front_cave
        right_cave = world_info.perception.right_cave
        behind_cave = world_info.perception.behind_cave
        left_cave = world_info.perception.left_cave
        # ------------ создаем словарь состояний окружающих пещер ------------
        all_caves = {'forward': front_cave, 'right': right_cave, 'back': behind_cave, 'left': left_cave}
        agent_direction = world_info.agent_info.direction
        arrow_count = world_info.agent_info.arrow_count
        directions = world_info.agent_info.direction_list
        min_w = -50
        max_w = 100
        all_actions = list(self.all_acts_dict.keys())[1:len(self.all_acts_dict)]
        weights = np.array(range(len(all_actions))) * 0 + min_w
        weights_dict = dict(zip(all_actions, weights))

        if current_cave.has_gold:
            weights_dict['take'] = max_w
        else:
            # обнуляем полезности возможных ходов; все остальыне остаются с min_w
            for direction in directions:
                shift_direction = self.__chooseRotation__(agent_direction, direction)
                weights_dict['go' + '_' + shift_direction] = 0
                weights_dict['shoot' + '_' + shift_direction] = 0

            # не надо пытаться стрелять - ЕСЛИ монстр мертв или стрел нет или рядом нет монстра
            if (not world_info.is_monster_alive) or (arrow_count == 0) or (not current_cave.has_bones):
                for direction in directions:
                    shift_direction = self.__chooseRotation__(agent_direction, direction)
                    weights_dict['shoot' + '_' + shift_direction] = min_w

            # вычисляем монстра, ЕСЛИ монстр жив и есть стрелы и он рядом
            if world_info.is_monster_alive and (arrow_count > 0) and current_cave.has_bones:
                for direction in directions:
                    shift_direction = self.__chooseRotation__(agent_direction, direction)
                    near_cave = all_caves[shift_direction]
                    if near_cave.has_monster:
                        weights_dict['shoot' + '_' + shift_direction] = max_w

        return weights_dict

    # получить случайное действие с вероятностью, зависящей от его веса-полезности
    def __getActionByWeight__(self, curr_weights_dict):
        acts = np.array(list(curr_weights_dict.keys()))
        weights = np.array(list(curr_weights_dict.values()), dtype=float)

        # сдвигаем все полезности в положительную область; минимальная полезность = 0,01
        min_weight = np.min(weights)
        weights = weights - min_weight + 0.01
        # нормируем, чтобы в сумме полезности давали 1
        weights_array = weights / np.sum(weights)

        # делаем случайный выбор в соответствии с полезностями
        curr_act = rnd.choices(population=list(acts), weights=weights_array)[0]
        acts = self.all_acts_dict[curr_act]

        return curr_act, acts

    # определение того, куда надо повернуться от текущего направления движения Агента к новому направлению
    @staticmethod
    def __chooseRotation__(current_direction, new_direction):
        all_shifts = {0: 'forward', 1: 'right', 2: 'back', 3: 'left'}
        all_directions_index = {'Up': 0, 'Right': 1, 'Down': 2, 'Left': 3}
        direction_diff = (all_directions_index[new_direction] - all_directions_index[current_direction] + 4) % 4
        return all_shifts[direction_diff]
