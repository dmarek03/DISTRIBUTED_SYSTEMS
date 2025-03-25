from socket import socket, AF_INET, SOCK_DGRAM

server_port = 9010
server_address = '127.0.0.1'

client_socket = socket(AF_INET, SOCK_DGRAM)

while True:

    message = input("Enter message:")
    message_from_python = "PYTHON| " + message

    client_socket.sendto(bytes(message_from_python, 'utf-8'), (server_address, server_port))

    received_message, address = client_socket.recvfrom(1024)
    received_message = received_message.decode('utf-8')
    print(f"Received from server: {received_message}")

    if received_message == 'EXIT':
        client_socket.close()
        break



