import datetime

from repository.user_repository import load_users, save_users
from utils.socket_utils import send, receive

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
                "date": datetime.datetime.now().strftime("%d-%m-%Y"),
                "operation": "Cambio de contrasena"
            })

    save_users(users)
    send(conn, "\nContraseña actualizada exitosamente.\n")

def view_history(conn, user):
    users = load_users()

    for u in users:
        if u["email"] == user["email"]:
            history = u.get("history", [])

    if not history:
        send(conn, "\nNo hay operaciones registradas.\n")
        return

    send(conn, "\n======= HISTORIAL DE OPERACIONES =======")

    for i, h in enumerate(history):
        send(conn, f"[{i+1}] {h['date']} - {h['operation']}")

    send(conn, "========================================\n")