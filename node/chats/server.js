const express = require("express");
const socketio = require("socket.io");
const http = require("http");
const https = require("https");
const cors = require("cors");
const PORT = process.env.PORT || 5400;
const isHTTPS = process.env.HTTPS || "no";
const API_HOST = process.env.API_HOST || "http://django:8000";
console.log(process.env.API_HOST);
const fs = require("fs");
const axios = require("axios");
const router = require("./router");
const app = express();
let server;
let io;
if (isHTTPS === "yes") {
  const options = {
    key: fs.readFileSync("/etc/letsencrypt/live/api.talendy.com/privkey.pem"),
    cert: fs.readFileSync(
      "/etc/letsencrypt/live/api.talendy.com/fullchain.pem"
    ),
  };
  server = https.createServer(options, app);
  io = socketio(server, {
    cors: {
      origin: ["https://talendy.com", "https://www.talendy.com"],
      methods: ["GET", "POST"],
    },
  });
} else {
  server = http.createServer(app);
  io = socketio(server, {
    cors: {
      origin: ["http://localhost:3000"],
      methods: ["GET", "POST"],
    },
  });
}

io.on("connection", (socket) => {
  socket.on("join room", (roomID) => {
    socket.join(roomID);
  });

  socket.on("text", async (payload) => {
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
        console.log("Message to django successfully");
      })
      .catch((err) => {
        console.log(err.response);
        console.log("Message to django failed");
      });
    payload.token = null;
    socket.in(roomID).emit("text", payload);
  });

  socket.on("disconnect", () => {
    console.log("User disconnect");
  });
});

app.use(cors());
app.use(router);

server.listen(PORT, () => console.log(`Server has started on port ${PORT}`));
