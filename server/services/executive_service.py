"""
Servicio del Ejecutivo (Operaciones).
Provee las funcionalidades para que los ejecutivos administren el negocio:
publicar, retirar o repreciar productos del catálogo, aprobar depósitos,
despachar órdenes o chatear con los clientes en espera.
"""

import datetime
import time

from server.repository.user_repository import load_users, save_users
from server.repository.catalogue_repository import load_catalogue, save_catalogue
from server.repository.order_repository import load_orders, save_orders, add_order
from server.repository.warehouse_repository import load_warehouse, save_warehouse, add_to_warehouse, remove_from_warehouse
from server.repository.deposit_repository import load_deposits, save_deposits
from server.utils.socket_utils import send, receive
from server.utils.server_state import (
    get_clients_snapshot, get_queue_snapshot, remove_from_queue,
    assign_client_to_executive, update_last_action
)
from server.utils.logger import log

def executive_status(conn, executive):
    clients = get_clients_snapshot()
    queue = get_queue_snapshot()
    log(f"Ejecutivo {executive['name']} consultó status.")
    lines = ["\n===== CLIENTES CONECTADOS ====="]
    for email, data in clients.items():
        lines.append(f"{email} - {data['name']}")
    lines.append(f"\nEsperando ejecutivo: {len(queue)}")
    for c in queue:
        lines.append(f"  [AVISO] {c['name']} quiere conectarse. Usa :connect.")
    lines.append("===============================\n")
    send(conn, "\n".join(lines))

def executive_details(conn, executive):
    clients = get_clients_snapshot()
    log(f"Ejecutivo {executive['name']} consultó detalles.")
    if not clients:
        send(conn, "\nNo hay clientes conectados.\n")
        return
    lines = ["\n===== DETALLES ====="]
    for email, data in clients.items():
        lines.append(f"{email} - {data['name']} - {data['last_action']}")
    lines.append("====================\n")
    send(conn, "\n".join(lines))

def executive_connect(conn, executive):
    queue = get_queue_snapshot()
    if not queue:
        send(conn, "\nNo hay clientes en espera.\n")
        return
    current_client = remove_from_queue(queue[0]["email"])
    assign_client_to_executive(executive["email"], current_client["email"])
    log(f"Cliente {current_client['name']} redirigido a ejecutivo {executive['name']}.")
    send(conn, f"\nConectado con {current_client['name']}.\n")
    send(current_client["conn"], f"\nEjecutivo {executive['name']} te está atendiendo.\n")
    chat_loop(conn, executive, current_client)
    current_client["ready_event"].set()

def executive_orders(conn, executive):
    log(f"Ejecutivo {executive['name']} consultó órdenes.")
    orders = load_orders()
    pagadas = [o for o in orders if o["type"] == "compra" and o["status"] == "Pagado"]
    enviadas = [o for o in orders if o["type"] == "compra" and o["status"] == "Enviado"]
    lines = ["\n===== ÓRDENES PENDIENTES DE ENVÍO ====="]
    if not pagadas:
        lines.append("Ninguna.")
    for o in pagadas:
        items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in o["items"])
        lines.append(f"#{o['id']} - {o['date']} - {o['client_email']} - {items_str} - ${o['total']}")
    lines.append("\n===== ÓRDENES EN TRÁNSITO =====")
    if not enviadas:
        lines.append("Ninguna.")
    for o in enviadas:
        items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in o["items"])
        lines.append(f"#{o['id']} - {o['date']} - {o['client_email']} - {items_str} - ${o['total']}")
    lines.append("================================\n")
    send(conn, "\n".join(lines))

def executive_catalogue(conn, executive):
    log(f"Ejecutivo {executive['name']} consultó catálogo.")
    catalogue = load_catalogue()
    lines = ["\n===== CATÁLOGO ====="]
    for item in catalogue:
        lines.append(f"[{item['id']}] {item['name']} - ${item['price']} - Stock: {item['stock']}")
    lines.append("====================\n")
    send(conn, "\n".join(lines))

def executive_warehouse(conn, executive):
    log(f"Ejecutivo {executive['name']} consultó bodega.")
    warehouse = load_warehouse()
    if not warehouse:
        send(conn, "\nNo hay cartas en bodega.\n")
        return
    lines = ["\n===== BODEGA ====="]
    for w in warehouse:
        lines.append(f"#{w['id']} - {w['card_name']} - ${w['price']} - {w['client_email']} - {w['date']}")
    lines.append("==================\n")
    send(conn, "\n".join(lines))

