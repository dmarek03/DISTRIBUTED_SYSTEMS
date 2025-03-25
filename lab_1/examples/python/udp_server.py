import socket

port = 9009

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', port))

buff = []

while True:
    buff, message = server_socket.recvfrom(1024)
    print("received msg: " + str(buff, 'utf-8'))
