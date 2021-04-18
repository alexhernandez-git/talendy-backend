const express = require("express");
const socketio = require("socket.io");
const http = require("http");
const cors = require("cors");
const PORT = process.env.PORT || 5500;

const router = require("./router");

const app = express();
const server = http.createServer(app);
const io = socketio(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"],
  },
});

const users = {};

const socketToRoom = {};

io.on("connection", (socket) => {
  socket.on("create", function (roomID) {
    console.log("room1 created");
    socket.join(roomID);
  });

  socket.on("join room", (roomID) => {
    console.log("New User has entered in room: " + roomID);
    console.log(users[roomID]);
    if (users[roomID]) {
      if (users[roomID].length === 5) {
        socket.emit("room full");
        return;
      }
      users[roomID].push(socket.id);
    } else {
      users[roomID] = [socket.id];
    }
    socketToRoom[socket.id] = roomID;
    const usersInThisRoom = users[roomID].filter((id) => id !== socket.id);

    socket.emit("all users", usersInThisRoom);
  });

  socket.on("sending signal", (payload) => {
    io.to(payload.userToSignal).emit("user joined", {
      signal: payload.signal,
      callerID: payload.callerID,
    });
  });

  socket.on("returning signal", (payload) => {
    io.to(payload.callerID).emit("receiving returned signal", {
      signal: payload.signal,
      id: socket.id,
    });
  });

  // SHARED NOTES
  socket.on("text", (payload) => {
    const { roomID, text } = payload;
    console.log(roomID);
    console.log(text);
    socket.broadcast.emit("text", text);
  });

  socket.on("disconnect", () => {
    const roomID = socketToRoom[socket.id];
    io.to(roomID).emit("user left", socket.id);
    let room = users[roomID];
    if (room) {
      room = room.filter((id) => id !== socket.id);
      users[roomID] = room;
    }
    console.log("User disconnect");
  });
});

app.use(cors());
app.use(router);

server.listen(PORT, () => console.log(`Server has started on port ${PORT}`));
