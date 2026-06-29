import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_PATH = os.path.join(BASE_DIR, "server.log")

def log(message):
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    full_message = f"[{timestamp}] [SERVIDOR] {message}"
    print(full_message)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")