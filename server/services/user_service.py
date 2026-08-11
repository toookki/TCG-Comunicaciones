"""
Servicio de Cuenta de Usuario.
Gestiona la lógica de negocio relacionada con la cuenta individual de un cliente,
como la consulta de saldo, historial de acciones y el cambio de contraseñas.
"""

import datetime
from server.repository.user_repository import load_users, save_users
from server.repository.order_repository import load_orders
from server.utils.socket_utils import send, receive

def register_action(user_email, action):
    users = load_users()
    for u in users:
        if u["email"] == user_email:
            if "history" not in u:
                u["history"] = []
            u["history"].append({
                "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                "operation": action
            })
            break
    save_users(users)

def get_balance(user):
    users = load_users()
    for u in users:
        if u["email"] == user["email"]:
            user["balance"] = u["balance"]
            break
    return user.get("balance", 0)

def change_password(conn, user):
    send(conn, "\nIngrese nueva contraseña:")
    p1 = receive(conn)
    send(conn, "Confirme nueva contraseña:")
    p2 = receive(conn)

    if p1 != p2:
        send(conn, "\nLas contraseñas no coinciden.\n")
        return

    users = load_users()
    for u in users:
        if u["email"] == user["email"]:
            u["password"] = p1
            user["password"] = p1
            if "history" not in u:
                u["history"] = []
            u["history"].append({
                "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                "operation": "Cambio de contraseña"
            })
    save_users(users)
    send(conn, "\nContraseña actualizada exitosamente.\n")

def view_history(conn, user):
    orders = load_orders()
    current_year = datetime.datetime.now().year

    client_orders = [
        o for o in orders
        if o["client_email"] == user["email"]
        and datetime.datetime.strptime(o["date"].split()[0], "%d-%m-%Y").year >= current_year - 1
    ]

    register_action(user["email"], "Consulta de historial")

    if not client_orders:
        send(conn, "\nNo hay operaciones registradas en el último año.\n")
        return

    send(conn, "\n======= HISTORIAL DEL ÚLTIMO AÑO =======")
    for i, o in enumerate(client_orders):
        if o["type"] == "compra":
            items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in o["items"])
            send(conn, f"[{i+1}] {o['date']} - Compra: {items_str} - ${o['total']} - {o['status']}")
        else:
            send(conn, f"[{i+1}] {o['date']} - Venta: {o['card_name']} - ${o['price']} - {o['status']}")
    send(conn, "=========================================\n")