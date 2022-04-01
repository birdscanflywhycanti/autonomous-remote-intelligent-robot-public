"""
Test navigation assuming set environment.
- Calculate ideal path in A*
- Create movement path for thunderborg
- Follow movement to end
"""

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

import ThunderBorg3 as ThunderBorg # conversion for python 3
import time
import math
import sys

import board
import adafruit_mpu6050

# Movement settings (worked out from our MonsterBorg on carpet tiles)
timeForward1m = 0.85                    # Number of seconds needed to move about 1 meter
testMode = False                        # True to run the motion tests, False to run the normal sequence

# Setup the ThunderBorg
TB = ThunderBorg.ThunderBorg()
# TB.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
TB.Init()
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print("No ThunderBorg found, check you are attached :)")
    else:
        print(
            "No ThunderBorg at address %02X, but we did find boards:" % (TB.i2cAddress)
        )
        for board in boards:
            print("    %02X (%d)" % (board, board))
        print(
            "If you need to change the I2C address change the setup line so it is correct, e.g."
        )
        print("TB.i2cAddress = 0x%02X" % (boards[0]))
    sys.exit()
TB.SetCommsFailsafe(False)  # Disable the communications failsafe

# Power settings
voltageIn = 9.6   # Total battery voltage to the ThunderBorg

# NOTE: limiter has lower bound to power motors, ~0.4 experimental lower bound
limiter = 0.6     # utilise only <limiter>% of power, to slow down actions

voltageOut = (
    12.0 * limiter
)  # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    max_power = 1.0
else:
    max_power = voltageOut / float(voltageIn)

# initialise gyroscope board
i2c = board.I2C()  # uses board.SCL and board.SDA
mpu = adafruit_mpu6050.MPU6050(i2c)

# Function to perform a general movement
def PerformMove(driveLeft, driveRight, numSeconds):
    # Set the motors running
    TB.SetMotor1(driveRight * max_power)
    TB.SetMotor2(driveLeft * max_power)
    # Wait for the time
    time.sleep(numSeconds)
    # Turn the motors off
    TB.MotorsOff()


# Function to spin an angle in degrees
def PerformSpin(degrees):
    if degrees < 0.0:
        # Left turn
        driveLeft = -1.0
        driveRight = +1.0
        degrees *= -1
    else:
        # Right turn
        driveLeft = +1.0
        driveRight = -1.0

    # Set the motors running
    TB.SetMotor1(driveRight * max_power)
    TB.SetMotor2(driveLeft * max_power)
    
    # poll the gyroscope for rotation
    # NOTE: sampling limited by real-time clock on system (0.1ms theoretical minimum, but experimentally encountered errors)
    sampling = 0.08 # poll every <sampling> seconds, fine tune to minimise overshooting target rotation
    total_rotation = 0

    while True:
        x, y, z = mpu.gyro
        x, y, z = math.degrees(x), math.degrees(y), math.degrees(z)
        abs_z = abs(z)
        sample = abs_z * sampling

        #print("Gyro X:%.2f, Y: %.2f, Z: %.2f rad/s" % (x, y, z))        
        print("X:%.2f, Y: %.2f, Z: %.2f deg/s \t sample:%.2f \t total:%.2f" % (x, y, z, sample, total_rotation))
        #print(total_rotation)

        # NOTE: z-axis experimentally defined as 2d plane orientation
        total_rotation += sample # increment degree rotation by current rotation velocity, devided by sampling time

        # if exceeded target exit
        if total_rotation >= degrees:
            break   # exit once achieved target rotation
        # if predicted to exceed during sleep, sleep for predicted time to target, then exit
        elif (total_rotation + sample) >= degrees:
            # total degrees left in rotation (degress-total_rotation) divided by abs(z) (positive rotational velocity) gives time to sleep (in seconds) before reaching target
            sleep = (degrees-total_rotation)/abs_z

            print("Assuming constant rotation of Z:%.2f, sleeping for %.2f seconds to rotate %.2f degrees" % (abs_z, sleep, (degrees-total_rotation)))
            time.sleep(sleep)

            # NOTE: this will set total rotation to target, which is only correct assuming rotation halts immediately and rotational velocity remains constant
            # in non-demo system current orientation should be independently tracked, not adjusted using this approximation
            total_rotation += abs_z * sleep  # update final rotation for tracking
            break

        time.sleep(sampling)

    # Turn the motors off
    TB.MotorsOff()

    print(f"total rotation: {total_rotation}")


# Function to drive a distance in meters
def PerformDrive(meters):
    if meters < 0.0:
        # Reverse drive
        driveLeft = -1.0
        driveRight = -1.0
        meters *= -1
    else:
        # Forward drive
        driveLeft = +1.0
        driveRight = +1.0
    # Calculate the required time delay
    numSeconds = meters * timeForward1m
    # Perform the motion
    PerformMove(driveLeft, driveRight, numSeconds)


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

    # arc-cosine method does not produce signed output
    #####
    """
    magnitude_origin = math.sqrt(origin_vector_x**2 + origin_vector_y**2)
    magnitude_target = math.sqrt(target_vector_x**2 + target_vector_y**2)

    x_product = origin_vector_x * target_vector_x
    y_product = origin_vector_y * target_vector_y
    
    product_sum = x_product + y_product
    magnitude_product = magnitude_origin * magnitude_target

    rad = math.acos( product_sum / magnitude_product  )
    """
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
    out = "move "
    fragment1 = vertical.get(y, "")
    fragment2 = horizontal.get(x, "")
    out = out + fragment1
    out = out + " "
    out = out + fragment2
    return out


def pathing(path, unit_size, origin=False, curr_angle=0):
    if not origin:
        origin = path.pop(0)

    instructions = []
    
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

        # Use a unit vector to transform the next step to be relative to the previous point rather than to the origin
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

        drive_distance = math.sqrt(
            (vertical*unit_size)**2 + (horizontal*unit_size)**2
        )  # Pythagorean theorem
        instructions.append((PerformDrive, drive_distance))

        print(get_move_string(vertical, horizontal))
        print("delta angle:" + str(delta_angle) + " global angle:" + str(target_angle))

        x, y = x_, y_
    return instructions


def follow(instructions):
    for action, arg in instructions:
        action(arg)



if __name__ == "__main__":
    #matrix = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    path = a_star(matrix, (0,0), (3,0))

    instructions = pathing(path, 0.4)

    print(instructions)

    follow(instructions)



