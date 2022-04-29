import asyncio
import json
import logging
import queue
import sys
import time

import adafruit_mpu6050
import board
import socketio

import pygame
import threading

import ThunderBorg3 as ThunderBorg  # conversion for python 3
from algorithms.algorithm import Algorithm

from pathfinding.core.grid import Grid

from robot.accelerometer import perform_drive
from robot.gyroscope import perform_spin
from robot.drive import follow, pathing, get_move_string, calculate_angle

from mpu6050 import MPU6050



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

mpu = MPU6050()
mpu.setName("MPU6050")
mpu.start()

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

# asyncio
sio = socketio.AsyncClient()

curr_position = (0, 0)
matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]

instruction_queue = queue.Queue()
emitQueue = queue.Queue()

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
        path = alg.use_a_star()
        instructions = pathing(path, 1)

        # add instructions to movement queue

        while not instruction_queue.empty():
            instruction_queue.get()
            instruction_queue.task_done()

        for path, instruction in list(zip(path, instructions)):
            instruction_queue.put((path, instruction))

        print(instruction_queue.qsize())

    elif "idKey" in json_data and json_data["idKey"] == "mapRequest":
        grid = Grid(matrix=matrix)
        emitQueue.put(json.dumps({'idKey': 'mapUpdate', 'map': grid.grid_str()}))


@sio.event
async def disconnect():
    logging.warning("disconnected from server")


@sio.event
async def send_json(data):
    await sio.emit("json", json.dumps())


async def listen():
    await sio.wait()


async def talk():
    while 1:
        if not emitQueue.empty():
            data = emitQueue.get()  # poll queue for instruction

            await sio.emit(
                "json", data,
            )  # emit new location to server
            emitQueue.task_done()
        else:
            print("sleep")
            await asyncio.sleep(0.5)

async def main(url):
    await sio.connect(url)

    coroutines = [listen(), talk()]
    res = await asyncio.gather(*coroutines, return_exceptions=True)

    return res

class Follow(threading.Thread):
    def __init__(self):
        super(Follow, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        print('Waiting for instructions..')
        while not self.terminated:
            if not instruction_queue.empty():
                (x, y), (action, arg) = instruction_queue.get()  # poll queue for instruction
                print("Action: ", action, arg)

                action(*arg, TB, mpu, max_power)  # execute instruction

                curr_position[:] = (x, y)

                emitQueue.put(
                    json.dumps(
                        {'idKey': 'robotUpdate', 'x': x, 'y': y}
                    )
                )  # emit new location to server
                instruction_queue.task_done()
            else:
                print("sleep")
                time.sleep(0.5)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.DEBUG)

        followthread = Follow()

        url = sys.argv[1]

        res1, res2 = asyncio.get_event_loop().run_until_complete(main(url))
    except:
        TB.SetCommsFailsafe(False)
        TB.SetLeds(0,0,0)
        TB.MotorsOff()

        # end sensor thread
        mpu.join()
        followthread.join()

        # exit program
        logging.debug("Stopped")
        sys.exit()