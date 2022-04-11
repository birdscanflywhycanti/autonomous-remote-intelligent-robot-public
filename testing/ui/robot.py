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

# asyncio
sio = socketio.AsyncClient()

@sio.on('*')
async def catch_all(event, data):
    logging.info(data)
    json_data = json.loads(data)

    destination = json_data['dest']
    angle = json_data['angle']

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

    coroutines = [listen(), test()]
    res = await asyncio.gather(*coroutines, return_exceptions=True)

    return res

async def test():
    ### RUN A* TEST ###
    from pathfinding.core.diagonal_movement import DiagonalMovement
    from pathfinding.core.grid import Grid
    from pathfinding.finder.a_star import AStarFinder

    logging.debug("0")

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

    logging.debug("1")

    logging.debug("2")

    matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    grid = Grid(matrix=matrix)

    start = grid.node(0, 0)
    end = grid.node(2, 2)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    logging.debug("3")

    instructions = instruction_list(pathing(path, 1, final_angle=180))

    logging.info(f"Running path: {path}")

    await follow(instructions, None, None, 0)

    logging.debug("4")


async def follow(instructions, TB, mpu, max_power):

    logging.debug("3.1")

    while instructions.size > 0:
        action, arg = instructions.pop()

        await sio.emit('json', json.dumps({'action':action}))

        logging.debug("3.2")

        action(*arg, TB, mpu, max_power)

        logging.debug("3.3")
        
        logging.info(f"sent: {action}")

        await asyncio.sleep(1)


class instruction_list:
    def __init__(self, instructions):
        self.instructions = []
        self.size = 0

    def pop(self):
        x = self.instructions.pop(0)
        self.size = len(self.instructions)
        return x

    def set(self, instructions):
        self.instructions = instructions
        self.size = len(self.instructions)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    url = sys.argv[1]

    res1, res2 = asyncio.get_event_loop().run_until_complete(main(url))

    