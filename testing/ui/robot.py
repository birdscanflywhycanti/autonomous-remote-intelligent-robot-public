import asyncio
import logging
import json
import socketio
import sys

# asyncio
sio = socketio.AsyncClient()

@sio.on('*')
async def catch_all(event, data):
    logging.info(data)

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

    matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    grid = Grid(matrix=matrix)

    start = grid.node(0, 0)
    end = grid.node(2, 2)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    print(f"Running path: {path}")

    # iterate actions (intervening path coords to destination)
    # send a websocket message to server for each action
    for action in path:
        await sio.emit('json', json.dumps({'action':action}))
        logging.info(f"sent: {action}")
        await asyncio.sleep(1)

    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    url = sys.argv[1]

    res1, res2 = asyncio.get_event_loop().run_until_complete(main(url))

    