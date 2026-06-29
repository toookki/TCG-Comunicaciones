import socket
import threading

from server.network.client_handler import handle_client
from server.network.executive_handler import handle_executive
from server.utils.socket_utils import send, receive

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 1024

class ChatServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"[SERVIDOR] Escuchando en {self.host}:{self.port}.")

        while True:
            conn, addr = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_connection, args=(conn, addr), daemon=True)
            thread.start()

    def handle_connection(self, conn, addr):
            while True:
                send(conn, "¿Tipo de usuario? (client/executive)")
                role = receive(conn)
                if role == "client":
                    handle_client(conn, addr)
                    break
                elif role == "executive":
                    handle_executive(conn, addr)
                    break
                else:
                    send(conn, "Tipo inválido, intente nuevamente.")

if __name__ == "__main__":
    server = ChatServer(HOST, PORT)
    server.start()