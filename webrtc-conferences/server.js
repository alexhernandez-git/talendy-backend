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
  console.log(users);
  console.log(socketToRoom);
  console.log(socket.id);

  socket.on("join room", (payload) => {
    const { roomID, userID } = payload;
    const userExists = users[roomID]?.some((user) => user.userID === userID);
    if (userExists) {
      socket.emit("not allowed");
      return;
    }
    if (!userID) {
      socket.emit("no user id");
      return;
    }
    socket.join(roomID);
    socket.join(userID);

    console.log("New User has entered in room: " + roomID);
    console.log(users[roomID]);
    if (users[roomID]) {
      if (users[roomID].length === 5) {
        socket.emit("room full");
        return;
      }
      users[roomID].push({ socketID: socket.id, userID: userID });
    } else {
      users[roomID] = [{ socketID: socket.id, userID: userID }];
    }
    console.log("users:", users);
    socketToRoom[socket.id] = roomID;
    const usersInThisRoom = users[roomID].filter(
      (user) => user.socketID !== socket.id
    );

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
      room = room.filter((user) => user.socketID !== socket.id);
      users[roomID] = room;
    }
    console.log("User disconnect");
  });
});

app.use(cors());
app.use(router);

server.listen(PORT, () => console.log(`Server has started on port ${PORT}`));
