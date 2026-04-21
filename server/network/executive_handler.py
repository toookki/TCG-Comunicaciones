from server.utils.socket_utils import send, receive
from server.services.auth_service import authenticate_executive

def handle_executive(conn, addr):
    executive = None

    try:
        # LOGIN
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

        print(f"[SERVIDOR] Ejecutivo {executive['name']} conectado {addr}.")
        send(conn, f"\nBienvenido {executive['name']}!\n")

        executive_loop(conn, executive)

    except Exception as e:
        print("[ERROR EXECUTIVE HANDLER]", e)

    finally:
        conn.close()

        if executive:
            print(f"[SERVIDOR] Ejecutivo {executive['name']} desconectado {addr}.")
        else:
            print(f"[SERVIDOR] Ejecutivo {addr} desconectado.")

def executive_loop(conn, executive):
    return

    """ while True:

        send(conn, "\nComando:")

        cmd = receive(conn)

        if cmd == ":status":
            show_status(conn)

        elif cmd == ":details":
            show_details(conn)

        elif cmd == ":history":
            show_client_history(conn)

        elif cmd == ":operations":
            show_full_operations(conn)

        elif cmd.startswith(":buy"):
            process_buy(conn, cmd)

        elif cmd.startswith(":publish"):
            process_publish(conn, cmd)

        elif cmd == ":disconnect":
            disconnect_client(conn)

        elif cmd == ":exit":
            send(conn, "\nDesconectando...\n")
            break

        else:
            send(conn, "\nComando inválido.\n")

    print(f"[SERVIDOR] Ejecutivo {executive['email']} desconectado.")"""