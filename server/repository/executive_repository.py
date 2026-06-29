import json
import threading
import os

executives_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXECUTIVES_PATH = os.path.join(BASE_DIR, "data", "executives.json")

def load_executives():
    with open(EXECUTIVES_PATH, "r") as f:
        return json.load(f)

def save_executives(executives):
    with executives_lock:
        with open(EXECUTIVES_PATH, "w") as f:
            json.dump(executives, f, indent=4)