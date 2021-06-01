const express = require("express");
const socketio = require("socket.io");
const http = require("http");
const https = require("https");
const fs = require("fs");
const cors = require("cors");
const axios = require("axios");
const PORT = process.env.PORT || 5500;
const isHTTPS = process.env.HTTPS || "no";
const API_HOST = process.env.API_HOST || "http://django:8000";
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
    const usersInThisRoom = users[roomID]?.filter(
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
    const { roomID, text, token } = payload;

    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
    };
    axios
      .patch(
        `${API_HOST}/api/posts/${roomID}/update_shared_notes/`,
        {
          shared_notes: text,
        },
        config
      )
      .then((res) => {
        console.log(res.data);
        console.log("Update shared notes to django successfully");
      })
      .catch((err) => {
        console.log(err.response);
        console.log("Update shared notes to django failed");
      });
    socket.in(roomID).emit("text", text);
  });

  // CHAT
  socket.on("message", async (payload) => {
    const { roomID, token, message } = payload;
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
    };
    axios
      .post(
        `${API_HOST}/api/posts/${roomID}/messages/`,
        {
          text: message.text,
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
    console.log(payload);
    payload.token = null;
    socket.in(roomID).emit("message", payload);
  });

  // Shared whiteboard
  socket.on("drawing", (payload) => {
    console.log("enter on drawing", payload.roomID);
    socket.in(payload.roomID).emit("drawing", payload.data);
  });

  socket.on("clear canvas", (payload) => {
    socket.in(payload.roomID).emit("clear canvas");
  });

  // Kanban board

  socket.on("update list order", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    axios
      .patch(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/update_kanban_list_order/`,
        {
          droppable_index_start: payload.droppableIndexStart,
          droppable_index_end: payload.droppableIndexEnd,
        },
        config
      )
      .then((res) => {
        console.log("Sort list success", res.data);
      })
      .catch((err) => {
        console.log("Sort list error", err.response);
      });
    socket.in(payload.roomID).emit("list order updated", payload);
  });

  socket.on("update card order", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    axios
      .patch(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/update_kanban_card_order/`,
        {
          list_id: payload.droppableIdStart,
          droppable_index_start: payload.droppableIndexStart,
          droppable_index_end: payload.droppableIndexEnd,
        },
        config
      )
      .then((res) => {
        console.log("Sort card success", res.data);
      })
      .catch((err) => {
        console.log("Sort card error", err.response);
      });
    socket.in(payload.roomID).emit("card order updated", payload);
  });

  socket.on("update card between lists order", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    axios
      .patch(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/update_kanban_card_between_lists_order/`,
        {
          list_start_id: payload.droppableIdStart,
          list_end_id: payload.droppableIdEnd,
          droppable_index_start: payload.droppableIndexStart,
          droppable_index_end: payload.droppableIndexEnd,
        },
        config
      )
      .then((res) => {
        console.log("Sort card between lists success", res.data);
      })
      .catch((err) => {
        console.log("Sort card between lists error", err.response);
      });
    socket.in(payload.roomID).emit("card between lists order updated", payload);
  });

  socket.on("add list", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    await axios
      .post(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/kanbans/`,
        payload.newList,
        config
      )
      .then(async (res) => {
        console.log("Create list success", res.data);
      })
      .catch(async (err) => {
        console.log("Create list error", err.response);
      });
    socket.in(payload.roomID).emit("list added", payload);
  });

  socket.on("add card", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    await axios
      .post(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/kanbans/${payload.listID}/cards/`,
        payload.newCard,
        config
      )
      .then(async (res) => {
        console.log("Create card success", res.data);
      })
      .catch(async (err) => {
        console.log("Create card error", err.response);
      });
    socket.in(payload.roomID).emit("card added", payload);
  });

  socket.on("update list", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    await axios
      .patch(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/kanbans/${payload.listID}/`,
        payload.values,
        config
      )
      .then(async (res) => {
        console.log("Update list success", res.data);
      })
      .catch(async (err) => {
        console.log("Update list error", err.response);
      });
    socket.in(payload.roomID).emit("list updated", payload);
  });

  socket.on("update card", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    await axios
      .patch(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/kanbans/${payload.listID}/cards/${payload.cardID}/`,
        payload.values,
        config
      )
      .then(async (res) => {
        console.log("Update card success", res.data);
      })
      .catch(async (err) => {
        console.log("Update card error", err.response);
      });
    socket.in(payload.roomID).emit("card updated", payload);
  });

  socket.on("delete list", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    await axios
      .delete(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/kanbans/${payload.listID}/cards/${payload.cardID}/`,
        config
      )
      .then(async (res) => {
        console.log("Delete card success", res.data);
      })
      .catch(async (err) => {
        console.log("Delete card error", err.response);
      });
    socket.in(payload.roomID).emit("list deleted", payload);
  });

  socket.on("delete card", async (payload) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${payload.token}`,
      },
    };
    await axios
      .delete(
        `${API_HOST}/api/posts/${payload.collaborateRoomID}/kanbans/${payload.listID}/`,
        config
      )
      .then(async (res) => {
        console.log("Delete list success", res.data);
      })
      .catch(async (err) => {
        console.log("Delete list error", err.response);
      });
    socket.in(payload.roomID).emit("card deleted", payload);
  });

  socket.on("disconnect", () => {
    const roomID = socketToRoom[socket.id];
    console.log("User left", socket.id);
    io.to(roomID).emit("user left", socket.id);
    let room = users[roomID];
    if (room) {
      room = room?.filter((user) => user.socketID !== socket.id);
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
