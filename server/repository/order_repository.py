"""
Repositorio de Órdenes.
Abstrae el acceso a los datos persistentes de órdenes de compra (orders.json).
Es el único componente autorizado para leer, modificar y proteger mediante cerrojos
(locks) la concurrencia sobre dicho archivo.
"""

import json
import threading
import os

orders_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDERS_PATH = os.path.join(BASE_DIR, "data", "orders.json")

def load_orders():
    with open(ORDERS_PATH, "r") as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_PATH, "w") as f:
        json.dump(orders, f, indent=4)

def add_order(new_order_data: dict):
    with orders_lock:
        orders = load_orders()
        new_id = max((o["id"] for o in orders), default=0) + 1
        new_order_data["id"] = new_id
        orders.append(new_order_data)
        save_orders(orders)
        return new_id