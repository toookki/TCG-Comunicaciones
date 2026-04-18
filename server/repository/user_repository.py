import json
import threading
import os

users_lock = threading.Lock()
executives_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")
EXECUTIVES_PATH = os.path.join(BASE_DIR, "data", "executives.json")

def load_users():
    with open(USERS_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with users_lock:
        with open(USERS_PATH, "w") as f:
            json.dump(users, f, indent=4)

def load_executives():
    with open(EXECUTIVES_PATH, "r") as f:
        return json.load(f)
    
def save_executives(users):
    with executives_lock:
        with open(EXECUTIVES_PATH, "w") as f:
            json.dump(users, f, indent=4)