class Position:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def create_from_string(string):
        position_array = string.split('_')
        return Position(int(position_array[1]), int(position_array[0]))


class CaveInfo:
    is_wall = None
    id = None
    position = None
    has_gold = None
    has_monster = None
    has_hole = None
    has_wind = None
    has_bones = None
    is_visible = None
    direction_list = None
    is_safe = None

    @staticmethod
    def parse(json_data):
        cave_info = CaveInfo()
        if 'isWall' in json_data:
            cave_info.is_wall = json_data['isWall'] == 1
        else:
            cave_info.id = json_data['cNum']
            column = json_data['colN']
            row = json_data['rowN']
            cave_info.position = Position.create_from_string(f'{row}_{column}')
            if json_data['isGold'] != 'None':
                cave_info.has_gold = json_data['isGold'] == 1
            if json_data['isMonster'] != 'None':
                cave_info.has_monster = json_data['isMonster'] == 1
            if json_data['isHole'] != 'None':
                cave_info.has_hole = json_data['isHole'] == 1
            if json_data['isWind'] != 'None':
                cave_info.has_wind = json_data['isWind'] == 1
            if json_data['isBones'] != 'None':
                cave_info.has_bones = json_data['isBones'] == 1
            cave_info.is_visible = json_data['isVisiable'] == 1
            if 'dirList' in json_data:
                cave_info.direction_list = json_data['dirList']
            if 'isSafety' in json_data:
                cave_info.is_safe = json_data['isSafety']

        return cave_info


class AgentInfo:
    a_name = None
    is_alive = None
    leg_count = None
    arrow_count = None
    has_gold = None
    direction = None
    position = None
    visited_caves_info = None
    score = None
    direction_list = None
    actions_cost_list = None
    actions = None
    passive_moves = None
    active_moves = None
    w_state_utilities = None
    i_a_state_utilities = None
    world_info = None
    all_dirs = None
    chosen_action = None
    timestamp = None
    ga_id = None
    id = None

    @staticmethod
    def parse(json_data):
        result = AgentInfo()
        result.a_name = json_data['aname']
        result.is_alive = int(json_data['isagentalive']) == 1
        result.leg_count = int(json_data['legscount'])
        result.arrow_count = int(json_data['arrowcount'])
        result.has_gold = int(json_data['havegold']) == 1
        result.direction = json_data['dir']
        result.position = Position.create_from_string(json_data['cavenum'])
        result.visited_caves_info = dict(map(AgentInfo.__parse_visited_cave_pair__, json_data['knowCaves'].items()))
        result.score = json_data['score']
        result.direction_list = json_data['dirList']

        result.actions_cost_list = json_data['actsCostList']
        result.actions = json_data['acts']
        result.passive_moves = json_data['passivMoves']
        result.active_moves = json_data['activMoves']
        result.w_state_utilities = json_data['WStateUtilities']
        result.i_a_state_utilities = json_data['IAStateUtilities']
        result.world_info = json_data['worldInfo']
        result.all_dirs = json_data['allDirs']
        result.chosen_action = json_data['choosenact']
        result.timestamp = json_data['timestamp']
        result.ga_id = json_data['gaid']
        result.id = json_data['id']

        return result

    @staticmethod
    def __parse_visited_cave_pair__(visited_cave_pair):
        cave_id = visited_cave_pair[0]
        cave_json_data = visited_cave_pair[1]
        return Position.create_from_string(cave_id), CaveInfo.parse(cave_json_data)


class Perception:
    current_cave = None
    front_cave = None
    behind_cave = None
    left_cave = None
    right_cave = None
    front_left_cave = None
    front_right_cave = None
    behind_left_cave = None
    behind_right_cave = None

    def get_top_cave(self, pivot_direction):
        return {
            'Up': self.front_cave,
            'Right': self.left_cave,
            'Down': self.behind_cave,
            'Left': self.right_cave
        }[pivot_direction]

    def get_top_right_cave(self, pivot_direction):
        return {
            'Up': self.front_right_cave,
            'Right': self.front_left_cave,
            'Down': self.behind_left_cave,
            'Left': self.behind_right_cave
        }[pivot_direction]

    def get_right_cave(self, pivot_direction):
        return {
            'Up': self.right_cave,
            'Right': self.front_cave,
            'Down': self.left_cave,
            'Left': self.behind_cave
        }[pivot_direction]

    def get_bottom_right_cave(self, pivot_direction):
        return {
            'Up': self.behind_right_cave,
            'Right': self.front_right_cave,
            'Down': self.front_left_cave,
            'Left': self.behind_left_cave
        }[pivot_direction]

    def get_bottom_cave(self, pivot_direction):
        return {
            'Up': self.behind_cave,
            'Right': self.right_cave,
            'Down': self.front_cave,
            'Left': self.left_cave
        }[pivot_direction]

    def get_bottom_left_cave(self, pivot_direction):
        return {
            'Up': self.behind_left_cave,
            'Right': self.behind_right_cave,
            'Down': self.front_right_cave,
            'Left': self.front_left_cave
        }[pivot_direction]

    def get_left_cave(self, pivot_direction):
        return {
            'Up': self.left_cave,
            'Right': self.behind_cave,
            'Down': self.right_cave,
            'Left': self.front_cave
        }[pivot_direction]

    def get_top_left_cave(self, pivot_direction):
        return {
            'Up': self.front_left_cave,
            'Right': self.behind_left_cave,
            'Down': self.behind_right_cave,
            'Left': self.front_right_cave
        }[pivot_direction]

    @staticmethod
    def parse(json_data):
        result = Perception()
        result.current_cave = CaveInfo.parse(json_data['current_cave'])
        result.front_cave = CaveInfo.parse(json_data['front_cave'])
        result.behind_cave = CaveInfo.parse(json_data['behind_cave'])
        result.left_cave = CaveInfo.parse(json_data['left_cave'])
        result.right_cave = CaveInfo.parse(json_data['right_cave'])
        result.front_left_cave = CaveInfo.parse(json_data['front_left_cave'])
        result.front_right_cave = CaveInfo.parse(json_data['front_right_cave'])
        result.behind_left_cave = CaveInfo.parse(json_data['behind_left_cave'])
        result.behind_right_cave = CaveInfo.parse(json_data['behind_right_cave'])

        return result


class WorldInfo:
    user_id = None
    new_cave_opened_count = None
    is_gold_found = None
    is_monster_alive = None
    tik_tak = None
    agent_info = None
    current_cave = None
    perception = None

    @staticmethod
    def parse(json_data):
        result = WorldInfo()
        result.user_id = json_data['userid']

        world_info_json_data = json_data['worldinfo']
        result.new_cave_opened_count = world_info_json_data['newcaveopened']
        result.is_gold_found = world_info_json_data['isgoldfinded'] == 1
        result.is_monster_alive = world_info_json_data['ismonsteralive'] == 1
        result.tik_tak = world_info_json_data['tiktak']

        result.agent_info = AgentInfo.parse(json_data['iagent'])
        result.current_cave = CaveInfo.parse(json_data['currentcave'])
        result.perception = Perception.parse(json_data['perception'])

        return result
