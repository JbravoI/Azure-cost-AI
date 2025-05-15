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
    
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    tenant = data.get("tenant")

    from cost_ai import login_with_credentials, list_azure_subscriptions

    login_result = login_with_credentials(username, password, tenant)

    if "error" in login_result:
        return jsonify(login_result)

    subscriptions = list_azure_subscriptions()
    return jsonify({
        "message": "Login successful",
        "subscriptions": subscriptions
    })
