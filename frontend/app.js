const root = document.getElementById('root');

// Create app layout
const app = document.createElement('div');
app.id = "app";
app.innerHTML = `
  <h1>Azure Cost AI</h1>
  <input id="prompt" placeholder="Ask a cost question..." />
  <button id="submit">Send</button>
  <pre id="output"></pre>
`;

root.appendChild(app);

// Define function to send prompt to backend
async function sendPrompt() {
  const promptInput = document.getElementById("prompt");
  const output = document.getElementById("output");
  const prompt = promptInput.value.trim();

  if (!prompt) return;

  output.textContent = "Loading...";
  try {
    const res = await fetch("http://localhost:5000/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = "Error: " + error.message;
  }

  promptInput.value = "";
}

// Click handler
document.getElementById("submit").onclick = sendPrompt;

// Enter key handler
document.getElementById("prompt").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendPrompt();
  }
});
