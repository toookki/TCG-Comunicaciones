import json
import threading
import os

users_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")

def load_users():
    with open(USERS_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with users_lock:
        with open(USERS_PATH, "w") as f:
            json.dump(users, f, indent=4)