"""
Controlador de sesión para usuarios tipo cliente.
Responsable de aislar la lógica de red e interacción de la sesión de un cliente,
gestionando su autenticación, presentando el menú de opciones interactivo, y
encaminando sus solicitudes hacia la capa de servicios correspondiente.
"""

import threading
from server.utils.socket_utils import send, receive
from server.utils.server_state import add_client, remove_client, update_last_action, add_to_queue, get_clients_snapshot, remove_from_queue
from server.utils.logger import log
from server.services.auth_service import authenticate
from server.services.user_service import change_password, view_history, get_balance, register_action
from server.services.shop_service import view_catalogue_buy
from server.services.order_service import confirm_received, request_return
from server.services.deposit_service import request_deposit

def handle_client(conn, addr):
    user = None
    is_duplicate = False 

    try:
        send(conn, "\n======= Bienvenido a TCG5 servicio al cliente =======")

        while user is None:
            send(conn, "Ingrese su email:")
            email = receive(conn)
            send(conn, "Ingrese su contraseña:")
            password = receive(conn)
            user = authenticate(email, password)
            if user is None:
                send(conn, "\nCredenciales incorrectas. Intente nuevamente.\n")

        clients = get_clients_snapshot()
        if user["email"] in clients:
            is_duplicate = True  # <- marcar
            send(conn, "\nEste usuario ya está conectado desde otro lado. Cerrando esta sesión.\n")
            conn.close()
            return

        add_client(user["email"], user["name"], conn)

        log(f"Cliente {user['name']} conectado {addr}.")
        send(conn, f"\nBienvenido {user['name']}!\n")

        while True:
            menu = (
                "================= MENÚ =================\n"
                "[1] Consultar saldo\n"
                "[2] Cambio de contraseña\n"
                "[3] Historial de operaciones\n"
                "[4] Catálogo de productos / Comprar\n"
                "[5] Solicitar devolución\n"
                "[6] Confirmar envío\n"
                "[7] Depositar saldo\n"
                "[8] Contactarse con un ejecutivo\n"
                "[9] Salir\n"
                "========================================\n"
            )
            send(conn, menu)
            send(conn, "Ingrese una opción:")
            option = receive(conn)

            if option == "1":
                update_last_action(user["email"], "Consultó saldo")
                log(f"Cliente {user['name']} consultó saldo.")
                balance = get_balance(user)
                send(conn, f"\nSu saldo actual es ${balance}\n")

            elif option == "2":
                update_last_action(user["email"], "Cambio de contraseña")
                log(f"Cambio clave cliente {user['name']}.")
                change_password(conn, user)

            elif option == "3":
                update_last_action(user["email"], "Consultó historial")
                log(f"Cliente {user['name']} consultó historial.")
                view_history(conn, user)

            elif option == "4":
                update_last_action(user["email"], "Consultó catálogo")
                log(f"Cliente {user['name']} consultó catálogo.")
                register_action(user["email"], "Consulta de catálogo")
                view_catalogue_buy(conn, user)

            elif option == "5":
                update_last_action(user["email"], "Solicitó devolución")
                log(f"Cliente {user['name']} solicitó devolución.")
                register_action(user["email"], "Solicitud de devolución")
                request_return(conn, user)

            elif option == "6":
                update_last_action(user["email"], "Confirmó recepción")
                log(f"Cliente {user['name']} confirmó recepción de envío.")
                register_action(user["email"], "Confirmación de recepción")
                confirm_received(conn, user)

            elif option == "7":
                update_last_action(user["email"], "Solicitó depósito")
                log(f"Cliente {user['name']} solicitó depósito.")
                register_action(user["email"], "Solicitud de depósito")
                request_deposit(conn, user)

            elif option == "8":
                update_last_action(user["email"], "Esperando ejecutivo")
                log(f"Cliente {user['name']} solicitó contacto con ejecutivo.")
                register_action(user["email"], "Derivación a ejecutivo")
                ready_event = threading.Event()
                client_gone_event = threading.Event()
                add_to_queue(user["email"], user["name"], conn, ready_event, client_gone_event)
                send(conn, "\nEsperando a un ejecutivo disponible...\n")
                connected = ready_event.wait(timeout=300)
                if not connected:
                    send(conn, "\nNo hay ejecutivos disponibles. Volviendo al menú.\n")
                    client_gone_event.set()
                    remove_from_queue(user["email"])

            elif option == "9":
                send(conn, "\nDesconectando...")
                break

            else:
                send(conn, "\nOpción inválida.\n")

    except Exception as e:
        log(f"Error en cliente {addr}: {e}")

    finally:
        if user and not is_duplicate:  # <- solo si no es duplicado
            remove_client(user["email"])
            log(f"Cliente {user['name']} desconectado {addr}.")
        elif not user:
            log(f"Cliente desconocido desconectado {addr}.")
        conn.close()