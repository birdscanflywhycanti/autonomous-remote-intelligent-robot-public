"""Top level main file for running the application"""

# imports
import sys

import ThunderBorg3 as ThunderBorg  # conversion for python 3
from algorithms.algorithm import Algorithm
#from hcsr04 import HCSR04
from mpu6050 import MPU6050
from robot.drive import follow, pathing

import logging

# from robot.accelerometer import perform_drive
# from robot.gyroscope import perform_spin

# Setup the ThunderBorg
TB = ThunderBorg.ThunderBorg()

i2cAddress = TB.i2cAddress

# i2cAddress = ( 0x15  # Uncomment and change the value if you have changed the board address)
TB.Init()

if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        logging.warning("No ThunderBorg found, check you are attached :)")
    else:
        logging.warning("No ThunderBorg at address %02X, but we did find boards:" % (i2cAddress))
        for board in boards:
            logging.info("%02X (%d)" % (board, board))
        logging.info(
            "If you need to change the I2C address change the setup line so it is correct, e.g."
        )
        logging.info("TB.i2cAddress = 0x%02X" % (boards[0]))
    sys.exit()

TB.SetCommsFailsafe(False)  # Disable the communications failsafe

# initialise mpu6050 board
mpu = MPU6050()
mpu.setName("MPU6050")
mpu.start()

#hcsr = HCSR04(trigger_pin=12, echo_pin=24, echo_timeout_ns=1000000)
#hcsr.setName("HCSR04")
#hcsr.start()

def main(TB, mpu):
    """Main function used to run the application
    Key variables:
        input_matrix: a matrix representing the space the robot is in
        start_node: the node the robot is starting from
        end_node: the node the robot is trying to reach
    """
    input_matrix = [
        [1, 0, 0, 1],
        [1, 0, 1, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ]
    start_node = (0, 0)
    end_node = (3, 0)

    # Power settings
    VOLTAGE_IN = 9.6  # Total battery voltage to the ThunderBorg

    # NOTE: limiter has lower bound to power motors, ~0.4 experimental lower bound
    LIMITER = 0.85  # utilise only <limiter>% of power, to slow down actions

    VOLTAGE_OUT = (
        12.0 * LIMITER
    )  # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

    # Setup the power limits
    if VOLTAGE_OUT > VOLTAGE_IN:
        max_power = 1.0
    else:
        max_power = VOLTAGE_OUT / float(VOLTAGE_IN)

    algorithm = Algorithm(matrix=input_matrix, start_node=start_node, end_node=end_node)
    path = algorithm.use_a_star()

    instructions = pathing(path, 1)
    logging.debug(instructions)

    follow(instructions, TB, mpu, max_power)

if __name__ == "__main__":
    # enable debug logging
    logging.basicConfig(level=logging.DEBUG)

    try:
        main(TB, mpu)
    except:
        # stop motors
        TB.SetCommsFailsafe(False)
        TB.SetLeds(0,0,0)
        TB.MotorsOff()

        # end sensor thread
        mpu.join()

        # exit program
        logging.debug("Stopped")
        sys.exit()