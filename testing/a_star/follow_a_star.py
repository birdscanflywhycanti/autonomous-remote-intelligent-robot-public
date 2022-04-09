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


def a_star(matrix):
    grid = Grid(matrix=matrix)

    start = grid.node(0, 0)
    end = grid.node(2, 2)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    # pathing instruction
    print(path)

    # visualisation
    print("operations:", runs, "path length:", len(path))
    print(grid.grid_str(path=path, start=start, end=end))

    return path


def pathing(path, origin=False, curr_angle=0):
    if not origin: 
        origin = path.pop(0)
    
    instructions = []

    unit_size = 0.4 #m
    diagonal_unit_distance = math.sqrt(unit_size**2 + unit_size**2) # Pythagorean theorem

    x, y = origin
    for coord in path:
        print(coord)
        x_, y_ = coord

        if x_ == x-1 and y_ == y-1:
            # move to relative top left
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            # spin further -45 degrees to face destination
            curr_angle = 315
            instructions.append((PerformSpin, curr_angle))
            # move forward from middle of current unit to middle of target unit
            instructions.append((PerformDrive, diagonal_unit_distance))

        elif x_ == x and y_ == y-1:
            # move to relative top
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            instructions.append((PerformDrive, unit_size))

        elif x_ == x+1 and y_ == y-1:
            # move to relative top right
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            # spin further 45 degrees to face destination
            curr_angle = 45
            instructions.append((PerformSpin, curr_angle))
            # move forward from middle of current unit to middle of target unit
            instructions.append((PerformDrive, diagonal_unit_distance))

        elif x_ == x-1 and y_ == y:
            # move to relative left
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            # spin further 270 degrees to face destination
            curr_angle = 270
            instructions.append((PerformSpin, curr_angle))
            # move forward from middle of current unit to middle of target unit
            instructions.append((PerformDrive, unit_size))

        elif x_ == x and y_ == y:
            print("Warning: instructions call for movement to same square twice in a row (is there an instruction error?)")

        elif x_ == x+1 and y_ == y:
            # move to relative right
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            # spin further 90 degrees to face destination
            curr_angle = 90
            instructions.append((PerformSpin, curr_angle))
            # move forward from middle of current unit to middle of target unit
            instructions.append((PerformDrive, unit_size))

        elif x_ == x-1 and y_ == y+1:
            # move to relative bottom left
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            # spin further 225 degrees to face destination
            curr_angle = 225
            instructions.append((PerformSpin, curr_angle))
            # move forward from middle of current unit to middle of target unit
            instructions.append((PerformDrive, diagonal_unit_distance))

        elif x_ == x and y_ == y+1:
            # move to relative bottom
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            # spin further 180 degrees to face destination
            curr_angle = 180
            instructions.append((PerformSpin, curr_angle))
            # move forward from middle of current unit to middle of target unit
            instructions.append((PerformDrive, unit_size))

        elif x_ == x+1 and y_ == y+1:
            # move to relative bottom right
            # orient to face north (spin degree of current angle from North)
            instructions.append((PerformSpin, -curr_angle))
            # spin further 135 degrees to face destination
            curr_angle = 135
            instructions.append((PerformSpin, curr_angle))
            # move forward from middle of current unit to middle of target unit
            instructions.append((PerformDrive, diagonal_unit_distance))

        x, y = x_, y_

    return instructions

def follow(instructions):
    for action, arg in instructions:
        action(arg)

if __name__ == "__main__":
    matrix = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]

    path = a_star(matrix)

    instructions = pathing(path)

    print(instructions)

    follow(instructions)