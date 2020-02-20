import math

from world_info import WorldInfo


class WorldInfoVisualizer:
    CAVE_SIZE = 5 * 2

    @staticmethod
    def draw_in_console(text):
        world_info = WorldInfo.parse(text)
        green_background = '\033[0;37;42m'
        yellow_background = '\033[0;37;43m'
        orange_background = '\033[0;37;44m'
        red_background = '\033[0;37;41m'
        green_color = '\033[32m'
        yellow_color = '\033[33m'
        red_color = '\033[91m'
        end_color = '\033[0m'
        caves = world_info.agent_info.visited_caves_info.values()
        agent_position = world_info.agent_info.position
        is_agent_alive = world_info.agent_info.is_alive
        agent_direction = world_info.agent_info.direction
        agent_arrow_count = world_info.agent_info.arrow_count
        agent_leg_count = world_info.agent_info.leg_count

        column_count = max(list(map(lambda cave: cave.position.x, caves))) + 1
        WorldInfoVisualizer.__draw_columns_indexes__(column_count)
        caves_by_row = WorldInfoVisualizer.__get_caves_by_row__(caves)

        for line_caves in caves_by_row:
            WorldInfoVisualizer.__draw_row_horizontal_border__(column_count)
            lines_count = WorldInfoVisualizer.CAVE_SIZE - 1
            for y in range(0, math.ceil(lines_count / 2)):
                print('  ', end='')
                previous_x = 0
                for cave in line_caves:
                    while previous_x < cave.position.x:
                        print('│', end='')
                        for x in range(0, WorldInfoVisualizer.CAVE_SIZE):
                            print(' ', end='')
                        previous_x += 1
                    print('│', end='')
                    for x in range(0, WorldInfoVisualizer.CAVE_SIZE):
                        if y == 0 or x == 0 or x == WorldInfoVisualizer.CAVE_SIZE - 1:
                            print(f'{green_background} {end_color}', end='')
                        elif cave.has_bones and cave.has_wind and (y == 1 or x == 1 or x == WorldInfoVisualizer.CAVE_SIZE - 2):
                            print(f'{orange_background} {end_color}', end='')
                        elif cave.has_wind and (y == 1 or x == 1 or x == WorldInfoVisualizer.CAVE_SIZE - 2):
                            print(f'{yellow_background} {end_color}', end='')
                        elif cave.has_bones and (y == 1 or x == 1 or x == WorldInfoVisualizer.CAVE_SIZE - 2):
                            print(f'{red_background} {end_color}', end='')
                        else:
                            print(' ', end='')
                    previous_x += 1
                print('│')

            print(f'{line_caves[0].position.y} ', end='')
            previous_x = 0
            for cave in line_caves:
                while previous_x < cave.position.x:
                    print('│', end='')
                    for x in range(0, WorldInfoVisualizer.CAVE_SIZE):
                        print(' ', end='')
                    previous_x += 1
                print('│', end='')
                space_count = WorldInfoVisualizer.CAVE_SIZE - 1
                for x in range(0, math.ceil(space_count / 2)):
                    if x == 0:
                        print(f'{green_background} {end_color}', end='')
                    elif cave.has_bones and cave.has_wind and x == 1:
                        print(f'{orange_background} {end_color}', end='')
                    elif cave.has_wind and x == 1:
                        print(f'{yellow_background} {end_color}', end='')
                    elif cave.has_bones and x == 1:
                        print(f'{red_background} {end_color}', end='')
                    else:
                        print(' ', end='')
                if cave.position.x == agent_position.x and cave.position.y == agent_position.y:
                    agent_character = WorldInfoVisualizer.__get_agent_character__(
                        is_agent_alive,
                        agent_direction,
                        agent_arrow_count,
                        agent_leg_count
                    )
                    if world_info.current_cave.has_gold:
                        print(f'{green_color}{agent_character}{end_color}', end='')
                    else:
                        print(agent_character, end='')
                elif cave.has_gold:
                    if cave.has_monster:
                        print('\b' + f'{red_color}💰{end_color} ', end='')
                    elif cave.has_hole:
                        print('\b' + f'{yellow_color}💰{end_color} ', end='')
                    else:
                        print('\b💰 ', end='')
                elif cave.has_monster:
                    print(f'{red_background} {end_color}', end='')
                elif cave.has_hole:
                    print(f'{yellow_background} {end_color}', end='')
                else:
                    print(' ', end='')
                for x in range(0, int(space_count / 2)):
                    if x == int(space_count / 2) - 1:
                        print(f'{green_background} {end_color}', end='')
                    elif cave.has_wind and cave.has_bones and x == int(space_count / 2) - 2:
                        print(f'{orange_background} {end_color}', end='')
                    elif cave.has_wind and x == int(space_count / 2) - 2:
                        print(f'{yellow_background} {end_color}', end='')
                    elif cave.has_bones and x == int(space_count / 2) - 2:
                        print(f'{red_background} {end_color}', end='')
                    else:
                        print(' ', end='')
                previous_x += 1
            print('│')

            for y in range(0, int(lines_count / 2)):
                print('  ', end='')
                previous_x = 0
                for cave in line_caves:
                    while previous_x < cave.position.x:
                        print('│', end='')
                        for x in range(0, WorldInfoVisualizer.CAVE_SIZE):
                            print(' ', end='')
                        previous_x += 1
                    print('│', end='')
                    for x in range(0, WorldInfoVisualizer.CAVE_SIZE):
                        if y == int(lines_count / 2) - 1 or x == 0 or x == WorldInfoVisualizer.CAVE_SIZE - 1:
                            print(f'{green_background} {end_color}', end='')
                        elif cave.has_bones and cave.has_wind and (y == int(lines_count / 2) - 2 or x == 1 or x == WorldInfoVisualizer.CAVE_SIZE - 2):
                            print(f'{orange_background} {end_color}', end='')
                        elif cave.has_wind and (y == int(lines_count / 2) - 2 or x == 1 or x == WorldInfoVisualizer.CAVE_SIZE - 2):
                            print(f'{yellow_background} {end_color}', end='')
                        elif cave.has_bones and (y == int(lines_count / 2) - 2 or x == 1 or x == WorldInfoVisualizer.CAVE_SIZE - 2):
                            print(f'{red_background} {end_color}', end='')
                        else:
                            print(' ', end='')
                    previous_x += 1
                print('│')
        WorldInfoVisualizer.__draw_row_horizontal_border__(column_count)

    @staticmethod
    def __get_caves_by_row__(caves):
        result = []
        max_y = max(list(map(lambda cave: cave.position.y, caves)))
        for y in range(0, max_y + 1):
            y_caves = list(filter(lambda cave: cave.position.y == y, caves))
            y_caves.sort(key=lambda cave: cave.position.x)
            result.append(y_caves)
        return result

    @staticmethod
    def __draw_columns_indexes__(column_count):
        print('  ', end='')
        for x in range(0, column_count):
            print(' ', end='')
            for cell_x in range(0, WorldInfoVisualizer.CAVE_SIZE):
                if cell_x != 0 and cell_x % math.ceil(WorldInfoVisualizer.CAVE_SIZE / 2) == 0:
                    print(x, end='')
                else:
                    print(' ', end='')
        print()

    @staticmethod
    def __draw_row_horizontal_border__(column_count):
        print('  ', end='')
        for x in range(0, column_count * (WorldInfoVisualizer.CAVE_SIZE + 1) + 1):
            print('―', end='')
        print()

    @staticmethod
    def __get_agent_character__(is_alive, direction, arrow_count, leg_count):
        red_color = '\033[91m'
        end_color = '\033[0m'
        if not is_alive:
            return f'{red_color}X{end_color}'
        if direction == 'Up':
            if arrow_count == 0:
                if leg_count == 1:
                    return f'{red_color}↑{end_color}'
                else:
                    return '↑'
            else:
                if leg_count == 1:
                    return f'{red_color}⇈{end_color}'
                else:
                    return '⇈'
        elif direction == 'Right':
            if arrow_count == 0:
                if leg_count == 1:
                    return f'{red_color}→{end_color}'
                else:
                    return '→'
            else:
                if leg_count == 1:
                    return f'\b{red_color}⇉{end_color} '
                else:
                    return '\b⇉ '
        elif direction == 'Down':
            if arrow_count == 0:
                if leg_count == 1:
                    return f'{red_color}↓{end_color}'
                else:
                    return '↓'
            else:
                if leg_count == 1:
                    return f'{red_color}⇊{end_color}'
                else:
                    return '⇊'
        elif direction == 'Left':
            if arrow_count == 0:
                if leg_count == 1:
                    return f'\b{red_color}←{end_color} '
                else:
                    return '\b← '
            else:
                if leg_count == 1:
                    return f'\b{red_color}⇇{end_color} '
                else:
                    return '\b⇇ '