def executive_stockin(conn, executive, card_name, price):
    log(f"Ejecutivo {executive['name']} agregó {card_name} a bodega manualmente.")
    add_to_warehouse({
        "card_name": card_name,
        "price": price,
        "client_email": "manual",
        "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    })
    send(conn, f"\n{card_name} agregado a bodega a ${price}.\n")

def executive_deposits(conn, executive):
    log(f"Ejecutivo {executive['name']} consultó depósitos.")
    deposits = load_deposits()
    pending = [d for d in deposits if d["status"] == "Pendiente"]
    if not pending:
        send(conn, "\nNo hay depósitos pendientes.\n")
        return
    lines = ["\n===== DEPÓSITOS PENDIENTES ====="]
    for d in pending:
        lines.append(f"#{d['id']} - {d['client_name']} ({d['client_email']}) - ${d['amount']} - Código: {d['transfer_code']} - {d['date']}")
    lines.append("================================\n")
    send(conn, "\n".join(lines))

def executive_approve(conn, executive, deposit_id):
    deposits = load_deposits()
    deposit = next((d for d in deposits if d["id"] == deposit_id and d["status"] == "Pendiente"), None)
    if not deposit:
        send(conn, f"\nNo se encontró depósito #{deposit_id} pendiente.\n")
        return
    users = load_users()
    for u in users:
        if u["email"] == deposit["client_email"]:
            u["balance"] = u.get("balance", 0) + deposit["amount"]
            break
    save_users(users)
    deposit["status"] = "Aprobado"
    deposit["approved_date"] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    save_deposits(deposits)
    log(f"Ejecutivo {executive['name']} aprobó depósito #{deposit_id} de {deposit['client_name']}.")
    send(conn, f"\nDepósito #{deposit_id} aprobado. ${deposit['amount']} acreditados a {deposit['client_name']}.\n")

def executive_moveout(conn, executive, card_name):
    catalogue = load_catalogue()
    item_found = next((i for i in catalogue if i["name"].lower() == card_name.lower() and i["stock"] > 0), None)
    if not item_found:
        send(conn, f"\nNo se encontró '{card_name}' en catálogo con stock disponible.\n")
        return
    item_found["stock"] -= 1
    save_catalogue(catalogue)
    add_to_warehouse({
        "card_name": item_found["name"],
        "price": item_found["price"],
        "client_email": "manual",
        "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    })
    log(f"Ejecutivo {executive['name']} movió {card_name} del catálogo a bodega.")
    send(conn, f"\n{card_name} movido a bodega. Stock actualizado.\n")

def executive_reprice(conn, executive, card_name, new_price):
    catalogue = load_catalogue()
    item_found = next((i for i in catalogue if i["name"].lower() == card_name.lower()), None)
    if not item_found:
        send(conn, f"\nNo se encontró '{card_name}' en catálogo.\n")
        return
    old_price = item_found["price"]
    item_found["price"] = new_price
    save_catalogue(catalogue)
    log(f"Ejecutivo {executive['name']} cambió precio de {card_name} de ${old_price} a ${new_price}.")
    send(conn, f"\nPrecio de {card_name} actualizado de ${old_price} a ${new_price}.\n")

def executive_history(conn, client_email):
    users = load_users()
    for u in users:
        if u["email"] == client_email:
            history = u.get("history", [])
            if not history:
                send(conn, "\nNo hay historial del sistema registrado.\n")
                return
            lines = ["\n======= HISTORIAL DEL SISTEMA ======="]
            for i, h in enumerate(history):
                lines.append(f"[{i+1}] {h['date']} - {h['operation']}")
            lines.append("=====================================\n")
            send(conn, "\n".join(lines))
            return

def executive_operations(conn, client_conn, client_email):
    orders = load_orders()
    client_orders = [o for o in orders if o["client_email"] == client_email]
    if not client_orders:
        send(client_conn, "\nNo hay órdenes registradas.\n")
        return
    lines = ["\n======= TODAS TUS ÓRDENES ======="]
    for i, o in enumerate(client_orders):
        if o["type"] == "compra":
            items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in o["items"])
            lines.append(f"\n[{i+1}] Compra: {items_str} - ${o['total']}")
        else:
            lines.append(f"\n[{i+1}] Venta: {o['card_name']} - ${o['price']}")
        for s in o.get("status_history", [{"status": o["status"], "date": o["date"]}]):
            lines.append(f"  → {s['status']} ({s['date']})")
    lines.append("\n=================================\n")
    send(client_conn, "\n".join(lines))

def executive_buy(conn, client_conn, client_email, card_name, price):
    add_to_warehouse({
        "card_name": card_name,
        "price": price,
        "client_email": client_email,
        "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    })
    users = load_users()
    for u in users:
        if u["email"] == client_email:
            u["balance"] = u.get("balance", 0) + price
            break
    save_users(users)
    send(conn, f"\nCompra de {card_name} por ${price} registrada. Estado: En bodega.\n")
    send(client_conn, f"\nEl ejecutivo compró tu {card_name} por ${price}. Estado: En bodega.\n")

    users = load_users()
    for u in users:
        if u["email"] == client_email:
            u["balance"] = u.get("balance", 0) + price
            break
    save_users(users)

    send(conn, f"\nCompra de {card_name} por ${price} registrada. Estado: En bodega.\n")
    send(client_conn, f"\nEl ejecutivo compró tu {card_name} por ${price}. Estado: En bodega.\n")

# executive_publish — reemplazar búsqueda en orders por warehouse
def executive_publish(conn, card_name, price):
    warehouse = load_warehouse()
    entry_found = next(
        (w for w in warehouse if w["card_name"].lower() == card_name.lower()),
        None
    )
    if not entry_found:
        send(conn, f"\nNo se encontró '{card_name}' en bodega.\n")
        return

    remove_from_warehouse(entry_found["id"])

    catalogue = load_catalogue()
    for item in catalogue:
        if item["name"].lower() == card_name.lower():
            item["stock"] += 1
            item["price"] = price
            save_catalogue(catalogue)
            send(conn, f"\nStock de {card_name} actualizado a ${price}.\n")
            return
    new_id = max(item["id"] for item in catalogue) + 1
    catalogue.append({
        "id": new_id,
        "name": entry_found["card_name"],
        "price": price,
        "stock": 1
    })
    save_catalogue(catalogue)
    send(conn, f"\n{card_name} agregado al catálogo a ${price}.\n")

def executive_ship(conn, order_id):
    orders = load_orders()
    order_found = next(
        (o for o in orders if o["id"] == order_id and o["type"] == "compra" and o["status"] == "Pagado"),
        None
    )
    if not order_found:
        send(conn, f"\nNo se encontró orden #{order_id} en estado 'Pagado'.\n")
        return
    order_found["status"] = "Enviado"
    order_found.setdefault("status_history", []).append(
        {"status": "Enviado", "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
    )
    save_orders(orders)
    send(conn, f"\nOrden #{order_id} marcada como Enviado.\n")

def executive_returns(conn):
    orders = load_orders()
    pending = [o for o in orders if o["type"] == "compra" and o["status"] == "Devolución solicitada"]
    if not pending:
        send(conn, "\nNo hay devoluciones pendientes.\n")
        return
    lines = ["\n===== DEVOLUCIONES PENDIENTES ====="]
    for o in pending:
        items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in o["items"])
        lines.append(f"#{o['id']} - {o['date']} - {o['client_email']} - {items_str} - ${o['total']}")
    lines.append("===================================\n")
    send(conn, "\n".join(lines))

def executive_accept(conn, order_id):
    orders = load_orders()
    order_found = next(
        (o for o in orders if o["id"] == order_id and o["type"] == "compra" and o["status"] == "Devolución solicitada"),
        None
    )
    if not order_found:
        send(conn, f"\nNo se encontró orden #{order_id} con devolución solicitada.\n")
        return
    catalogue = load_catalogue()
    for it in order_found["items"]:
        for item in catalogue:
            if item["name"].lower() == it["name"].lower():
                item["stock"] += it["quantity"]
                break
    save_catalogue(catalogue)
    users = load_users()
    for u in users:
        if u["email"] == order_found["client_email"]:
            u["balance"] = u.get("balance", 0) + order_found["total"]
            break
    save_users(users)
    order_found["status"] = "Devolución aceptada"
    order_found.setdefault("status_history", []).append(
        {"status": "Devolución aceptada", "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
    )
    save_orders(orders)
    send(conn, f"\nDevolución #{order_id} aceptada. Saldo y stock actualizados.\n")


def chat_loop(conn, executive, current_client):
    client_conn = current_client["conn"]
    client_email = current_client["email"]

    while True:
        send(conn, f"\n{executive['name']} >")
        cmd = receive(conn)

        if cmd.startswith(":"):
            if cmd == ":disconnect":
                log(f"Ejecutivo {executive['name']} desconectó a {current_client['name']}.")
                send(conn, "\nChat terminado.\n")
                send(client_conn, "\nEl ejecutivo ha terminado la sesión. Volviendo al menú.\n")
                time.sleep(0.1)
                assign_client_to_executive(executive["email"], None)
                break

            elif cmd == ":history":
                log(f"Ejecutivo {executive['name']} consultó historial de {current_client['name']}.")
                executive_history(conn, client_email)

            elif cmd == ":operations":
                log(f"Ejecutivo {executive['name']} mostró operaciones a {current_client['name']}.")
                executive_operations(conn, client_conn, client_email)

            elif cmd.startswith(":buy"):
                parts = cmd.split()
                if len(parts) < 3:
                    send(conn, "\nUso: :buy [carta] [precio]\n")
                    continue
                try:
                    price = int(parts[-1])
                except:
                    send(conn, "\nPrecio inválido.\n")
                    continue
                card_name = " ".join(parts[1:-1])
                log(f"Ejecutivo {executive['name']} compró {card_name} a {current_client['name']} por ${price}.")
                executive_buy(conn, client_conn, client_email, card_name, price)

            else:
                send(conn, "\nComando inválido.\n")

        else:
            try:
                send(client_conn, f"\n{executive['name']}: {cmd}\n{current_client['name']} >")
                msg = receive(client_conn)
            except ConnectionError:
                send(conn, "\nEl cliente se desconectó abruptamente. Chat terminado.\n")
                assign_client_to_executive(executive["email"], None)
                break
            update_last_action(current_client["email"], f"Chat con ejecutivo: {msg[:30]}")
            log(f"Chat - {current_client['name']}: {msg}")
            send(conn, f"{current_client['name']}: {msg}\n")
