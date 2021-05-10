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
  socket.on("join room", (payload) => {
    const { roomID, userID } = payload;
    const userExists = users[roomID]?.some((user) => user.userID === userID);
    if (userExists) {
      users[roomID] = users[roomID]?.filter((user) => user.userID !== userID);
    }
    if (!userID) {
      socket.emit("no user id");
      return;
    }
    socket.join(roomID);

    console.log("New User has entered in room: " + roomID);
    console.log(users[roomID]);
    if (users[roomID]) {
      if (users[roomID].length === 10) {
        socket.emit("room full");
        return;
      }
      users[roomID].push({ socketID: socket.id, userID: userID });
    } else {
      users[roomID] = [{ socketID: socket.id, userID: userID }];
    }
    console.log("users:", users);
    socketToRoom[socket.id] = roomID;
    io.to(roomID).emit("joined members", users[roomID]);

    console.log("joined members", users[roomID]);
  });
  socket.on("media ready", (roomID) => {
    console.log("media ready");
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
    console.log(roomID, text);
    socket.in(roomID).emit("text", text);
  });

  // CHAT
  socket.on("message", async (payload) => {
    const { roomID } = payload;
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    console.log(`${API_HOST}/api/chats/${roomID}/messages/`);
    axios
      .post(
        `${API_HOST}/api/chats/${roomID}/messages/`,
        {
          text: payload.message.text,
        },
        config
      )
      .then((res) => {
        console.log(res.data);
        console.log("Post message to django successfully");
      })
      .catch((err) => {
        console.log(err.response);
        console.log("Post message to django failed");
      });
    payload.token = null;
    socket.in(roomID).emit("text", payload);
  });

  socket.on("disconnect", () => {
    const roomID = socketToRoom[socket.id];
    console.log("User left", socket.id);
    io.to(roomID).emit("user left", socket.id);
    let room = users[roomID];
    if (room) {
      room = room.filter((user) => user.socketID !== socket.id);
      users[roomID] = room;
    }
    console.log("members left", users[roomID]);
    io.to(roomID).emit("members left", users[roomID]);

    console.log("User  ");
  });
});

app.use(cors());
app.use(router);

server.listen(PORT, () => console.log(`Server has started on port ${PORT}`));
