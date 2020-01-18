#! /usr/bin/python3

import simp_agent
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Менеджер, организующий взаимодействие агента с миром
class Manager:
    url = None  # url сервера

    user_id = 0  # id пользователя
    case_id = 0  # id задачи

    map_numbers = []  # номера карт
    attempts_count = 0  # количество попыток на карте

    check_situations = 1  # получить информацию о всех пещерах вокруг

    # PUBLIC METHODS ==============================================================

    # Запуск проверки агента
    def check(self, iter_count=1):
        agent = simp_agent.SimpleAgent(
            user_id=self.user_id,
            case_id=self.case_id,
            tournament_id=self.tournament_id,
            hash_id=self.hash_id
        )

        print("Start checking.")
        print("Iteration count: ", iter_count, ", attempt count: ", self.attempts_count, ", map numbers: ",
              self.map_numbers)

        for it in range(1, iter_count + 1):
            iter_games_count = 0
            iter_wins_count = 0
            iter_score_count = 0
            for map_number in self.map_numbers:
                for attempt_num in range(1, self.attempts_count + 1):
                    code, score = agent.play_game(map_number)

                    if code is None:
                        print("Connection failed for: map = {0}, attempt = {1}".format(map_number, attempt_num))
                    else:
                        iter_games_count += 1
                        if code == 2:
                            iter_score_count += score
                            iter_wins_count += 1

            if iter_games_count > 0:
                iter_win_rate = (iter_wins_count * 100) / iter_games_count
                iter_score_rate = iter_score_count / iter_games_count
            else:
                iter_win_rate = 0
                iter_score_rate = 0

            print("************************************")
            print("Iteration: ", it, ", map: ", map_number)
            print("Games: ", iter_games_count, ", Win rate: ", iter_win_rate, ", Score rate: ", iter_score_rate)

    # PRIVATE METHODS =============================================================

    def __init__(self, session_parameters, map_parameters):
        self.user_id = session_parameters[0]
        self.case_id = session_parameters[1]
        self.tournament_id = session_parameters[2]
        self.hash_id = session_parameters[3]
        self.map_numbers = map_parameters[0]
        self.attempts_count = map_parameters[1]


case_id = 20  # id кейса задачи
user_id = 293  # id пользователя
tournament_id = 0  # для выбора турнира
hash_id = 0  # если контрольное тестирование

agent_name = "Elder"  # название агента
url = "https://mooped.net/local/its/game/agentaction/"  # url сервера

map_numbers = list(range(1, 2))  # список номеров карт, на которых будем проверять агента
attempts_per_map = 1  # количество попыток на каждую карту

# создать менеджера и запустить
obs = Manager([user_id, case_id, tournament_id, hash_id], [map_numbers, attempts_per_map])

start = time.time()
obs.check()
end = time.time()
print("Время проверки составило (мин) ", round((end - start) / 60))
