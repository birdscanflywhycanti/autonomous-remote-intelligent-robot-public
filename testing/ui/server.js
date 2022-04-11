const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);

app.get('/', (req, res) => {
  console.log(__dirname)
  console.log(req.url)
  res.sendFile(__dirname + '/public/index.html');
});

app.use(express.static('public'))

io.on('connection', (socket) => {
  console.log('a user connected');
  socket.on('disconnect', () => {
    console.log('user disconnected');
  });

  socket.on('json', (data) => {
    console.log('message: ' + data);
    socket.broadcast.emit('mirror', data);
  });
});

server.listen(3000, () => {
  console.log('listening on *:3000');
});