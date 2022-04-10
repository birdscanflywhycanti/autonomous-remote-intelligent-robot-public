from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, send
import json
import os
import requests
import asyncio
import logging
import websockets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

node_url = ""

landmarks = {
    # dummy list of landmarks (by name) and corresponding coords
    "door 1": (0, 1),
    "door 2": (4, 2),
}

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

def get_landmark_coords(landmark):
    # read coordinate data from landmark table
    if landmark in landmarks:
        coords = landmarks[landmark]
    else:
        return False

    return coords

@socketio.on('json')
def handle_json(json):
    logging.info('Received json: ' + str(json))


@socketio.on('connect')
def test_connect():
    logging.info("I'm connected")


async def update_client(env):
    emit('update',  {'env': env})


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
    socketio.run(app)
