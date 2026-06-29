HEADER_SIZE = 8  # 8 bytes para indicar el largo del mensaje

def send(conn, msg):
    data = (msg + "\n").encode("utf-8")
    length = str(len(data)).zfill(HEADER_SIZE).encode("utf-8")
    conn.sendall(length + data)

def receive(conn):
    # Primero leer el header con el largo
    header = b""
    while len(header) < HEADER_SIZE:
        chunk = conn.recv(HEADER_SIZE - len(header))
        if not chunk:
            raise ConnectionError("Cliente desconectado.")
        header += chunk

    msg_length = int(header.decode("utf-8"))

    # Luego leer exactamente esa cantidad de bytes
    data = b""
    while len(data) < msg_length:
        chunk = conn.recv(min(4096, msg_length - len(data)))
        if not chunk:
            raise ConnectionError("Cliente desconectado.")
        data += chunk

    return data.decode("utf-8").strip()