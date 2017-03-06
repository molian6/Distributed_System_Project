import socket
from helper import *

s = create_listen_sockets("127.0.0.2", 8888)
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# s.bind(("127.0.0.2", 8888))
# s.listen(20)

while True:
    # connect
    clientsocket, address = s.accept()
    max_data = 1024
    all_data = ""

    while True:
        message = clientsocket.recv(max_data)
        all_data += message.decode("utf-8")

        if len(message) != max_data:
            break
    clientsocket.close()

    print(all_data)

    send_message("127.0.0.2", 8888, "hey here's a message")

