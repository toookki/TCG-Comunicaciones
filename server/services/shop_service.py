import datetime
from server.repository.user_repository import load_users, save_users
from server.repository.catalogue_repository import load_catalogue, save_catalogue, get_catalogue_lock
from server.repository.order_repository import load_orders, add_order
from server.utils.socket_utils import send, receive
from server.utils.logger import log

catalogue_lock = get_catalogue_lock()

def view_catalogue_buy(conn, user):
    try:
        catalogue = load_catalogue()
        users = load_users()

        current_user = None
        for u in users:
            if u["email"] == user["email"]:
                current_user = u
                break

        if current_user is None:
            send(conn, "Usuario no encontrado.")
            return

        cart = []

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

            if product["stock"] == 0:
                send(conn, "\nEse producto está agotado.\n")
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

            cart.append({"product": product, "quantity": quantity})
            send(conn, "Producto agregado al carrito.")
            send(conn, "¿Desea comprar algo más? (s/n)")
            more = receive(conn).lower()

            if more != "s":
                break

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

        with catalogue_lock:
            catalogue = load_catalogue()

            for item in cart:
                product_id = item["product"]["id"]
                for cat_item in catalogue:
                    if cat_item["id"] == product_id:
                        if cat_item["stock"] < item["quantity"]:
                            send(conn, f"\nStock insuficiente para {cat_item['name']} al momento de confirmar. Compra cancelada.\n")
                            return
                        break

            for item in cart:
                for cat_item in catalogue:
                    if cat_item["id"] == item["product"]["id"]:
                        cat_item["stock"] -= item["quantity"]
                        break

            save_catalogue(catalogue)

        order_items = [
            {"name": item["product"]["name"], "quantity": item["quantity"], "price": item["product"]["price"]}
            for item in cart
        ]

        current_user["balance"] -= total
        user["balance"] = current_user["balance"]
        save_users(users)

        add_order({
            "type": "compra",
            "client_email": user["email"],
            "items": order_items,
            "total": total,
            "status": "Pagado",
            "status_history": [
                {"status": "Pagado", "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
            ],
            "date": datetime.datetime.now().strftime("%d-%m-%Y")
        })

        send(conn, "\nCompra realizada con éxito.\n")
        items_str = ", ".join(f"{it['name']} x{it['quantity']}" for it in order_items)
        log(f"Cliente {user['name']} compró: {items_str} por ${total}.")

    except Exception as e:
        print("[ERROR CART]", e)
        send(conn, "Error en el sistema de compra.")