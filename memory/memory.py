import json

FILE = "memory/memory.json"

def remember(key, value):
    try:
        data = json.load(open(FILE))
    except:
        data = {}

    data[key] = value
    json.dump(data, open(FILE, "w"))

def recall(key):
    try:
        data = json.load(open(FILE))
        return data.get(key, "No memory found")
    except:
        return "Memory error"