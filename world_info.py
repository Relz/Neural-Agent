class Position:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def create_from_string(string):
        position_array = string.split('_')
        return Position(position_array[1], position_array[0])


class CaveInfo:
    is_wall = False
    id = ''
    x = 0
    y = 0
    has_gold = False
    has_monster = False
    has_hole = False
    has_wind = False
    has_bones = False
    is_visible = False
    direction_list = {}  # Why dictionary?
    is_safe = False

    @staticmethod
    def parse(json_data):
        cave_info = CaveInfo()
        if 'isWall' in json_data:
            cave_info.is_wall = json_data['isWall'] == 1
        else:
            cave_info.id = json_data['cNum']
            cave_info.x = json_data['colN']
            cave_info.y = json_data['rowN']
            cave_info.has_gold = json_data['isGold'] == 1
            cave_info.has_monster = json_data['isMonster'] == 1
            cave_info.has_hole = json_data['isHole'] == 1
            cave_info.has_wind = json_data['isWind']
            cave_info.has_bones = json_data['isBones']
            cave_info.is_visible = json_data['isVisiable'] == 1
            if 'dirList' in json_data:
                cave_info.direction_list = json_data['dirList']
            if 'isSafety' in json_data:
                cave_info.is_safe = json_data['isSafety']

        return cave_info


class AgentInfo:
    a_name = ''  # What is it? Seems to be the agent's name, but how to specify that name?
    is_alive = False
    leg_count = 0
    arrow_count = 0
    has_gold = False
    direction = ''
    cave_position = Position(0, 0)
    visited_caves_info = {}
    score = 0
    direction_list = {}
    actions_cost_list = {}  # Why I need it?
    acts = None  # What is it? Why I need it?
    passive_moves = []  # Why I need it?
    active_moves = []  # Why I need it?
    w_state_utilities = {}  # Why I need it?
    i_a_state_utilities = {}  # What is it? Why I need it?
    world_info = None  # What is it? Why I need it?
    all_dirs = {}  # Why I need it? Why dictionary?
    chosen_action = ''  # Why I need it?
    timestamp = 0  # Why I need it?
    ga_id = 0  # What is it? Why I need it?
    id = 0  # What is it? Why I need it?

    @staticmethod
    def parse(json_data):
        result = AgentInfo()
        result.a_name = json_data['aname']
        result.is_alive = int(json_data['isagentalive']) == 1
        result.leg_count = int(json_data['legscount'])
        result.arrow_count = int(json_data['arrowcount'])
        result.has_gold = int(json_data['havegold']) == 1
        result.direction = json_data['dir']
        result.cave_position = Position.create_from_string(json_data['cavenum'])
        result.visited_caves_info = dict(map(AgentInfo.__parse_visited_cave_pair__, json_data['knowCaves'].items()))
        result.score = json_data['score']
        result.direction_list = json_data['dirList']

        result.actions_cost_list = json_data['actsCostList']
        result.acts = json_data['acts']
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
        return cave_id, CaveInfo.parse(cave_json_data)


class Perception:
    current_cave = CaveInfo()
    front_cave = CaveInfo()
    behind_cave = CaveInfo()
    left_cave = CaveInfo()
    right_cave = CaveInfo()
    front_left_cave = CaveInfo()
    front_right_cave = CaveInfo()
    behind_left_cave = CaveInfo()
    behind_right_cave = CaveInfo()

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
    user_id = 0  # Why I need it?
    new_cave_opened_count = 0
    is_gold_found = False
    is_monster_alive = False
    tik_tak = None  # What is it? Why I need it?
    agent_info = AgentInfo()
    current_cave = CaveInfo()
    perception = Perception()  # Why I need it?

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
