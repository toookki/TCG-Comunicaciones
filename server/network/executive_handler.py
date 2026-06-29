from server.utils.socket_utils import send, receive
from server.utils.server_state import add_executive, remove_executive, get_clients_snapshot, get_executives_snapshot
from server.utils.logger import log
from server.services.auth_service import authenticate_executive
from server.services.executive_service import (
    executive_status, executive_details, executive_connect,
    executive_catalogue, executive_orders, executive_ship,
    executive_publish, executive_warehouse, executive_stockin,
    executive_returns, executive_accept, executive_deposits,
    executive_approve, executive_moveout, executive_reprice
)

def handle_executive(conn, addr):
    executive = None

    try:
        while executive is None:
            send(conn, "Ingrese su email:")
            email = receive(conn)
            send(conn, "Ingrese su contraseña:")
            password = receive(conn)
            send(conn, "Ingrese su codigo 2FA:")
            code = receive(conn)
            executive = authenticate_executive(email, password, code)
            if executive is None:
                send(conn, "\nCredenciales incorrectas. Intente nuevamente.\n")

        executives = get_executives_snapshot()
        if executive["email"] in executives:
            send(conn, "\nEste ejecutivo ya está conectado. Cerrando esta sesión.\n")
            conn.close()
            return

        add_executive(executive["email"], executive["name"], conn)
        clients = get_clients_snapshot()
        log(f"Ejecutivo {executive['name']} conectado {addr}.")
        send(conn, f"\nBienvenido {executive['name']}! Hay {len(clients)} clientes conectados.\n")

        executive_loop(conn, executive)

    except Exception as e:
        log(f"Error en ejecutivo {addr}: {e}")

    finally:
        if executive:
            remove_executive(executive["email"])
            log(f"Ejecutivo {executive['name']} desconectado {addr}.")
        else:
            log(f"Ejecutivo desconocido desconectado {addr}.")
        conn.close()


def executive_loop(conn, executive):
    while True:
        send(conn, "\nComando:")
        cmd = receive(conn)

        if not cmd.startswith(":"):
            send(conn, "\nDebes ingresar un comando.\n")
            continue

        if cmd == ":status":
            executive_status(conn, executive)

        elif cmd == ":details":
            executive_details(conn, executive)

        elif cmd == ":connect":
            executive_connect(conn, executive)

        elif cmd == ":catalogue":
            executive_catalogue(conn, executive)

        elif cmd == ":orders":
            executive_orders(conn, executive)

        elif cmd.startswith(":ship"):
            parts = cmd.split()
            if len(parts) < 2:
                send(conn, "\nUso: :ship [order_id]\n")
                continue
            try:
                order_id = int(parts[1])
            except:
                send(conn, "\nID inválido.\n")
                continue
            executive_ship(conn, order_id)

        elif cmd.startswith(":publish"):
            parts = cmd.split()
            if len(parts) < 3:
                send(conn, "\nUso: :publish [carta] [precio]\n")
                continue
            try:
                price = int(parts[-1])
            except:
                send(conn, "\nPrecio inválido.\n")
                continue
            card_name = " ".join(parts[1:-1])
            executive_publish(conn, card_name, price)

        elif cmd == ":warehouse":
            executive_warehouse(conn, executive)

        elif cmd.startswith(":stockin"):
            parts = cmd.split()
            if len(parts) < 3:
                send(conn, "\nUso: :stockin [carta] [precio]\n")
                continue
            try:
                price = int(parts[-1])
            except:
                send(conn, "\nPrecio inválido.\n")
                continue
            card_name = " ".join(parts[1:-1])
            executive_stockin(conn, executive, card_name, price)

        elif cmd == ":returns":
            executive_returns(conn)

        elif cmd.startswith(":accept"):
            parts = cmd.split()
            if len(parts) < 2:
                send(conn, "\nUso: :accept [order_id]\n")
                continue
            try:
                order_id = int(parts[1])
            except:
                send(conn, "\nID inválido.\n")
                continue
            executive_accept(conn, order_id)

        elif cmd == ":deposits":
            executive_deposits(conn, executive)

        elif cmd.startswith(":approve"):
            parts = cmd.split()
            if len(parts) < 2:
                send(conn, "\nUso: :approve [deposit_id]\n")
                continue
            try:
                deposit_id = int(parts[1])
            except:
                send(conn, "\nID inválido.\n")
                continue
            executive_approve(conn, executive, deposit_id)

        elif cmd.startswith(":moveout"):
            parts = cmd.split()
            if len(parts) < 2:
                send(conn, "\nUso: :moveout [carta]\n")
                continue
            card_name = " ".join(parts[1:])
            executive_moveout(conn, executive, card_name)

        elif cmd.startswith(":reprice"):
            parts = cmd.split()
            if len(parts) < 3:
                send(conn, "\nUso: :reprice [carta] [nuevo_precio]\n")
                continue
            try:
                new_price = int(parts[-1])
            except:
                send(conn, "\nPrecio inválido.\n")
                continue
            card_name = " ".join(parts[1:-1])
            executive_reprice(conn, executive, card_name, new_price)

        elif cmd == ":exit":
            log(f"Ejecutivo {executive['name']} se desconectó.")
            send(conn, "\nDesconectando...\n")
            break

        else:
            send(conn, "\nComando inválido.\n")