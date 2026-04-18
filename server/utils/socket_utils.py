BUFFER_SIZE = 1024

def send(conn, msg):
    conn.send((msg + "\n").encode())

def receive(conn):
    data = conn.recv(BUFFER_SIZE)
    if not data:
        raise ConnectionError("Cliente desconectado.")
    return data.decode().strip()