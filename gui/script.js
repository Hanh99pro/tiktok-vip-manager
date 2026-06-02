function log(message) {
  const box = document.getElementById("log");
  const time = new Date().toLocaleTimeString();
  box.textContent += `\n[${time}] ${message}`;
  box.scrollTop = box.scrollHeight;
}

async function loadAccounts() {
  const res = await fetch("/api/accounts?t="+Date.now());
  const data = await res.json();
  const select = document.getElementById("account");
  select.innerHTML = '<option value="">Chọn nick</option>';

  Object.entries(data).forEach(([key, name]) => {
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = `${key}. ${name}`;
    select.appendChild(opt);
  });
}

async function loadTopics() {
  const res = await fetch("/api/topics");
  const data = await res.json();
  const select = document.getElementById("topic");

  data.forEach((topic) => {
    const opt = document.createElement("option");
    opt.value = topic;
    opt.textContent = topic;
    select.appendChild(opt);
  });
}

async function loadStats() {
  const topic = document.getElementById("topic").value;

  if (!topic) return;

  const res = await fetch(`/api/stats?topic=${encodeURIComponent(topic)}`);
  const data = await res.json();

  document.getElementById("videosCount").textContent = data.videos;
  document.getElementById("pendingCount").textContent = data.pending;
  document.getElementById("uploadedCount").textContent = data.uploaded;
  
}

async function startBot() {
  const account = document.getElementById("account").value;
  const topic = document.getElementById("topic").value;
  const wait_seconds = document.getElementById("wait").value;
  const run_mode = document.getElementById("runMode").value;
  const start_time = document.getElementById("startTime").value;  
  

  const res = await fetch("/api/start", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({account, topic, wait_seconds,run_mode,
    start_time})
  });

  const data = await res.json();

  if (data.ok) {
    log(data.message);
  } else {
    log(`Lỗi: ${data.message}`);
    alert(data.message);
  }

  loadStats();
}

async function stopBot() {
  const res = await fetch("/api/stop", {method: "POST"});
  const data = await res.json();

  if (data.ok) {
    log(data.message);
  } else {
    log(`Lỗi: ${data.message}`);
  }
}
async function deleteSelectedAccount() {
  const account = document.getElementById("account").value;

  if (!account) {
    alert("Bạn chưa chọn tài khoản");
    return;
  }

  if (!confirm("Bạn chắc muốn xóa tài khoản này?")) {
    return;
  }

  const res = await fetch(`/api/accounts/${account}`, {
    method: "DELETE"
  });

  const data = await res.json();
  alert(data.message);

  if (data.ok) {
    window.location.reload();
  }
}
function addTikTokAccount() {
  alert("Hãy mở bằng tab ẩn danh hoặc đăng xuất TikTok trước khi thêm tài khoản mới.");
  window.open("/api/tiktok/login", "_blank");
}

function toggleStartTime() {
  const mode = document.getElementById("runMode").value;
  const startInput = document.getElementById("startTime");

  if (mode === "schedule") {
    startInput.style.display = "block";
  } else {
    startInput.style.display = "none";
    startInput.value = "";
  }
}
loadAccounts();
loadTopics();
setInterval(loadStats, 5000);
// setInterval(loadAccounts, 3000);

window.addEventListener("focus", () => {
  loadAccounts();
});