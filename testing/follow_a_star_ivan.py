import time
import math
import sys
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


def a_star(matrix, start_node, end_node):
    grid = Grid(matrix=matrix)

    start = grid.node(*start_node)
    end = grid.node(*end_node)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    # pathing instruction
    print(path)

    # visualisation
    print("operations:", runs, "path length:", len(path))
    print(grid.grid_str(path=path, start=start, end=end))

    return path


def calculate_angle(unit_target_vector):
    # print("(" + str(x) + "," + str(y) + ")" + "(" + str(x_) + "," + str(y_) + ")")

    origin_vector_x, origin_vector_y = (0, 1)
    target_vector_x, target_vector_y = unit_target_vector
    # magnitude_origin = math.sqrt(origin_vector_x**2 + origin_vector_y**2)
    # magnitude_target = math.sqrt(target_vector_x**2 + target_vector_y**2)
    # r = math.acos( (origin_vector_x * target_vector_x + origin_vector_y * target_vector_y) / (magnitude_origin * magnitude_target)  )

    ######
    # arc-cosine method does not produce signed output
    ######
    r = math.atan2(origin_vector_y, origin_vector_x) - math.atan2(
        target_vector_y, target_vector_x
    )

    r = math.degrees(r)

    # print(r)
    return r


def get_move_string(y, x):
    vertical = {
        1: "up",
        -1: "down",
    }
    horizontal = {
        1: "right",
        -1: "left",
    }
    str = "move "
    fragment1 = vertical.get(y, "")
    fragment2 = horizontal.get(x, "")
    str = str + fragment1
    str = str + " "
    str = str + fragment2
    return str


def pathing(path, origin=False, curr_angle=0):
    if not origin:
        origin = path.pop(0)

    instructions = []
    x, y = (0, 0)

    global_angle = 0
    for coord in path:
        print(coord)
        x_, y_ = coord

        vertical = y - y_
        horizontal = x - x_

        # move_up = (y-y_ == 1)
        # move_down = (y-y_ == -1)
        # move_right = (x-x_ == 1)
        # move_left = (x-x_ == -1)

        unit_target_vector = (x_ - x, y - y_)

        target_angle = calculate_angle(unit_target_vector)
        delta_angle = target_angle - curr_angle

        curr_angle = curr_angle + delta_angle

        print(get_move_string(vertical, horizontal))
        print("delta angle:" + str(delta_angle) + " global angle:" + str(target_angle))

        instructions.append((PerformSpin, delta_angle))
        instructions.append((PerformDrive, diagonal_unit_distance))

        x, y = x_, y_


matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]

path = a_star(matrix, (0, 0), (3, 0))
pathing(path)
