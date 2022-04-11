"""
Rotate given angle, tracked using gyroscope.
"""

import math
import sys
import time

import adafruit_mpu6050
import board
import ThunderBorg3 as ThunderBorg  # conversion for python 3

import logging

# Function to drive a distance in meters
def perform_drive(meters, TB, mpu, max_power):
    """Drive a distance in meters.

    Args:
        meters (float): distance to drive in meters.
    """
    power = max_power*0.75

    if meters < 0.0:
        # Reverse drive
        drive_left = -1.0
        drive_right = -1.0
        meters *= -1
    else:
        # Forward drive
        drive_left = +1.0
        drive_right = +1.0

    # Perform the motion
    # Set the motors running
    TB.SetMotor1(drive_right * power)
    TB.SetMotor2(drive_left * power)

    # poll the gyroscope for acceleration
    # NOTE: sampling limited by real-time clock on system (0.1ms theoretical minimum, but experimentally encountered errors)

    # poll every <sampling> seconds, fine tune to minimise overshooting target rotation
    sampling = 0.08
    total_motion = 0

    velocity = 0

    while True:
        x, y, z = mpu.acceleration
        # x, y, z = math.degrees(x), math.degrees(y), math.degrees(z)

        # Calculate current velocity of vehicle from acceleration by time since last sample
        change_in_velocity = z * sampling  # velocity = acceleration * time
        velocity += change_in_velocity
        sample = velocity * sampling

        logging.debug("Acceleration X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (x, y, z))
        logging.debug(
            "Velocity: X:%.2f, Y: %.2f, Z: %.2f m/s \t sample:%.2f \t total:%.2f"
            % (x, y, z, sample, total_motion)
        )
        # print(total_motion)

        # NOTE: z-axis experimentally defined as 2d plane forward axis
        total_motion += (
            sample  # increment total motion by distance moved, divided by sampling time
        )

        # if exceeded target exit
        if total_motion >= meters:
            break  # exit once achieved target rotation
        # if predicted to exceed during sleep, sleep for predicted time to target, then exit
        elif (total_motion + sample) >= meters:
            # total degrees left in metres (meters-total_motion) divided by abs(z)
            # (positive acceleration) gives time to sleep (in seconds) before reaching target
            sleep = (meters - total_motion) / velocity

            logging.debug(
                "Assuming constant velocity of Z:%.2f, sleeping for %.2f seconds to drive %.2f meters"
                % (velocity, sleep, (meters - total_motion))
            )
            time.sleep(sleep)

            # NOTE: this will set total motion to target, which is only correct assuming rotation halts immediately and velocity remains constant
            # in non-demo system current orientation should be independently tracked, not adjusted using this approximation
            total_motion += velocity * sleep  # update final rotation for tracking
            break

        time.sleep(sampling)

    # Turn the motors off
    TB.MotorsOff()

    logging.debug(f"total motion: {total_motion}")


if __name__ == "__main__":
    # enable debug logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

    # Setup the ThunderBorg
    TB = ThunderBorg.ThunderBorg()
    # TB.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
    TB.Init()
    if not TB.foundChip:
        boards = ThunderBorg.ScanForThunderBorg()
        if len(boards) == 0:
            logging.warning("No ThunderBorg found, check you are attached :)")
        else:
            logging.warning(
                "No ThunderBorg at address %02X, but we did find boards:"
                % (TB.i2cAddress)
            )
            for board in boards:
                logging.info("    %02X (%d)" % (board, board))
            logging.info(
                "If you need to change the I2C address change the setup line so it is correct, e.g."
            )
            logging.info("TB.i2cAddress = 0x%02X" % (boards[0]))
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
        max_power = 1.0
    else:
        max_power = voltageOut / float(voltageIn)

    # initialise gyroscope board
    i2c = board.I2C()  # uses board.SCL and board.SDA
    mpu = adafruit_mpu6050.MPU6050(i2c)

    perform_drive(0.5)
