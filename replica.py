import config
from helper import *
# Implement the protocol each replica will run
class Replica(object):
    uid = None
    f = None
    view = None
    ports_info = None #a map uid-> [ip, ports]
    request_list = {} # (req_id,value) -> count
    received_propose_list = {} #req_id -> [client_id, proposor, value]
    learned_list = {} # req_id -> value, executed?
    waiting_request_list = {}

    num_followers = None
    last_exec_req = None

    def __init__(self, f, uid, ports_info):
        self.uid = uid
        self.f = f
        self.ports_info = ports_info
        self.receive_socket = create_listen_sockets(self.ports_info[self.uid][0], self.ports_info[self.uid][1])

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
        

    def broadcast(self, m):
        for v in self.ports_info:
            send_message(v[0], v[1], m)

    def logging(self, req_id):
        if self.last_exec_req + 1 == req_id:
            # logging
            self.last_exec_req += 1
            learned_list[req_id] = [value , True]
            #send logging message to client
            if req_id+1 is in self.learned_list and self.learned_list[req_id+1][1] == False:
                self.logging(req_id+1)
        else:
            learned_list[req_id] = [value , False]

    def beProposor(self):
        self.num_followers = 1
        # broadcast message IAmYourLeader
        # handle holes or not?

    def handle_IAmYourLeader(self, m):
        # if sender_id > view, update self.view
        # send YouAreMyLeader back with message = jsonify received_propose_list

    def handle_YouAreMyLeader(self, m):
        # update the most recent value for each blank in received_propose_list.
        self.num_followers += 1
        if self.num_followers == self.f + 1:
        #   fill the holes with NOOP
        #   propose everything in the list
        #   propose everything in waiting_request_list

    def handle_ProposeValue(self, m):
        # if sender_id > view, update view & update
        #   update received_propose_list
        #   broadcast AcceptValue(proposorid + req_id + value)

    def handle_AcceptValue(self, m):
        # if any value reach the majority, do logging

    def handle_TimeOut(self, m):
        self.view += 1
        if (self.view == self.uid):
            self.beProposor()

    def handle_Request(self, m):
        if self.view == self.uid:
            #if  is leader #propose()
            #else: add request to waiting_request_list
