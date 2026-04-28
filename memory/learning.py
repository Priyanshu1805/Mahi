import json
from datetime import datetime
import os

FILE = "memory/habits.json"

def log_action(action):
    """
    Logs a user action with a timestamp to learn habits over time.
    """
    try:
        if os.path.exists(FILE):
            with open(FILE, "r") as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []

    data.append({
        "action": action,
        "time": str(datetime.now())
    })

    try:
        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving habit: {e}")

def suggest():
    """
    Suggests actions based on logged habits.
    """
    try:
        if not os.path.exists(FILE):
            return "Learning your habits..."
            
        with open(FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return "No habits found yet."

    if len(data) > 5:
        # Simple logic: suggest the last action
        return f"Based on your habits, you might want to: {data[-1]['action']}"
    
    return "Still learning your routine. Keep using the system!"
