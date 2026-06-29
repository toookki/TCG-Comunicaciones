import threading

connected_clients = {}
clients_lock = threading.Lock()

executive_queue = []
queue_lock = threading.Lock()

connected_executives = {}
executives_lock = threading.Lock()


def add_client(email, name, conn):
    with clients_lock:
        connected_clients[email] = {
            "name": name,
            "conn": conn,
            "last_action": "Conectado"
        }

def remove_client(email):
    with clients_lock:
        connected_clients.pop(email, None)

def update_last_action(email, action):
    with clients_lock:
        if email in connected_clients:
            connected_clients[email]["last_action"] = action


def add_to_queue(email, name, conn, ready_event, client_gone_event):
    with queue_lock:
        executive_queue.append({
            "email": email,
            "name": name,
            "conn": conn,
            "ready_event": ready_event,
            "client_gone_event": client_gone_event
        })
    notify_executives(name)

def remove_from_queue(email):
    with queue_lock:
        for i, client in enumerate(executive_queue):
            if client["email"] == email:
                return executive_queue.pop(i)
    return None

def get_queue_snapshot():
    with queue_lock:
        return list(executive_queue)

def notify_executives(client_name):
    from server.utils.socket_utils import send as socket_send
    with executives_lock:
        for exec_data in connected_executives.values():
            if exec_data.get("current_client") is not None:  # <- agregar esta línea
                continue                                      # <- y esta
            try:
                socket_send(exec_data["conn"], f"\n[AVISO] {client_name} quiere conectarse. Usa :connect.")
            except:
                pass


def add_executive(email, name, conn):
    with executives_lock:
        connected_executives[email] = {
            "name": name,
            "conn": conn,
            "current_client": None
        }

def remove_executive(email):
    with executives_lock:
        connected_executives.pop(email, None)

def assign_client_to_executive(executive_email, client_email):
    with executives_lock:
        if executive_email in connected_executives:
            connected_executives[executive_email]["current_client"] = client_email

def get_clients_snapshot():
    with clients_lock:
        return dict(connected_clients)

def get_executives_snapshot():
    with executives_lock:
        return dict(connected_executives)