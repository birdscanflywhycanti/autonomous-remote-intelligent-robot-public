from algorithms.algorithm import Algorithm
#from hcsr04 import HCSR04
from mpu6050 import MPU6050

from robot.accelerometer import PerformDrive
from robot.drive import follow, pathing
from robot.gyroscope import PerformSpin

import ThunderBorg3 as ThunderBorg  # conversion for python 3
import sys

# initialise mpu6050 board
mpu = MPU6050()
mpu.setName("MPU6050")
mpu.start()

#hcsr = HCSR04(trigger_pin=16, echo_pin=0, echo_timeout_us=1000000)
#hcsr.setName("HCSR04")
#hcsr.start()

# Setup the ThunderBorg
TB = ThunderBorg.ThunderBorg()

i2cAddress = TB.i2cAddress

# i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
TB.Init()

if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print("No ThunderBorg found, check you are attached :)")
    else:
        print(
            "No ThunderBorg at address %02X, but we did find boards:"
            % (i2cAddress)
        )
        for board in boards:
            print("%02X (%d)" % (board, board))
        print(
            "If you need to change the I2C address change the setup line so it is correct, e.g."
        )
        print("TB.i2cAddress = 0x%02X" % (boards[0]))
    sys.exit()

TB.SetCommsFailsafe(False)  # Disable the communications failsafe

# Power settings
voltageIn = 9.6  # Total battery voltage to the ThunderBorg

# NOTE: limiter has lower bound to power motors, ~0.4 experimental lower bound
limiter = 0.6  # utilise only <limiter>% of power, to slow down actions

voltageOut = (
    12.0 * limiter
)  # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

def main():
    input_matrix = [
        [1, 0, 1, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ]
    start_node = (0, 0)
    end_node = (3, 0)

    algorithm = Algorithm(matrix=input_matrix, start_node=start_node, end_node=end_node)
    path = algorithm.use_a_star()

    instructions = pathing(path, 0.4)
    print(instructions)

    follow(instructions)


if __name__ == "__main__":
    main()
