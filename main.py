import ThunderBorg3 as ThunderBorg # conversion for python 3
import time
import math
import sys
import board
import adafruit_mpu6050

from algorithms.a_star import a_star
from algorithms.d_star_lite import d_star_lite

from sensors.accelerometer import PerformDrive
from sensors.gyroscope import PerformSpin
from sensors.drive import pathing, follow

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


def main():
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
        maxPower = 1.0
    else:
        maxPower = voltageOut / float(voltageIn)

    # initialise gyroscope board
    i2c = board.I2C()  # uses board.SCL and board.SDA
    mpu = adafruit_mpu6050.MPU6050(i2c)

    # test following example matrix
    #matrix = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    path = a_star(matrix)

    instructions = pathing(path, 0.4)

    print(instructions)

    follow(instructions)

if __name__ == "__main__":
    main()