import asyncio
import logging
import json
import socketio
import sys
import time

import adafruit_mpu6050
import board
import ThunderBorg3 as ThunderBorg  # conversion for python 3

from robot import perform_spin, perform_drive, pathing

import queue

# asyncio
sio = socketio.AsyncClient()

@sio.on('*')
async def catch_all(event, data):
    logging.info(data)
    json_data = json.loads(data)

    destination = json_data['dest']
    angle = json_data['angle']

    # calculate movement to new position

    # add instructions to movement queue
    instruction_queue.put((action, arg))

@sio.event
async def disconnect():
    logging.warning('disconnected from server')

@sio.event
async def send_json(data):
    await sio.emit('json', json.dumps())

async def listen():
    await sio.wait()

async def main(url):
    await sio.connect(url)

    coroutines = [listen(), follow()]
    res = await asyncio.gather(*coroutines, return_exceptions=True)

    return res

async def follow(instructions, TB, mpu, max_power):

    # initialise some objects for movement
    # initialise gyroscope board
    i2c = board.I2C()  # uses board.SCL and board.SDA
    mpu = adafruit_mpu6050.MPU6050(i2c)

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

    # repeat forever
    while 1:
        if not instruction_queue.empty():
            action, arg = instruction_queue.get()    # poll queue for instruction
        else:
            await asyncio.sleep(1)

        action(*arg, TB, mpu, max_power)    # execute instruction
        
        await sio.emit('json', json.dumps({'action':action}))   # emit new location to server

        instruction_queue.task_done()
        logging.info(f"sent: {action}")
        

if __name__ == "__main__":
    instruction_queue = queue.Queue()

    logging.basicConfig(level=logging.DEBUG)

    url = sys.argv[1]

    res1, res2 = asyncio.get_event_loop().run_until_complete(main(url))

    