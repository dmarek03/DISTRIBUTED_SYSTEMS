from socket import socket, AF_INET, SOCK_DGRAM


server_port = 9008
server_address = '127.0.0.1'

client_socket = socket(AF_INET, SOCK_DGRAM)


while True:

    number = int(input(f'Enter number to send: '))
    msg_bytes = number.to_bytes(4, byteorder='little')

    client_socket.sendto(msg_bytes, (server_address, server_port))

    buff, address = client_socket.recvfrom(4)
    received_number = int.from_bytes(buff, byteorder='little')
    print(f'Received from server: {received_number}')


