import asyncio
import json
import logging
import queue
import sys
import time

import adafruit_mpu6050
import board
import socketio

import ThunderBorg3 as ThunderBorg  # conversion for python 3
from algorithms.algorithm import Algorithm

# asyncio
sio = socketio.AsyncClient()


@sio.on("*")
async def catch_all(event, data):
    logging.info(data)
    json_data = json.loads(data)

    print(json_data)
    if "idKey" in json_data and json_data["idKey"] == "destUpdate":
        destination = json_data["dest"]
        angle = json_data["angle"]

        # calculate movement to new position
        alg = Algorithm(matrix, curr_position, destination)
        instructions = pathing(alg.use_a_star(), 1)

        # add instructions to movement queue

        while not instruction_queue.empty():
            instruction_queue.get()
            instruction_queue.task_done()

        for instruction in instructions:
            instruction_queue.put(instruction)
            print(instruction)

        print(instruction_queue.qsize())


@sio.event
async def disconnect():
    logging.warning("disconnected from server")


@sio.event
async def send_json(data):
    await sio.emit("json", json.dumps())


async def listen():
    await sio.wait()


async def main(url):
    await sio.connect(url)

    coroutines = [listen(), follow()]
    res = await asyncio.gather(*coroutines, return_exceptions=True)

    return res


async def follow():

    # repeat forever
    while 1:

        if not instruction_queue.empty():
            action, arg = instruction_queue.get()  # poll queue for instruction
            print("follw", action, arg)

            action(*arg, TB, mpu, max_power)  # execute instruction

            await sio.emit(
                "json",
                json.dumps(
                    {
                        "idKey": "robotUpdate",
                        "x": curr_position[0],
                        "y": curr_position[1],
                    }
                ),
            )  # emit new location to server
            instruction_queue.task_done()
        else:
            print("sleep")
            await asyncio.sleep(1)


"""Contains functionality for driving the robot"""

import logging
import math
import time


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
    print("spimmimg")
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
            (vertical * unit_size) ** 2 + (horizontal * unit_size) ** 2
        )  # Pythagorean theorem
        instructions.append(
            (perform_drive, (drive_distance,))
        )  # NOTE: wrap drive_distance in tuple to be compatible when unpacking as with perform_spin (the trailing comma is important!)

        logging.debug(get_move_string(vertical, horizontal))
        logging.debug(
            "delta angle:" + str(delta_angle) + " global angle:" + str(target_angle)
        )

        x, y = x_, y_

    """
    # reorient to face north
    delta_angle = (
        0 - curr_angle
    )  # calculate the difference in between the current and the target angle

    instructions.append(
        (perform_spin, delta_angle)
    )  # rotate the car to match the target angle by rotating the remaining distance
    """

    return instructions


# Function to drive a distance in meters
def perform_drive(meters, TB, mpu, max_power):
    """Drive a distance in meters.

    Args:
        meters (float): distance to drive in meters.
    """
    print("drive")
    power = max_power * 0.75

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
    print("drive2")
    TB.SetMotor1(drive_right * power)
    print("drive22")
    TB.SetMotor2(drive_left * power)
    print("drive222")

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


# Function to spin an angle in degrees
def perform_spin(delta, target, TB, mpu, max_power):
    """Spin an angle in degrees.

    Args:
        delta (float): angle to spin in degrees.
    """

    power = max_power * 0.75

    if delta < 0.0:
        # Left turn
        drive_left = -1.0
        drive_right = +1.0
        delta *= -1
    else:
        # Right turn
        drive_left = +1.0
        drive_right = -1.0

    offset = (mpu.orientation + delta) - (
        target + delta
    )  # calculate offset from target+delta versus actual+delta
    delta += (
        offset  # update delta with offset to align according to actual initial angle
    )

    # Set the motors running
    TB.SetMotor1(drive_right * power)
    TB.SetMotor2(drive_left * power)

    # poll the gyroscope for rotation
    # NOTE: sampling limited by real-time clock on system \
    # (0.1ms theoretical minimum, but experimentally encountered errors)

    # poll every <sampling> seconds, fine tune to minimise overshooting target rotation
    sampling = 0.08
    total_rotation = 0

    while True:
        abs_z = mpu.gyro_abs_z
        sample = mpu.abs_z * sampling

        # print("Gyro X:%.2f, Y: %.2f, Z: %.2f rad/s" % (x, y, z))
        if logging.isEnabledFor(logging.DEBUG):
            x, y, z = mpu.gyro
            x, y, z = math.degrees(x), math.degrees(y), math.degrees(z)
            logging.debug(
                "Gyro: X:%.2f, Y: %.2f, Z: %.2f deg/s \t sample:%.2f \t total:%.2f"
                % (x, y, z, sample, total_rotation)
            )
        # print(total_rotation)

        # NOTE: z-axis experimentally defined as 2d plane orientation

        # increment degree rotation by current rotation velocity, divided by sampling time
        total_rotation += sample

        # if exceeded target exit
        if total_rotation >= delta:
            break  # exit once achieved target rotation
        # if predicted to exceed during sleep, sleep for predicted time to target, then exit
        elif (total_rotation + sample) >= delta:
            # total degrees left in rotation (degress-total_rotation) divided by abs(z)\
            # (positive rotational velocity) gives time to sleep (in seconds) before reaching target
            sleep = (delta - total_rotation) / abs_z

            logging.debug(
                "Assuming constant rotation of Z:%.2f, sleeping for %.2f seconds to rotate %.2f degrees"
                % (abs_z, sleep, (delta - total_rotation))
            )
            time.sleep(sleep)

            # NOTE: this will set total rotation to target, which is only correct \
            # assuming rotation halts immediately and rotational velocity remains constant

            # in non-demo system current orientation should be independently \
            # tracked, not adjusted using this approximation

            total_rotation += abs_z * sleep  # update final rotation for tracking
            break

        time.sleep(sampling)

    # Turn the motors off
    TB.MotorsOff()

    logging.debug(f"total rotation: {total_rotation}")


if __name__ == "__main__":

    # initialise some objects for movement
    # initialise gyroscope board
    logging.debug("0.111")
    i2c = board.I2C()  # uses board.SCL and board.SDA
    mpu = adafruit_mpu6050.MPU6050(i2c)
    logging.debug("0.1")
    # Setup the ThunderBorg
    TB = ThunderBorg.ThunderBorg()
    logging.debug("0.1")
    # TB.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
    TB.Init()

    logging.debug("0.2")

    if not TB.foundChip:
        boards = ThunderBorg.ScanForThunderBorg()
        if len(boards) == 0:
            print("No ThunderBorg found, check you are attached :)")
        else:
            print(
                "No ThunderBorg at address %02X, but we did find boards:"
                % (TB.i2cAddress)
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
    VOLTAGE_IN = 9.6  # Total battery voltage to the ThunderBorg

    # NOTE: limiter has lower bound to power motors, ~0.4 experimental lower bound
    LIMITER = 0.6  # utilise only <limiter>% of power, to slow down actions

    VOLTAGE_OUT = (
        12.0 * LIMITER
    )  # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

    # Setup the power limits
    if VOLTAGE_OUT > VOLTAGE_IN:
        max_power = 1.0
    else:
        max_power = VOLTAGE_OUT / float(VOLTAGE_IN)

    curr_position = (0, 0)
    matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    instruction_queue = queue.Queue()

    logging.basicConfig(level=logging.DEBUG)

    url = sys.argv[1]

    res1, res2 = asyncio.get_event_loop().run_until_complete(main(url))
