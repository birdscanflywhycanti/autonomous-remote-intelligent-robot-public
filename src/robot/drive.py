"""Contains functionality for driving the robot"""

import math

from robot.accelerometer import perform_drive
from robot.gyroscope import perform_spin

import time
import logging


def calculate_angle(unit_target_vector):
    """Calculates the angle between a given vector and a known unit vector [facing up]

    Arguments:
        unit_target_vector {tuple} -- a vector with a known unit vector [facing up]

    Returns:
        float -- the angle needed to rotate from the known vector to match the given vector
    """

    origin_vector_x, origin_vector_y = (0, 1)
    target_vector_x, target_vector_y = unit_target_vector

    # arc-cosine method does not produce signed output:

    # magnitude_origin = math.sqrt(origin_vector_x**2 + origin_vector_y**2)
    # magnitude_target = math.sqrt(target_vector_x**2 + target_vector_y**2)
    #
    # x_product = origin_vector_x * target_vector_x
    # y_product = origin_vector_y * target_vector_y
    #
    # product_sum = x_product + y_product
    # magnitude_product = magnitude_origin * magnitude_target
    #
    # rad = math.acos( product_sum / magnitude_product  )

    rad = math.atan2(origin_vector_y, origin_vector_x) - math.atan2(
        target_vector_y, target_vector_x
    )

    angle = math.degrees(rad)

    # print(r)
    return angle


def get_move_string(y, x):
    """Converts a move to a string

    Args:
        y (int): the y-coordinate of the move
        x (int): the x-coordinate of the move

    Returns:
        str: the string representation of the move
    """

    vertical = {
        1: "up",
        -1: "down",
    }
    horizontal = {
        1: "right",
        -1: "left",
    }
    out = "move "
    fragment1 = vertical.get(y, "")
    fragment2 = horizontal.get(x, "")
    out = out + fragment1
    out = out + " "
    out = out + fragment2
    return out


def pathing(path, unit_size, origin=False, curr_angle=0):
    """Drives the robot to the given path

    Args:
        path (list): a list of tuples representing the path
        unit_size (int): the size of the unit the robot is moving in
        origin (bool, optional): whether or not the robot is starting at the origin,\
            defaults to False
        curr_angle (int, optional): the angle the robot is starting at, defaults to 0

    Returns:
        list: a list of instructions to be performed by the robot
    """
    if not origin:
        origin = path.pop(0)

    instructions = []

    x, y = (0, 0)

    for coord in path:
        logging.debug(coord)
        x_, y_ = coord

        # calculate the unit deviation from the previous point
        vertical = y - y_
        horizontal = x - x_

        # move_up = (vertical == 1)
        # move_down = (vertical == -1)
        # move_right = (horizontal == 1)
        # move_left = (horizontal == -1)

        # Use a unit vector to transform the next step to be relative \
        # to the previous point rather than to the origin
        unit_target_vector = (x_ - x, y - y_)

        target_angle = calculate_angle(unit_target_vector)

        delta_angle = (
            target_angle - curr_angle
        )  # calculate the difference in between the current and the target angle

        if abs(delta_angle) > 0:
            instructions.append(
                (perform_spin, (delta_angle, target_angle))
            )  # rotate the car to match the target angle by rotating the remaining distance

        curr_angle = (
            curr_angle + delta_angle
        )  # update current angle to match the the robot's angle

        drive_distance = math.sqrt(
            (vertical*unit_size)**2 + (horizontal*unit_size)**2
        )  # Pythagorean theorem
        instructions.append((perform_drive, (drive_distance,))) # NOTE: wrap drive_distance in tuple to be compatible when unpacking as with perform_spin (the trailing comma is important!)

        logging.debug(get_move_string(vertical, horizontal))
        logging.debug("delta angle:" + str(delta_angle) + " global angle:" + str(target_angle))

        x, y = x_, y_

    
    # reorient to face north
    delta_angle = (
        0 - curr_angle
    )  # calculate the difference in between the current and the target angle

    instructions.append(
        (perform_spin, (delta_angle, 0))
    )  # rotate the car to match the target angle by rotating the remaining distance
    

    return instructions


def follow(instructions, TB, mpu, max_power):
    """Follows a list of instructions

    Args:
        instructions (list): a list of instructions to be performed by the robot
    """

    for action, arg in instructions:
        action(*arg, TB, mpu, max_power)
        time.sleep(0.5)


if __name__ == "__main__":
    # enable debug logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

    from pathfinding.core.diagonal_movement import DiagonalMovement
    from pathfinding.core.grid import Grid
    from pathfinding.finder.a_star import AStarFinder

    input_matrix = [
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ]
    start_node = (0, 0)
    end_node = (3, 0)
    
    # define dummy functions
    def perform_spin(delta, target, TB, mpu, max_power):
        print(f"spin: {delta} deg")
    
    def perform_drive(meters, TB, mpu, max_power):
        print(f"drive: {meters} m")

    def a_star(matrix, start_node, end_node):
        """A function that returns a path using the A* algorithm

        Args:
            matrix (list): a matrix representing the space the robot is in
            start_node (tuple): the node the robot is starting from
            end_node (tuple): the node the robot is trying to reach

        Returns:
            path (list) : a list of nodes representing the path the robot should take
        """
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
    

    path = a_star(input_matrix, start_node, end_node)

    instructions = pathing(path, 1)

    follow(instructions, None, None, 0)