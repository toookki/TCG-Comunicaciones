"""
Repositorio de Bodega (Inventario Interno).
Abstrae el acceso a los datos persistentes del inventario privado (warehouse.json).
Es el único componente autorizado para leer, modificar y proteger mediante cerrojos
(locks) la concurrencia sobre dicho archivo.
"""

import json
import threading
import os

warehouse_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WAREHOUSE_PATH = os.path.join(BASE_DIR, "data", "warehouse.json")

def load_warehouse():
    with open(WAREHOUSE_PATH, "r") as f:
        return json.load(f)

def save_warehouse(warehouse):
    with open(WAREHOUSE_PATH, "w") as f:
        json.dump(warehouse, f, indent=4)

def add_to_warehouse(entry: dict):
    with warehouse_lock:
        warehouse = load_warehouse()
        new_id = max((w["id"] for w in warehouse), default=0) + 1
        entry["id"] = new_id
        warehouse.append(entry)
        save_warehouse(warehouse)
        return new_id

def remove_from_warehouse(entry_id: int):
    with warehouse_lock:
        warehouse = load_warehouse()
        found = next((w for w in warehouse if w["id"] == entry_id), None)
        if found:
            warehouse = [w for w in warehouse if w["id"] != entry_id]
            save_warehouse(warehouse)
        return found