const root = document.getElementById("root");

// Create app layout
const app = document.createElement("div");
app.id = "app";
app.innerHTML = `
  <h1>Azure Cost AI</h1>
  <input id="prompt" placeholder="Ask a cost question..." />
  <button id="submit">Send</button>
  <pre id="output"></pre>
  <div id="loginForm" style="display:none; margin-top:20px;">
    <h3>Azure Login</h3>
    <input id="username" placeholder="Client ID" style="display:block; margin-bottom: 10px;" />
    <input id="password" placeholder="Client Secret" type="password" style="display:block; margin-bottom: 10px;" />
    <input id="tenant" placeholder="Tenant ID" style="display:block; margin-bottom: 10px;" />
    <button id="loginBtn">Login</button>
  </div>
`;
root.appendChild(app);

// Handle prompt submission
async function sendPrompt() {
  const promptInput = document.getElementById("prompt");
  const output = document.getElementById("output");
  const loginForm = document.getElementById("loginForm");

  const prompt = promptInput.value.trim();
  if (!prompt) return;

  output.textContent = "Processing...";
  loginForm.style.display = "none";

  try {
    const res = await fetch("http://localhost:5000/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();

    if (data.require_login) {
      output.textContent = "Azure login required. Please provide credentials.";
      loginForm.style.display = "block";
    } else {
      output.textContent = JSON.stringify(data, null, 2);
    }
  } catch (error) {
    output.textContent = "Error: " + error.message;
  }

  promptInput.value = "";
}

// Handle login form submission
async function submitLogin() {
  const output = document.getElementById("output");

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const tenant = document.getElementById("tenant").value.trim();

  if (!username || !password || !tenant) {
    output.textContent = "All fields are required for login.";
    return;
  }

  output.textContent = "Logging in to Azure...";

  try {
    const res = await fetch("http://localhost:5000/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, tenant }),
    });
    const data = await res.json();

    if (data.error) {
      output.textContent = "Login failed: " + data.error;
    } else {
      let text = `${data.message}\n\nSubscriptions:\n`;
      if (Array.isArray(data.subscriptions)) {
        data.subscriptions.forEach((sub, index) => {
          text += `\n${index + 1}. ${sub.name} (${sub.id}) - ${sub.state}`;
        });
      } else {
        text += "Failed to retrieve subscriptions.";
      }
      output.textContent = text;
    }
  } catch (error) {
    output.textContent = "Login error: " + error.message;
  }
}

// Add event listeners
document.getElementById("submit").onclick = sendPrompt;
document.getElementById("prompt").addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendPrompt();
});
document.getElementById("loginBtn").onclick = submitLogin;
