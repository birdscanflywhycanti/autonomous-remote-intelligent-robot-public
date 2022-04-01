"""Contains functionality for driving the robot"""

import math

from robot.accelerometer import perform_drive
from robot.gyroscope import PerformSpin


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

    diagonal_unit_distance = math.sqrt(
        unit_size**2 + unit_size**2
    )  # Pythagorean theorem

    x, y = (0, 0)

    for coord in path:
        print(coord)
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
        instructions.append(
            (PerformSpin, delta_angle)
        )  # rotate the car to match the target angle by rotating the remaining distance
        curr_angle = (
            curr_angle + delta_angle
        )  # update current angle to match the the robot's angle

        instructions.append((perform_drive, diagonal_unit_distance))

        print(get_move_string(vertical, horizontal))
        print("delta angle:" + str(delta_angle) + " global angle:" + str(target_angle))

        x, y = x_, y_
    return instructions


def follow(instructions):
    """Follows a list of instructions

    Args:
        instructions (list): a list of instructions to be performed by the robot
    """

    for action, arg in instructions:
        action(arg)
