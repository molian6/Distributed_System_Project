import socket
import ruamel.yaml as yaml
import json
from config import Message

def send_message(host, port_number, m):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if s.connect_ex((host, port_number)) == 0:
        s.sendall(str.encode(m))
    s.close()

def create_listen_sockets(host, port_number):
    print "#############"
    print host,port_number
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port_number))
    s.listen(20)
    return s

def encode_message(m):
    message = {
        "mtype": m.mtype,
        "request_id": m.request_id,
        "client_id": m.client_id,
        "client_request_id": m.client_request_id,
        "sender_id": m.sender_id,
        "value": m.value,
        "received_propose_list": m.received_propose_list
    }
    return json.dumps(message)

def decode_message(msg):
    msg_dict = yaml.safe_load(msg)
    m = Message(msg_dict["mtype"], msg_dict["request_id"], msg_dict["client_id"], ["client_request_id"], msg_dict["sender_id"], msg_dict["value"], msg_dict["received_propose_list"])
    return m

def debug_print(debug_str, num):
    print_on = False
    if print_on:
        print("\t" * 3 * num + debug_str)
