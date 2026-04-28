from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>FRIDAY Control Panel</h1>
    <form action="/send" method="post">
        <input name="cmd" placeholder="Enter command"/>
        <button type="submit">Send</button>
    </form>
    """

@app.route("/send", methods=["POST"])
def send():
    cmd = request.form["cmd"]
    
    print("Command from mobile:", cmd)

    # You can connect this to your main system
    return "Command Sent!"

app.run(host="0.0.0.0", port=8000)