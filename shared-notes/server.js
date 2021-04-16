const express = require("express");
const socketio = require("socket.io");
const http = require("http");
const cors = require("cors");
const PORT = process.env.PORT || 5000;

const router = require("./router");

const app = express();
const server = http.createServer(app);
const io = socketio(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"],
  },
});
io.sockets.on("connection", connection);

const text = {
  text: "",
};

function connection(socket) {
  socket.on("create", function (room) {
    console.log("room1 created");
    socket.join(room);
  });

  console.log("a new user with id " + socket.id + " has entered");
  // socket.emit("newUser", text);

  function handleTextSent(data) {
    if (data) {
      text.text = data;
    }
    // socket.broadcast.emit("text", text);
    socket.broadcast.in("room1").emit("text", text);
  }

  socket.on("text", handleTextSent);
}
app.use(cors());
app.use(router);

server.listen(PORT, () => console.log(`Server has started on port ${PORT}`));
