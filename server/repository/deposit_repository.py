"""
Repositorio de Depósitos.
Abstrae el acceso a los datos persistentes de los depósitos de fondos (deposits.json).
Es el único componente autorizado para leer, modificar y proteger mediante cerrojos
(locks) la concurrencia sobre dicho archivo.
"""

import json
import threading
import os

deposits_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEPOSITS_PATH = os.path.join(BASE_DIR, "data", "deposits.json")

def load_deposits():
    if not os.path.exists(DEPOSITS_PATH):
        return []
    with open(DEPOSITS_PATH, "r") as f:
        return json.load(f)

def save_deposits(deposits):
    with open(DEPOSITS_PATH, "w") as f:
        json.dump(deposits, f, indent=4)

def add_deposit(deposit_data: dict):
    with deposits_lock:
        deposits = load_deposits()
        new_id = max((d["id"] for d in deposits), default=0) + 1
        deposit_data["id"] = new_id
        deposits.append(deposit_data)
        save_deposits(deposits)
        return new_id