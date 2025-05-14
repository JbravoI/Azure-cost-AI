const root = document.getElementById('root');

const app = document.createElement('div');
app.innerHTML = `
  <h1>Azure Cost AI</h1>
  <input id="prompt" placeholder="Ask a cost question..." style="width: 300px;" />
  <button id="submit">Send</button>
  <pre id="output"></pre>
`;

root.appendChild(app);

document.getElementById("submit").onclick = async () => {
  const prompt = document.getElementById("prompt").value;
  const res = await fetch("http://localhost:5000/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });
  const data = await res.json();
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
};
