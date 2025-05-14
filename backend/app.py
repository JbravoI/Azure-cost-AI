from flask import Flask, request, jsonify
from cost_ai import process_prompt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    prompt = data.get("prompt", "")
    response = process_prompt(prompt)
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
