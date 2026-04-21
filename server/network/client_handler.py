from server.utils.socket_utils import send, receive
from server.services.auth_service import authenticate
from server.services.user_service import change_password, view_history
from server.services.shop_service import view_catalogue_buy

def handle_client(conn, addr):
    user = None

    try:
        send(conn, "\n======= Bienvenido a TCG5 servicio al cliente =======")

        # LOGIN
        while user is None:
            send(conn, "Ingrese su email:")
            email = receive(conn)

            send(conn, "Ingrese su contraseña:")
            password = receive(conn)

            user = authenticate(email, password)

            if user is None:
                send(conn, "\nCredenciales incorrectas. Intente nuevamente.\n")

        print(f"[SERVIDOR] Cliente {user['name']} conectado {addr}.")
        send(conn, f"\nBienvenido {user['name']}!\n")

        # MENU PRINCIPAL
        while True:
            menu = (
                "================= MENÚ =================\n"
                "[1] Consultar saldo\n"
                "[2] Cambio de contraseña\n"
                "[3] Historial de operaciones\n"
                "[4] Catálogo de productos / Comprar\n"
                "[5] Solicitar devolución\n"
                "[6] Confirmar envío\n"
                "[7] Contactarse con un ejecutivo\n"
                "[8] Salir\n"
                "========================================\n"
            )

            send(conn, menu)
            send(conn, "Ingrese una opción:")

            option = receive(conn)

            if option == "1":
                send(conn, f"\nSu saldo actual es ${user.get('balance', 0)}\n")

            elif option == "2":
                change_password(conn, user)

            elif option == "3":
                view_history(conn, user)

            elif option == "4":
                view_catalogue_buy(conn, user)

            elif option == "5":
                send(conn, "\nSolicitud de devolución registrada.\n")

            elif option == "6":
                send(conn, "\nEnvío confirmado.\n")

            elif option == "7":
                send(conn, "\nSolicitud enviada. Espere a un ejecutivo.\n")

            elif option == "8":
                send(conn, "\nDesconectando...")
                break

            else:
                send(conn, "\nOpción inválida.\n")

    except Exception as e:
        print("[ERROR CLIENT HANDLER]", e)

    finally:
        conn.close()

        if user:
            print(f"[SERVIDOR] Cliente {user['name']} desconectado {addr}.")
        else:
            print(f"[SERVIDOR] Cliente {addr} desconectado.")