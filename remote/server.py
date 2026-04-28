from flask import Flask, request, jsonify, render_template
import os
import queue

# Update template folder path to the local directory
app = Flask(__name__, template_folder='templates')
command_queue = queue.Queue()

@app.route("/")
def home():
    """Serves the futuristic HUD dashboard."""
    return render_template("index.html")

@app.route("/command", methods=["POST"])
def command():
    """
    Endpoint for remote commands (e.g., from the Web HUD or Tasker).
    """
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    cmd = data.get("cmd")
    print(f"MAHI HUD Command: {cmd}")
    
    # Put the command into the queue for the AI loop to pick up
    command_queue.put(cmd)

    return jsonify({"status": "executed", "command": cmd})

def run_server():
    print("Remote HUD Server is running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    run_server()
