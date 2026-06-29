import socket
import getpass
import select

HOST = "127.0.0.1"
PORT = 5000
HEADER_SIZE = 8

def recv_msg(sock):
    header = b""
    while len(header) < HEADER_SIZE:
        chunk = sock.recv(HEADER_SIZE - len(header))
        if not chunk:
            return None
        header += chunk
    msg_length = int(header.decode("utf-8"))
    data = b""
    while len(data) < msg_length:
        chunk = sock.recv(min(4096, msg_length - len(data)))
        if not chunk:
            return None
        data += chunk
    return data.decode("utf-8")

def send_msg(sock, text):
    data = (text + "\n").encode("utf-8")
    length = str(len(data)).zfill(HEADER_SIZE).encode("utf-8")
    sock.sendall(length + data)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

waiting = False

while True:
    try:
        readable, _, _ = select.select([client], [], [], 0.5)
        if not readable:
            continue

        msg = recv_msg(client)
        if not msg:
            print("Servidor desconectado.")
            break

        print(msg, end="", flush=True)

        last_line = msg.strip().split("\n")[-1].lower()

        if "esperando a un ejecutivo" in last_line:
            waiting = True
            continue

        if waiting:
            waiting = False

        if msg.strip().endswith(":") or msg.strip().endswith("?") or msg.strip().endswith(")") or msg.strip().endswith(">"):
            if "ejecutivo ha terminado" in msg.lower():
                continue
            if "contraseña" in last_line or "2fa" in last_line:
                data = getpass.getpass("")
            else:
                data = input("")
            send_msg(client, data)

    except Exception as e:
        print(f"Desconectado: {e}")
        break

client.close()