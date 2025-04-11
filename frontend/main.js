let token = '';
let currentUser = '';
const API_URL = "http://localhost:8000";
const WS_URL = "ws://localhost:8000";
async function register() {
  const username = document.getElementById('reg-username').value;
  const password = document.getElementById('reg-password').value;

  const res = await fetch(`${API_URL}/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  alert(data.detail || 'Registered!');
}

async function login() {
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      username,
      password
    })
  });

  if (res.ok) {
    const data = await res.json();
    token = data.access_token;
    document.getElementById("room-actions").classList.remove("hidden");
    alert("Login successful!");
  } else {
    alert("Login failed.");
  }
}

// ✅ Create Room
async function createRoom() {
    const name = document.getElementById("room-name").value;
  
    const res = await fetch(`${API_URL}/rooms/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ name })
    });
  
    if (res.ok) {
      alert("Room created");
      listRooms();
    } else {
      alert("Failed to create room");
    }
  }
  
  async function listRooms() {
    const res = await fetch(`${API_URL}/rooms/rooms/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  
    const rooms = await res.json();
    const list = document.getElementById("room-list");
    list.innerHTML = "";
  
    rooms.forEach((room) => {
      const div = document.createElement("div");
      div.className = "room-entry";
  
      const span = document.createElement("span");
      span.innerText = `${room.name} (ID: ${room.id.slice(0, 6)}...)`; // Show partial ID for clarity
  
      const button = document.createElement("button");
      button.innerText = "Join";
      button.onclick = () => {
        console.log("🟢 Join button clicked for:", room.id);
        joinRoom(room.id);
      };
  
      div.appendChild(span);
      div.appendChild(button);
      list.appendChild(div);
    });
  }
  
  async function joinRoom(roomId) {
    try {
      const res = await fetch(`${API_URL}/rooms/${roomId}/join`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (res.ok) {
        console.log("✅ Joined room via API");
      } else {
        const data = await res.json();
        if (res.status === 400 && data.detail === "User already in the room") {
          console.warn("⚠️ Already in room, proceeding to chat...");
        } else {
          alert("❌ Failed to join room: " + data.detail);
          return;
        }
      }
    } catch (err) {
      console.error("Error while joining room:", err);
      return;
    }
  
    // ✅ Now proceed to open WebSocket connection
    currentRoomId = roomId;
    document.getElementById("chat-area").classList.remove("hidden");
  
    const socketUrl = `${WS_URL}/ws/rooms/${roomId}?token=${token}`;
    console.log("🔌 Connecting to WebSocket:", socketUrl);
  
    ws = new WebSocket(socketUrl);
  
    ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };
  
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
  
      const messagesDiv = document.getElementById("messages");
      const peopleList = document.getElementById("people");

      if (data.type === "presence") {
        const peopleList = document.getElementById("people");
        peopleList.innerHTML = "";
        data.users.forEach(user => {
          const li = document.createElement("li");
          li.innerText = user;
          peopleList.appendChild(li);
        });
      }
  
      if (data.type === "chat") {
        const messagesDiv = document.getElementById("messages");
        messagesDiv.innerHTML += `<div><b>${data.sender}:</b> ${data.message}</div>`;
      }
  
      if (data.type === "init") {
        messagesDiv.innerHTML = "";
        peopleList.innerHTML = "";
        data.messages.forEach((msg) => {
          messagesDiv.innerHTML += `<div><b>${msg.sender}:</b> ${msg.message}</div>`;
        });
        data.people.forEach((user) => {
          const li = document.createElement("li");
          li.innerText = user;
          peopleList.appendChild(li);
        });
      }
  
      if (data.type === "user_joined") {
        const li = document.createElement("li");
        li.innerText = data.username;
        peopleList.appendChild(li);
      }
  
      if (data.type === "user_left") {
        const items = peopleList.querySelectorAll("li");
        items.forEach((item) => {
          if (item.innerText === data.username) {
            peopleList.removeChild(item);
          }
        });
      }
    
      if (data.type === "join" || data.type === "leave") {
        const messagesDiv = document.getElementById("messages");
        messagesDiv.innerHTML += `<div style="color: gray;"><i>${data.message}</i></div>`;
      }
      
    };
    document.getElementById("send-btn").addEventListener("click", () => {
        const input = document.getElementById("message-input");
        const message = input.value.trim();
      
        if (message && ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: "chat",
            message: message
          }));
          input.value = "";
        }
      });
      
  
    ws.onclose = () => {
      console.log("❌ WebSocket disconnected");
    };
  }
  
  
  