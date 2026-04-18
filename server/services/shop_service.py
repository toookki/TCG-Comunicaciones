import datetime

from repository.user_repository import load_users, save_users
from repository.catalogue_repository import load_catalogue, save_catalogue
from utils.socket_utils import send, receive

def view_catalogue_buy(conn, user):
    try:
        catalogue = load_catalogue()
        users = load_users()

        # buscar usuario persistente
        current_user = None
        for u in users:
            if u["email"] == user["email"]:
                current_user = u
                break

        if current_user is None:
            send(conn, "Usuario no encontrado.")
            return

        cart = []

        # FASE 1: CONSTRUCCIÓN DEL CARRITO
        while True:
            send(conn, "\n========== CATÁLOGO ==========")

            for item in catalogue:
                send(conn, f"[{item['id']}] {item['name']} - ${item['price']} - Stock: {item['stock']}")

            send(conn, "================================\n")
            send(conn, f"Saldo disponible: ${current_user.get('balance', 0)}")

            send(conn, "\nIngrese ID del producto (0 para finalizar selección):")
            product_id = receive(conn)

            if product_id == "0":
                break

            product = None

            for item in catalogue:
                if str(item["id"]) == product_id:
                    product = item
                    break

            if product is None:
                send(conn, "\nProducto inválido.\n")
                continue

            send(conn, "¿Cuántas unidades desea agregar?")

            try:
                quantity = int(receive(conn))
            except:
                send(conn, "Cantidad inválida.")
                continue

            if quantity <= 0:
                send(conn, "Cantidad inválida.")
                continue

            already_in_cart = sum(
                item["quantity"] for item in cart
                if item["product"]["id"] == product["id"]
            )

            if already_in_cart + quantity > product["stock"]:
                send(conn, "\nStock insuficiente considerando lo ya agregado al carrito.")
                continue

            cart.append({
                "product": product,
                "quantity": quantity
            })

            send(conn, "Producto agregado al carrito.")
            send(conn, "¿Desea comprar algo más? (s/n)")
            more = receive(conn).lower()

            if more != "s":
                break

        # FASE 2: CHECKOUT
        if not cart:
            send(conn, "\nNo se agregaron productos.\n")
            return

        send(conn, "\n========== RESUMEN DE COMPRA ==========")

        total = 0

        for item in cart:

            p = item["product"]
            q = item["quantity"]
            subtotal = p["price"] * q
            total += subtotal

            send(conn, f"{p['name']} x{q} = ${subtotal}")

        send(conn, "=======================================\n")
        send(conn, f"TOTAL: ${total}")

        if current_user.get("balance", 0) < total:
            send(conn, "\nSaldo insuficiente. Compra cancelada.\n")
            return

        send(conn, "¿Confirmar compra? (s/n)")
        confirm = receive(conn).lower()

        if confirm != "s":
            send(conn, "\nCompra cancelada.\n")
            return

        # FASE 3: APLICAR COMPRA
        for item in cart:
            product = item["product"]
            quantity = item["quantity"]

            product["stock"] -= quantity

        current_user["balance"] -= total
        user["balance"] = current_user["balance"]

        current_user["history"].append({
            "date": datetime.datetime.now().strftime("%d-%m-%Y"),
            "operation": f"Compra multiple por ${total}"
        })

        save_users(users)
        save_catalogue(catalogue)

        send(conn, "\nCompra realizada con éxito.\n")

    except Exception as e:

        print("[ERROR CART]", e)
        send(conn, "Error en el sistema de compra.")