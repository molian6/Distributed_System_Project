import socket

def send_message(host, port, m):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if s.connect_ex((host, port_number)) == 0:
        s.sendall(str.encode(m))
    s.close()

def create_listen_sockets(host, port_number):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port_number))
    s.listen(20)
    return s

def debug_print(debug_str, num):
    print_on = False
    if print_on:
        print("\t" * 3 * num + debug_str)
