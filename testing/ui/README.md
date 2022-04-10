# UI controller

### Robot node
- Websocket connection between robot and server.
    - Send location and sensor data.
    - Recieve new commands.

### Node.js
- Serves static client webpage.
- Boosts all websocket messages to all participants.

### Client
- HTML requests to Flask server to load webpage.
    - Recieve static files.
- Websocket connection between client and server.
    - Send new commands.
    - Recieve environment map data.
    - Recieve updates on robot position.
