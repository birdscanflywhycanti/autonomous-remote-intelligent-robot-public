import asyncio
import logging
import websockets
import json

async def consumer_handler(websocket):
    async for message in websocket:
        logging.info(f"Message: {message}")


async def consume(hostname, port):
    websocket_resource_url = f"ws:{hostname}:{port}"
    async with websockets.connect(websocket_resource_url) as websocket:
        await consumer_handler(websocket)


async def produce(message, hostname, port):
    websocket_resource_url = f"ws:{hostname}:{port}"
    async with websockets.connect(websocket_resource_url) as websocket:
        await websocket.send(message)
        await websocket.recv()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # open listener thread
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume(hostname="localhost", port=5000))
    loop.run_forever()

    ### RUN A* TEST ###
    from pathfinding.core.diagonal_movement import DiagonalMovement
    from pathfinding.core.grid import Grid
    from pathfinding.finder.a_star import AStarFinder
    import time

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
        asyncio.run(produce(message=json.dumps({"action":action}), host='localhost', port=4000))