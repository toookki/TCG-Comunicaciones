from server.utils.socket_utils import send, receive
from server.repository.order_repository import load_orders, save_orders
import datetime

def get_client_orders(client_email):
    orders = load_orders()
    return [o for o in orders if o["client_email"] == client_email]

def confirm_received(conn, user):
    orders = load_orders()
    client_orders = [o for o in orders if o["client_email"] == user["email"] and o["type"] == "compra" and o["status"] == "Enviado"]

    if not client_orders:
        send(conn, "\nNo tienes compras en estado 'Enviado'.\n")
        return

    send(conn, "\n===== ÓRDENES ENVIADAS =====")
    for i, o in enumerate(client_orders):
        items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in o["items"])
        send(conn, f"[{i+1}] {o['date']} - {items_str} - ${o['total']}")
    send(conn, "============================\n")
    send(conn, "Ingrese número de orden a confirmar (0 para cancelar):")

    choice = receive(conn)

    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(client_orders):
            send(conn, "\nOpción inválida.\n")
            return
    except:
        send(conn, "\nOpción inválida.\n")
        return

    order_id = client_orders[idx]["id"]
    for o in orders:
        if o["id"] == order_id:
            o["status"] = "Recibido"
            o.setdefault("status_history", []).append(
                {"status": "Recibido", "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
            )
            break

    save_orders(orders)
    send(conn, "\nEnvío confirmado. ¡Gracias por tu compra!\n")

def request_return(conn, user):
    orders = load_orders()
    client_orders = [o for o in orders if o["client_email"] == user["email"] and o["type"] == "compra" and o["status"] == "Recibido"]

    if not client_orders:
        send(conn, "\nNo tienes compras en estado 'Recibido' para devolver.\n")
        return

    send(conn, "\n===== ÓRDENES RECIBIDAS =====")
    for i, o in enumerate(client_orders):
        items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in o["items"])
        send(conn, f"[{i+1}] {o['date']} - {items_str} - ${o['total']}")
    send(conn, "=============================\n")
    send(conn, "Ingrese número de orden a devolver (0 para cancelar):")

    choice = receive(conn)

    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(client_orders):
            send(conn, "\nOpción inválida.\n")
            return
    except:
        send(conn, "\nOpción inválida.\n")
        return

    order_id = client_orders[idx]["id"]
    for o in orders:
        if o["id"] == order_id:
            o["status"] = "Devolución solicitada"
            o.setdefault("status_history", []).append(
                {"status": "Devolución solicitada", "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
            )
            break

    save_orders(orders)
    send(conn, "\nSolicitud de devolución registrada.\n")