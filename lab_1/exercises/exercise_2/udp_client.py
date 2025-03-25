import socket

server_port = 9999
server_address = '127.0.0.1'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg_to_send = 'żółta gęś'

client_socket.sendto(bytes(msg_to_send, 'utf-8'), (server_address, server_port))

