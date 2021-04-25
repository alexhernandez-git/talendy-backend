const express = require("express");
const socketio = require("socket.io");
const http = require("http");
const cors = require("cors");
const PORT = process.env.PORT || 5400;

const router = require("./router");

const app = express();
const server = http.createServer(app);
const io = socketio(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"],
  },
});

io.on("connection", (socket) => {
  socket.on("join room", (roomID) => {
    socket.join(roomID);
  });

  socket.on("text", (payload) => {
    const { roomID } = payload;
    socket.in(roomID).emit("text", payload);
  });

  socket.on("disconnect", () => {
    console.log("User disconnect");
  });
});

app.use(cors());
app.use(router);

server.listen(PORT, () => console.log(`Server has started on port ${PORT}`));
