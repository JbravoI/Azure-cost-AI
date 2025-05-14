const root = document.getElementById('root');

const app = document.createElement('div');
app.id = "app"; // <-- Needed for CSS
app.innerHTML = `
  <h1>Azure Cost AI</h1>
  <input id="prompt" placeholder="Ask a cost question..." />
  <button id="submit">Send</button>
  <pre id="output"></pre>
`;

root.appendChild(app);

async function sendPrompt() {
  const prompt = document.getElementById("prompt").value;
  const res = await fetch("http://localhost:5000/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });
  const data = await res.json();
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
}

document.getElementById("submit").onclick = sendPrompt;

document.getElementById("prompt").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendPrompt();
  }
});
