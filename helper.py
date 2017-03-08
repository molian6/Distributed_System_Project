import socket
import ruamel.yaml as yaml
import json
import time
import random
from config import Message

# def send_message(host, port_number, m):
#     sleeptime = random.randint(0,2)/10.0
#     #time.sleep(sleeptime)
#     #if random.randint(0,7) == 0:
#     #    return
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     if s.connect_ex((host, port_number)) == 0:
#         s.settimeout(2)
#         try:
#             t = time.time()
#             #print 'start to send message at time', t
#             s.sendall(str.encode(m))
#             #print 'send message in %f seconds' % (time.time()-t)
#             #print m
#         except Exception, e:
#             print 'Error: %d' % (port_number), e
#         finally:
#             s.close()
#     #time.sleep(0.2)
#     #s.close()

def send_message(host, port_number, m):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, port_number))
    s.sendall(m)
    s.close()

def create_listen_sockets(host, port_number):
    #print "#############"
    #print host,port_number
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port_number))
    # s.listen(2000)
    return s
# def create_listen_sockets(host, port_number):
#     #print "#############"
#     #print host,port_number
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     s.bind((host, port_number))
#     s.listen(2000)
#     return s

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
