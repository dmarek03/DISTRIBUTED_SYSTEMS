import socket

server_port = 9009

server_address = '127.0.0.1'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = 'hello world'
client_socket.sendto(bytes(message, 'utf-8'), (server_address, server_port))
