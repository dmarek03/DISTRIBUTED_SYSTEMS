from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SO_REUSEADDR,SOL_SOCKET,SO_RCVBUF
from threading import Thread
from dataclasses import dataclass
from enum import Enum
import argparse


@dataclass
class CommunicationProtocol(Enum):
    TCP = 'TCP'
    UDP = 'UDP'
    MCT = 'MCT'


@dataclass
class Server:
    server_port: int
    server_address: str
    clients = {}
    server_tcp_socket = None
    server_udp_socket = None

    def init_connection(self) -> None:
        self.server_tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.server_tcp_socket.bind((self.server_address, self.server_port))
        self.server_tcp_socket.listen(5)
        print("Server TCP is waiting for connections ...")

        self.server_udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_udp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_udp_socket.setsockopt(SOL_SOCKET, SO_RCVBUF, 1024 * 1024)
        self.server_udp_socket.bind((self.server_address, self.server_port))

        print("Server UDP is waiting for connection ...")

    def broadcast(self, sender_name, message, communication_protocol: CommunicationProtocol):

        match communication_protocol:
            case CommunicationProtocol.TCP:

                for client_name, client_socket in self.clients.items():
                    if sender_name != client_name:
                        client_socket.send(bytes(message, 'utf-8'))

            case CommunicationProtocol.UDP:

                for client_name, client_socket in self.clients.items():
                    if sender_name != client_name:
                        self.server_udp_socket.sendto(bytes(message, 'utf-8'), client_socket.getpeername())

            case _:
                print('Error')

    def listen(self) -> None:
        self.init_connection()

        udp_thread = Thread(target=self.handle_udp_client, daemon=True)
        udp_thread.start()

        while True:
            client_socket, address = self.server_tcp_socket.accept()
            print(f'Connection from: {address}')

            tcp_thread = Thread(target=self.handle_tcp_client, args=(client_socket,), daemon=True)
            tcp_thread.start()

    def handle_tcp_client(self, client_socket):

        client_name = self.register_client(client_socket)

        client_socket = self.clients[client_name]
        while True:
            try:
                received_message = str(client_socket.recv(1024), 'utf-8')

                if not received_message or received_message == 'bye':

                    self.broadcast(client_name, f'\033[31m[server]: {client_name} has already left the chat\033[0m', CommunicationProtocol.TCP)
                    break
                else:

                    self.broadcast(client_name, client_name + ':' + received_message, CommunicationProtocol.TCP)

            except Exception as e:
                print(f'Error in client handling: {e}')
                break

        self.clients.pop(client_name)
        self.broadcast(
            client_name,
            f'\033[31m[server]: {client_name} has already left the chat\033[0m',
            CommunicationProtocol.TCP
            )
        client_socket.close()
        print(f'Connection with {client_name} was closed')

    def handle_udp_client(self):

        while True:
            try:
                received_message, address = self.server_udp_socket.recvfrom(5000)
                received_message = str(received_message, 'utf-8')

                client_name = [c_name for c_name, c_address in self.clients.items() if address == c_address.getpeername()]
                client_name = client_name[0] if client_name else None
                if not client_name:
                    print(f'UDP message from unknown client:{received_message}')
                    continue

                else:

                    self.broadcast(client_name, client_name + ":" + received_message,  CommunicationProtocol.UDP)

            except Exception as e:
                print(f'Error in handling udp client: {e}')
                break
        self.server_udp_socket.close()

    def register_client(self, client):
        client.send(bytes("\033[32m[server]: Welcome! Please choose your nickname:\033[0m", 'utf-8'))
        while True:
            try:
                client_name = str(client.recv(1024), 'utf-8')

                if client_name in ['server', 'address', 'port']:
                    client.send(
                        bytes(
                            '\033[31m[server]:This nickname is not allowed! Choose another nickname:\033[0m', 'utf-8'
                        )
                    )

                    continue

                if not client_name:
                    client.send(
                        bytes("\033[31m[server]:Nickname can not be empty! Choose another nickname:\033[0m",  'utf-8')
                    )
                    continue

                if self.clients.get(client_name):
                    client.send(
                        bytes("\033[31m[server]:This nickname is taken ! Choose another nickname:\033[0m",  'utf-8')
                    )
                    continue
                else:
                    client.send(
                        bytes(
                            f"\033[32m[server]:Your nickname:[{client_name}] was registered correctly!\033[0m", 'utf-8'
                        )
                    )
                    self.broadcast(
                        client_name,
                        f'\033[32m[server]:{client_name} has just joined the chat\033[0m',
                        CommunicationProtocol.TCP
                    )
                    self.clients[client_name] = client
                    return client_name

            except Exception as e:
                print(f'Error during client registration: {e}')
                break


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='server_port', type=int, help='Add server port')
    parser.add_argument('-a', dest='server_address', type=str, help='Add server address')
    args = parser.parse_args()

    server_port = args.server_port
    server_address = args.server_address

    server = Server(server_port=server_port, server_address=server_address)
    server.listen()


if __name__ == '__main__':
    main()
