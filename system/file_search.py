import os

def find_file(name):
    for root, dirs, files in os.walk("C:\\"):
        if name in files:
            return os.path.join(root, name)
    return "File not found"