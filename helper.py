import socket
import ruamel.yaml as yaml
import json
import time
import random
from config import Message

def send_message(host, port_number, m):
    # TODO: I think its better to set a timeout here
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, port_number))
    s.sendall(m)
    s.close()

def create_listen_sockets(host, port_number):
    #print "#############"
    #print host,port_number
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port_number))
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
    m = Message(msg_dict["mtype"], msg_dict["request_id"], msg_dict["client_id"], msg_dict["client_request_id"], msg_dict["sender_id"], msg_dict["value"], msg_dict["received_propose_list"])
    '''
    if m.request_id != None: m.request_id = int(m.request_id)
    if m.sender_id != None: m.sender_id = int(m.sender_id)
    if m.client_id != None: m.client_id = int(m.client_id)
    if m.client_request_id != None: m.client_request_id = int(m.client_request_id)
    if m.mtype != None: m.mtype = int(m.mtype)
    '''
    return m

def debug_print(debug_str, num):
    print_on = False
    if print_on:
        print("\t" * 3 * num + debug_str)
