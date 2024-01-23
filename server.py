import socket
from threading import Thread
import logging


class Server:
    def __init__(self):
        self.HOST = '192.168.1.4'
        self.PORT = 7777
        self.clients = set()

    def listening_client(self, socket):
        username = socket.recv(4096).decode('utf-8')
        clients = self.clients.copy()
        for client in clients:
            try:
                client.send(
                    f'*{username} присоединился к чату*\n'.encode('utf-8')
                    )
            except ConnectionResetError:
                logging.warning(f'connection with {client} has been lost')
        while True:
            try:
                message = socket.recv(4096).decode('utf-8')
                message = message.replace('\n', '\n   ')
                for client in self.clients:
                    client.send(f'{username}: {message}\n'.encode('utf-8'))
            except ConnectionResetError:
                socket.close()
                self.clients.remove(socket)
                break

    def start_listening(self):
        self.session.listen()
        logging.info('server started')
        while True:
            client_socket, client_address = self.session.accept()
            self.clients.add(client_socket)
            client_session = Thread(
                target=self.listening_client,
                args=(client_socket,),
                daemon=True)
            client_session.start()

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.session:
            try:
                self.session.bind((self.HOST, self.PORT))
                self.start_listening()
            except OSError:
                print(f'invalid host format: {self.HOST}')
                logging.warning(f'invalid host format: {self.HOST}')
            except OverflowError:
                print(f'invalid port format: {self.HOST}')
                logging.warning(f'invalid port format: {self.HOST}')


logging.basicConfig(level=logging.INFO, filename="ServerLogs.log",
                    filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

Server().start_server()
