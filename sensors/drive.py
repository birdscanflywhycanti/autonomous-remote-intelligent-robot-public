import ThunderBorg3 as ThunderBorg # conversion for python 3
import time
import math
import sys

from sensors import PerformDrive, PerformSpin

# Calculates the angle between a given vector and a known unit vector [up]
# Returns a the angle needed to rotate from the known vector to match the given vector
def calculate_angle(unit_target_vector):
    # print("(" + str(x) + "," + str(y) + ")" + "(" + str(x_) + "," + str(y_) + ")")

    origin_vector_x, origin_vector_y = (0, 1)
    target_vector_x, target_vector_y = unit_target_vector
    
    # arc-cosine method does not produce signed output
    #####
    '''
    magnitude_origin = math.sqrt(origin_vector_x**2 + origin_vector_y**2)
    magnitude_target = math.sqrt(target_vector_x**2 + target_vector_y**2)

    x_product = origin_vector_x * target_vector_x
    y_product = origin_vector_y * target_vector_y
    
    product_sum = x_product + y_product
    magnitude_product = magnitude_origin * magnitude_target

    rad = math.acos( product_sum / magnitude_product  )
    '''
    ######


    rad = math.atan2(origin_vector_y, origin_vector_x) - math.atan2(
        target_vector_y, target_vector_x
    )

    angle = math.degrees(rad)

    # print(r)
    return angle


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


def pathing(path, unit_size, origin=False, curr_angle=0):
    if not origin:
        origin = path.pop(0)

    instructions = []

    diagonal_unit_distance = math.sqrt(unit_size**2 + unit_size**2) # Pythagorean theorem

    x, y = (0, 0)

    global_angle = 0
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

        # Use a unit vector to transform the next step to be relative to the previous point rather than to the origin
        unit_target_vector = (x_ - x, y - y_)

        target_angle = calculate_angle(unit_target_vector)

        
        delta_angle = target_angle - curr_angle # calculate the difference in between the current and the target angle 
        instructions.append((PerformSpin, delta_angle)) # rotate the car to match the target angle by rotating the remaining distance
        curr_angle = curr_angle + delta_angle # update current angle to match the the robot's angle


        instructions.append((PerformDrive, diagonal_unit_distance))


        print(get_move_string(vertical, horizontal))
        print("delta angle:" + str(delta_angle) + " global angle:" + str(target_angle))

        x, y = x_, y_
    return instructions
        
def follow(instructions):
    for action, arg in instructions:
        action(arg)