#! /usr/bin/python3

import numpy as np
import random as rnd
import requests as req


# ===================  установка связи с сервером  =====================
def connect_to_server(user_id, case_id, map_num, acts=None, tournament_id=0, hash_id=0):
    if acts is None:
        acts = ['noAct', 'noAct']

    # proxy_dict = {
    #     "http": "http://10.0.0.4:3128",
    #     "https": "https://10.0.0.4:3128"
    # }

    if tournament_id != 0:  # если соревнования
        url = 'https://mooped.net/local/its/tournament/agentaction/'
        resp = req.get(url,
                       params={
                           'tid': tournament_id,
                           'userid': user_id,
                           'passive': acts[0], 'active': acts[1],
                           'checksituations': 1},
                       # proxies=proxy_dict,
                       verify=False)
    elif hash_id != 0:  # если контрольное тестирование
        url = 'https://mooped.net/local/its/tests/agentaction/'
        resp = req.get(url,
                       params={
                           'hash': hash_id,
                           'passive': acts[0], 'active': acts[1],
                           'checksituations': 1},
                       # proxies=proxy_dict,
                       verify=False)
    else:  # если нет соревнований и контрольного тестирования, то тестируем на карте mapnum
        url = 'https://mooped.net/local/its/game/agentaction/'
        # print(url + "?caseid=" + str(case_id) + "&userid=" + str(user_id) + "&mapnum=" + str(map_num) + "&passive=" + acts[0] + "&active=" + acts[1] + "&checksituations=1")
        resp = req.get(url,
                       params={
                           'caseid': case_id,
                           'userid': user_id,
                           'mapnum': map_num,
                           'passive': acts[0], 'active': acts[1],
                           'checksituations': 1},
                       # proxies=proxy_dict,
                       verify=False)

    json = None
    if resp.status_code == 200:
        # print("----- соединение установлено -----")
        json = resp.json()
    return json


