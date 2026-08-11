"""
Servicio de Depósitos.
Responsable de manejar las peticiones de los clientes para cargar fondos a
sus cuentas, registrando el depósito en estado pendiente para posterior
aprobación por parte de un ejecutivo.
"""

import datetime
from server.repository.deposit_repository import add_deposit
from server.utils.socket_utils import send, receive

def request_deposit(conn, user):
    send(conn, "\n===== DEPÓSITO DE SALDO =====")
    send(conn, "Ingrese el monto a depositar:")
    try:
        amount = int(receive(conn))
    except:
        send(conn, "\nMonto inválido.\n")
        return

    if amount <= 0:
        send(conn, "\nMonto inválido.\n")
        return

    send(conn, f"\nSimule una transferencia de ${amount} a la cuenta 12345678 del Banco TCG.")
    send(conn, "Ingrese el código de transferencia (cualquier texto):")
    transfer_code = receive(conn)

    add_deposit({
        "client_email": user["email"],
        "client_name": user["name"],
        "amount": amount,
        "transfer_code": transfer_code,
        "status": "Pendiente",
        "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    })

    send(conn, "\nSolicitud de depósito enviada. Un ejecutivo la aprobará pronto.\n")