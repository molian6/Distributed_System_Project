import config, time, socket
from datetime import datetime, timedelta
from helper import *
# Implement the protocol each replica will run
class Replica(object):
    uid = None
    f = None
    view = None
    ports_info = None #a map uid-> [ip, ports]
    client_ports_info = None #a map client_id-> [ip, ports]
    request_count = {} # (req_id,value) -> count
    received_propose_list = {} #req_id -> [client_id, proposor, value, client_request_id]
    learned_list = {} # req_id -> value, executed?
    waiting_request_list = []
    request_mapping = {} #(client_id, client_request_id) -> req_id
    log_file = None

    num_followers = None
    last_exec_req = None

    def __init__(self, f, uid, ports_info, client_ports_info):
        self.uid = uid
        self.f = f
        self.ports_info = ports_info
        self.client_ports_info = client_ports_info
        self.last_exec_req = -1
        self.receive_socket = create_listen_sockets(self.ports_info[self.uid][0], self.ports_info[self.uid][1])
        log_file = 'log%d.txt'%(self.uid)
        with open(log_file , 'w') as fid:
            fid.write('Log for replica %d:\n' % (self.uid))

        if (self.uid == 0):
            self.beProposor()

        while True:
            # connect
            clientsocket, address = self.receive_socket.accept()
            max_data = 1024
            all_data = ""

            while True:
                message = clientsocket.recv(max_data)
                all_data += message.decode("utf-8")

                if len(message) != max_data:
                    break
            clientsocket.close()

            self.handle_message(self.parse_message(all_data))

    def handle_message(self, m):
        if (m.mtype == 0):
            self.handle_IAmYourLeader(self, m)
        elif (m.mtype == 0):
            self.handle_YouAreMyLeader(self, m)
        elif (m.mtype == 0):
            self.handle_ProposeValue(self, m)
        elif (m.mtype == 0):
            self.handle_AcceptValue(self, m)
        elif (m.mtype == 0):
            self.handle_TimeOut(self, m)
        elif (m.mtype == 0):
            self.handle_Request(self, m)

    def sleep_forever(self):
        while True:
            time.sleep(1000)

    def broadcast_msg(self, m):
        for v in self.ports_info:
            send_message(v[0], v[1], m)

    def write_to_disk(req_id):
        with open(self.log_file , 'a') as fid:
            fid.write('request %d: %s\n'%(req_id , self.received_propose_list[req_id][2]))

    def send_response_to_client(req_id):
        client_id = self.received_propose_list[req_id][0]
        msg = Message(6, None, None, None, None, None, None)
        send_message(self.client_ports_info[client_id][0], self.client_ports_info[client_id][1], encode_message(msg))

    def logging(self, req_id):
        if self.last_exec_req + 1 == req_id:
            # logging
            self.last_exec_req += 1
            self.write_to_disk(self.last_exec_req)
            if self.received_propose_list[req_id][2] != "NOOP":
                self.send_response_to_client(self.last_exec_req)
            learned_list[req_id] = [value , True]
            #send logging message to client
            if req_id+1 is in self.learned_list and self.learned_list[req_id+1][1] == False:
                self.logging(req_id+1)
        else:
            learned_list[req_id] = [value , False]

    def beProposor(self):
        self.num_followers = 0
        self.request_mapping = {}
        msg = Message(0, None, None, None, self.uid, None, None)
        self.broadcast_msg(encode_message(msg))


    def handle_IAmYourLeader(self, m):
        # if sender_id > view, update self.view
        # send YouAreMyLeader back with message = jsonify received_propose_list
        if m.sender_id >= self.view:
            self.view = m.sender_id
            msg = Message(1, None, None, None, self.uid, None, self.received_propose_list)
            send_message(self.ports_info[self.view][0], self.ports_info[self.view][1], encode_message(msg))

    def handle_YouAreMyLeader(self, m):
        # update the most recent value for each blank in received_propose_list.
        self.num_followers += 1
        for key, x in m.received_propose_list.iteritems():
            # if update every value to the newest proposer value
            if key not in self.received_propose_list.keys():
                self.received_propose_list[key] = x
            elif x[1] > self.received_propose_list[key][1]:
                self.received_propose_list[key] = x

        if self.num_followers == self.f + 1:
            #   fill the holes with NOOP
            for i in range(0,max(self.received_propose_list.keys(), key = int)):
                if not i in self.received_propose_list:
                    self.received_propose_list[i] = [-1, self.uid, "NOOP", None]

            #   propose everything in the list
            for key, x in self.received_propose_list.iteritems():
                msg = Message(2, key, x[0], x[3], self.uid, x[2], None)
                self.broadcast_msg(encode_message(msg))
                if x[2] != 'NOOP':
                    self.request_mapping[(x[0] , x[3])] = key

            #   propose everything in waiting_request_list
            while len(self.waiting_request_list) != 0:
                m = self.waiting_request_list.pop(0)
                m = decode_message(m)
                if (m.client_id , m.client_request_id) not in self.request_mapping.keys():
                    # edit message
                    m.sender_id = self.uid
                    #req_id is next index in request_mapping
                    if len(self.request_mapping) == 0: req_id = 0
                    else: req_id = max(self.request_mapping.values()) + 1
                    m.request_id = req_id
                    # change message type to proposeValue
                    m.mtype = 2
                    # encode message
                    msg = encode_message(m)
                    # broadcast message
                    self.broadcast_msg(msg)
                    # add req_id to mapping list
                    self.request_mapping[(m.client_id , m.client_request_id)] = req_id

    def handle_ProposeValue(self, m):
        # if sender_id > view, update view & update
        #   update received_propose_list
        #   broadcast AcceptValue(proposorid + req_id + value)
        if m.sender_id >= self.view:
            self.view = m.sender_id
            self.received_propose_list[m.request_id] = [m.client_id, m.sender_id, m.value, m.client_request_id]
            msg = Message(3, m.request_id, m.client_id, m.client_request_id, self.uid, m.value, None)
            self.broadcast_msg(encode_message(msg))


    def handle_AcceptValue(self, m):
        # if any value reach the majority, do logging
        m = docode_message(m)
        p = (m.request_id , m.value)
        if p not in self.request_count:
            self.request_count[p] = 1
        else:
            self.request_count[p] += 1
        if self.request_count[p] == self.f + 1:
            self.logging(m.request_id)

    def handle_TimeOut(self, m):
        self.view += 1
        if (self.view == self.uid):
            self.beProposor()

    def handle_Request(self, m):
        if self.view == self.uid:
            if self.num_followers == self.f + 1:
                # has enough followers
                m = decode_message(m)
                if (m.client_id , m.client_request_id) not in self.request_mapping.keys():
                    # edit message
                    m.sender_id = self.uid
                    #req_id is next index in request_mapping
                    if len(self.request_mapping) == 0: req_id = 0
                    else: req_id = max(self.request_mapping.values()) + 1
                    m.request_id = req_id
                    # change message type to proposeValue
                    m.mtype = 2
                    # encode message
                    msg = encode_message(m)
                    # broadcast message
                    self.broadcast_msg(msg)
                    # add req_id to mapping list
                    self.request_mapping[(m.client_id , m.client_request_id)] = req_id
            else:
                # waitting for followers, add request to waitlist
                self.waiting_request_list.append(m)
