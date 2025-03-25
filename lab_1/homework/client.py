import argparse
import sys
from socket import (
    socket, inet_aton, AF_INET, SOCK_STREAM, SOCK_DGRAM, SO_REUSEADDR,
    SOL_SOCKET, INADDR_ANY, IP_MULTICAST_TTL, IPPROTO_IP, IP_ADD_MEMBERSHIP,
)
from struct import pack
from ascii_art import computer, cs_go_logo, dog
import threading
from dataclasses import dataclass
import re


@dataclass
class Client:
    server_port: int
    server_address: str
    multicast_port: int
    multicast_address: str
    name: str = None
    client_tcp_socket = None
    client_udp_socket = None
    client_multicast_socket = None
    choosing_nickname_running: bool = True
    running: bool = True

    def init_socket(self):
        self.client_tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.client_tcp_socket.connect((self.server_address, self.server_port))

        tcp_local_port = self.client_tcp_socket.getsockname()[1]

        self.client_udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_udp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.client_udp_socket.bind(('', tcp_local_port))
        self.client_udp_socket.connect((self.server_address, self.server_port))

        self.client_multicast_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_multicast_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.client_multicast_socket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 32)
        self.client_multicast_socket.bind(('', self.multicast_port))

        mreq = pack('4sl', inet_aton(self.multicast_address), INADDR_ANY)
        self.client_multicast_socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

    def listen_on_tcp(self):
        while self.running:
            try:
                received_message = str(self.client_tcp_socket.recv(1024), 'utf-8')
                print(received_message)

                if 'was registered correctly!' in received_message:
                    nickname = re.findall(r"\[([^]]+)]", received_message)[1]
                    self.name = nickname

            except Exception as e:
                print(f'Error in receiving data: {e}')
                self.running = False
                break

        self.close_tcp_connection()

    def listen_on_udp(self):
        while self.running:
            try:
                received_message, address = self.client_udp_socket.recvfrom(1024)
                if address[0] != self.client_multicast_socket.getsockname()[0]:
                    received_message = str(received_message, 'utf-8')
                print(received_message)

            except Exception as e:
                print(f'Error during receiving message from server on udp socket:{e}')
                self.running = False
                break

        self.close_udp_connection()

    def listen_on_multicast(self):

        while self.running:
            try:
                received_message, address = self.client_multicast_socket.recvfrom(1024)
                sender_name, received_message = str(received_message, 'utf-8').split('|')

                if sender_name != self.name:
                    print(sender_name + ':' + received_message)

            except Exception as e:

                print(f'Error during receiving message from server on multicast socket :{e}')
                self.running = False
                break

        self.close_multicast_connection()

    def talk_to_server(self) -> None:
        self.init_socket()

        tcp_thread = threading.Thread(target=self.listen_on_tcp, daemon=True)
        tcp_thread.start()

        udp_thread = threading.Thread(target=self.listen_on_udp, daemon=True)
        udp_thread.start()

        multicast_thread = threading.Thread(target=self.listen_on_multicast, daemon=True)
        multicast_thread.start()

        self.send_message()

    def send_message(self):

        while self.running:
            try:
                input_message = input('')
                message = input_message[4:]
                if input_message.startswith("TCP|"):

                    self.client_tcp_socket.send(bytes(message, 'utf-8'))

                elif input_message.startswith("UDP|"):
                    if 'cs go' in input_message:
                        message += cs_go_logo
                    elif 'computer' in input_message:
                        message += computer
                    else:
                        message += dog
                    self.client_udp_socket.sendto(bytes(message, 'utf-8'), (self.server_address, self.server_port))

                elif input_message.startswith("MCT|"):
                    message = f'{self.name}| {message}'
                    self.client_multicast_socket.sendto(bytes(message, 'utf-8'),
                                                        (self.multicast_address, self.multicast_port))

                else:
                    print(f'Unknown communication protocol! Please choose one from TCP, UDP or MCT')

                if message == 'bye':
                    sys.exit()
            except Exception as e:
                print(f'Error in sending data: {e}')
                self.running = False
                break

        self.close_tcp_connection()
        self.close_udp_connection()
        self.close_multicast_connection()

    def choose_nickname(self) -> None:

        while self.choosing_nickname_running:
            try:
                nickname = input('')
                self.client_tcp_socket.send(bytes(nickname, 'utf-8'))
            except Exception as e:
                print(f'Error in choosing nickname: {e}')

    def close_tcp_connection(self) -> None:
        if self.client_tcp_socket:
            try:

                self.client_tcp_socket.close()
            except Exception as e:
                print(f'Error in closing tcp socket: {e}')

        sys.exit()

    def close_udp_connection(self) -> None:
        if self.client_udp_socket:
            try:
                self.client_udp_socket.close()

            except Exception as e:
                print(f'Error in closing udp socket: {e}')

        sys.exit()

    def close_multicast_connection(self) -> None:
        if self.client_multicast_socket:
            try:
                self.client_multicast_socket.close()

            except Exception as e:
                print(f'Error in closing multicast socket: {e}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='server_port', type=int, help='Add server port')
    parser.add_argument('-a', dest='server_address', type=str, help='Add server address')
    parser.add_argument('-mp', dest='multicast_port', type=int, help='Add server port')
    parser.add_argument('-ma', dest='multicast_address', type=str, help='Add server address')
    args = parser.parse_args()

    server_port = args.server_port
    server_address = args.server_address
    multicast_port = args. multicast_port
    multicast_address = args.multicast_address

    # server_port = 9090
    # server_address = 'localhost'
    #
    # multicast_port = 9091
    # multicast_address = '239.254.255.123'

    client = Client(
        server_port=server_port,
        server_address=server_address,
        multicast_port=multicast_port,
        multicast_address=multicast_address
    )
    client.talk_to_server()


if __name__ == '__main__':
    main()