# простой агент, использующий полензости =======================================
class SimpleAgent:
    user_id = None
    case_id = None
    url = None

    prev_act = None
    prev_hash = None

    state = None
    my_state = None

    all_acts_dict = {
        "none": ["noAct", "noAct"],
        "take": ["noAct", "Take"],
        "go_forward": ["noAct", "Go"],
        "go_back": ["upSideDn", "Go"],
        "go_left": ["onLeft", "Go"],
        "go_right": ["onRight", "Go"],
        "shoot_forward": ["noAct", "Shoot"],
        "shoot_back": ["upSideDn", "Shoot"],
        "shoot_left": ["onLeft", "Shoot"],
        "shoot_right": ["onRight", "Shoot"]
    }

    # alldirs = ['Up', 'Right', 'Down', 'Left']

    # PUBLIC METHODS ==============================================================

    def play_game(self, map_num):
        actions = self.all_acts_dict["none"]
        request = connect_to_server(
            user_id=self.user_id,
            case_id=self.case_id,
            map_num=map_num,
            acts=actions,
            tournament_id=self.tournament_id,
            hash_id=self.hash_id)
        request_code = None
        curr_score = 0

        if request is not None:
            request_error = request["error"]
            perception = request["text"]

            while request_error is None:
                if request is not None:
                    self.__stateUpdate__(perception)
                    actions = self.__chooseAct__()

                request = connect_to_server(
                    user_id=self.user_id,
                    case_id=self.case_id,
                    map_num=map_num, acts=actions,
                    tournament_id=self.tournament_id,
                    hash_id=self.hash_id)

                if request is not None:
                    request_error = request["error"]
                    perception = request["text"]
                    curr_score = perception["iagent"]["score"]
                    request_code = int(request["text"]["code"])
                else:
                    print("WARNING! Server was not responded.")

            print("Код завершения: ", request_error)

        return request_code, curr_score

    # PRIVATE METHODS =============================================================

    def __init__(self, user_id, case_id, tournament_id, hash_id):
        self.user_id = user_id
        self.case_id = case_id
        self.tournament_id = tournament_id
        self.hash_id = hash_id
        self.state_hash = 0

    # обновление состояния мира по восприятию
    def __stateUpdate__(self, perception):
        i_agent = perception['iagent']
        known_caves = i_agent['knowCaves']
        cur_cave = known_caves[i_agent['cavenum']]
        world_info = perception['worldinfo']
        situation = perception['perception']
        self.state_hash = self.__getHash__(perception)

        # простой рефлексирующий агент - использует только текущее восприятие
        self.state = {
            'curcave': cur_cave,
            'front_cave': situation['front_cave'],
            'right_cave': situation['right_cave'],
            'behind_cave': situation['behind_cave'],
            'left_cave': situation['left_cave'],
            'worldinfo': world_info,
            'agentdir': i_agent['dir'],
            'dirs': i_agent['dirList'],
            'lastMove': i_agent['choosenact'],
            'arrowsQ': int(i_agent['arrowcount']),
            'legsQ': int(i_agent['legscount'])
         }

    # выбор следующего шага
    # обновление полезности хода
    def __chooseAct__(self):
        # оцениваем веса-полезности каждого хода (новое состояние мира уже должно быть рассчитано)
        weights_dict = self.__calcWeights__()

        # выбираем текущий ход по рассичтанным полезностям
        curr_act, acts = self.__getActionByWeight__(weights_dict)

        return acts

    # оценить веса-полезности ходов, используя состояние мира
    def __calcWeights__(self):
        cur_cave = self.state['curcave']
        front_cave = self.state['front_cave']
        right_cave = self.state['right_cave']
        behind_cave = self.state['behind_cave']
        left_cave = self.state['left_cave']
        # ------------ создаем словарь состояний окружающих пещер ------------
        all_caves = {"forward": front_cave, "right": right_cave, "back": behind_cave, "left": left_cave}
        agent_direction = self.state['agentdir']
        directions = self.state['dirs']
        world_info = self.state['worldinfo']
        min_w = -50
        max_w = 100
        all_actions = list(self.all_acts_dict.keys())[1:len(self.all_acts_dict)]
        weights = np.array(range(len(all_actions))) * 0 + min_w
        weights_dict = dict(zip(all_actions, weights))

        if cur_cave['isGold']:
            weights_dict['take'] = max_w
        else:
            # обнуляем полезности возможных ходов; все остальыне остаются с min_w
            for direction in directions:
                shift_direction = self.__chooseRotation__(agent_direction, direction)
                weights_dict["go" + "_" + shift_direction] = 0
                weights_dict["shoot" + "_" + shift_direction] = 0

            # не надо пытаться стрелять - ЕСЛИ монстр мертв или стрел нет или рядом нет монстра
            if (world_info['ismonsteralive'] == 0) or (self.state['arrowsQ'] == 0) or (not cur_cave['isBones']):
                for direction in directions:
                    shift_direction = self.__chooseRotation__(agent_direction, direction)
                    weights_dict["shoot" + "_" + shift_direction] = min_w

            # вычисляем монстра, ЕСЛИ монстр жив и есть стрелы и он рядом
            if (world_info['ismonsteralive'] == 1) and (self.state['arrowsQ'] > 0) and (cur_cave['isBones'] == 1):
                for direction in directions:
                    shift_direction = self.__chooseRotation__(agent_direction, direction)
                    near_cave = all_caves[shift_direction]
                    if near_cave['isMonster'] == 1:
                        weights_dict["shoot" + "_" + shift_direction] = max_w

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
        all_shifts = {0: "forward", 1: "right", 2: "back", 3: "left"}
        all_directions_index = {'Up': 0, 'Right': 1, 'Down': 2, 'Left': 3}
        direction_diff = (all_directions_index[new_direction] - all_directions_index[current_direction] + 4) % 4
        return all_shifts[direction_diff]

    # получить хэш ситуации по восприятию
    def __getHash__(self, perception):
        is_monster_alive = str(int(perception["worldinfo"]["ismonsteralive"]))
        arrow_count = str(int(perception["iagent"]["arrowcount"]))
        legs_count = str(int(perception["iagent"]["legscount"]))
        curr_cave = perception["currentcave"]
        curr_cave_state = str(int(curr_cave["isGold"])) + str(int(curr_cave["isWind"])) + str(
            int(curr_cave["isBones"])) + str(int(curr_cave["isHole"]))
        front_cave_state = self.__get_near_cave_state__(perception["perception"]["front_cave"])
        back_cave_state = self.__get_near_cave_state__(perception["perception"]["behind_cave"])
        left_cave_state = self.__get_near_cave_state__(perception["perception"]["left_cave"])
        right_cave_state = self.__get_near_cave_state__(perception["perception"]["right_cave"])
        front_left_cave_state = self.__get_near_cave_state__(perception["perception"]["front_left_cave"])
        front_right_cave_state = self.__get_near_cave_state__(perception["perception"]["front_right_cave"])
        behind_left_cave_state = self.__get_near_cave_state__(perception["perception"]["behind_left_cave"])
        behind_right_cave_state = self.__get_near_cave_state__(perception["perception"]["behind_right_cave"])
        res = is_monster_alive + arrow_count + legs_count + curr_cave_state + front_cave_state + back_cave_state + left_cave_state + right_cave_state
        res = res + front_left_cave_state + front_right_cave_state + behind_left_cave_state + behind_right_cave_state

        return res

    def __get_near_cave_state__(self, cave):
        cave_state = "2222"
        if cave["isWall"] == 0:
            cave_state = "0222"
            if cave["isVisiable"] == 1:
                cave_state = "1" + str(int(cave["isWind"])) + str(int(cave["isBones"])) + str(int(cave["isHole"]))
        return cave_state
