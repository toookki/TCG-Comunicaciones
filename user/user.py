import socket
import getpass

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

buffer = ""

while True:

    msg = client.recv(1024).decode()

    if not msg:
        print("Servidor desconectado.")
        break

    print(msg, end="")

    if msg.strip().endswith(":") or msg.strip().endswith("?") or msg.strip().endswith(")"):
        last_line = msg.strip().split("\n")[-1].lower()

        if "contraseña" in last_line or "2fa" in last_line:
            data = getpass.getpass("> ")
        else:
            data = input("> ")

        client.sendall((data + "\n").encode())