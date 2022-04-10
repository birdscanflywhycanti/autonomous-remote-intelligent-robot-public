# UI controller

### Client
- HTML requests to Flask server to load webpage.
    - Recieve static files.
- Websocket connection between client and server.
    - Send new commands.
    - Recieve environment map data.
    - Recieve updates on robot position.

### Server
- Flask server for static resources for client interface.
    - Send static files.
- Flask SocketIO server for opening websocket between server and client.
    - Send robot location and sensor updates.
    - Recieve new commands.
- Websocket connection between server and robot.
    - Send new commands.
    - Recieve sensor and location data.

### Robot
- Websocket connection between robot and server.
    - Send location and sensor data.
    - Recieve new commands.