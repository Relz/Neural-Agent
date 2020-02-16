import random

import urllib3
from agent_manager import AgentManager
from server_helper.server_helper_examination import ServerHelperExamination
from server_helper.server_helper_tournament import ServerHelperTournament
from server_helper.server_helper_training import ServerHelperTraining

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

name = 'Elder'
user_id = 293
# user_id = 3574
case_id = 0
# case_id = 1  # 2 обвала, 1 монстр (всё видно)
# case_id = 6  # 0 обвал, 0 монстр
# case_id = 7  # 1 обвал, 0 монстр
case_id = 20  # 1 обвал, 1 монстр
# case_id = 16  # 0 обвал, 1 монстр, монстр защищает клад
tournament_id = 0
# tournament_id = 40
hash_id = 0
# hash_id = '9c71bff4caf4c3a946b72f777fbe96fe'
map_numbers = random.sample(list(range(1, 251)), 50)
file_name = f'./neural_network_models/{name}'
input_layer_size = 3 + 4 + 6 * 8  # количество нейронов, описывающих состояние игры
hidden_layer_size = input_layer_size * 3   # произвольно подбираемое число
output_layer_size = 9  # кол-во возможных действий агента
learning_rate = 0.01  # фактор обучения
gamma = 0.5  # фактор дисконтирования
delta = 0.0001  # коэффициент уменьшения learning_rate
batch_size = 10  # размер пакета обучения: сколько игр нужно отыграть для начала анализа
decay_rate = 0.95  # коэффициент затухания для RMSProp leaky суммы квадрата градиента

agent_manager = AgentManager(
    server_helper_creators=
    ((lambda: [lambda: ServerHelperTournament(user_id, tournament_id)], lambda: [])[tournament_id == 0]()) +
    ((lambda: [lambda: ServerHelperExamination(hash_id)], lambda: [])[hash_id == 0]()) +
    (
        (
            lambda: list(map(lambda map_number: lambda: ServerHelperTraining(user_id, case_id, map_number), map_numbers)),
            lambda: []
        )[case_id == 0]()
    ),
    attempts_count=50,
    file_name=file_name,
    input_layer_size=input_layer_size,
    hidden_layer_size=hidden_layer_size,
    output_layer_size=output_layer_size,
    learning_rate=learning_rate,
    gamma=gamma,
    delta=delta,
    batch_size=batch_size,
    decay_rate=decay_rate
)

agent_manager.check(iteration_count=1)
