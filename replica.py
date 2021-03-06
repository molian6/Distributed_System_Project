import time, socket
from config import Message
from datetime import datetime, timedelta
from helper import *
# Implement the protocol each replica will run
class Replica(object):
    debug = False
    uid = None
    f = None
    view = None
    ports_info = None #a map uid-> [ip, ports]
    client_ports_info = None #a map client_id-> [ip, ports]
    request_count = {} # (req_id,value) -> count
    received_propose_list = {} #req_id -> [client_id, proposor, value, client_request_id]
    learned_list = {} # req_id -> [value, executed, client_id, client_request_id]
    waiting_request_list = []
    request_mapping = {} #(client_id, client_request_id) -> req_id
    log_file = None

    num_followers = None
    last_exec_req = None

    def __init__(self, f, uid, ports_info, client_ports_info, debug):
        self.uid = uid
        self.f = f
        self.ports_info = ports_info
        self.client_ports_info = client_ports_info
        self.last_exec_req = -1
        self.receive_socket = create_listen_sockets(self.ports_info[self.uid][0], self.ports_info[self.uid][1])
        self.view = -1
        self.debug = debug
        print "replica %d starts running at %s." % (self.uid , time.ctime(int(time.time())))
        self.log_file = 'log%d.txt'%(self.uid)
        with open(self.log_file , 'w') as fid:
            fid.write('Log for replica %d:\n' % (self.uid))

        if (self.uid == 0):
            time.sleep(1)
            self.beProposor()

        while True:
            # connect
            clientsocket, address = self.receive_socket.accept()
            max_data = 64000
            all_data = ""

            while True:
                message = clientsocket.recv(max_data)
                all_data += message.decode("utf-8")

                if len(message) != max_data:
                    break
            #clientsocket.settimeout(3)
            #try:
            if all_data != "":
                self.handle_message(decode_message(all_data))
            clientsocket.close()
            #except socket.timeout:
            #    clientsocket.close()
            
            #print all_data , self.uid

    def handle_message(self, m):
        if (m.mtype == 0):
            self.handle_IAmYourLeader(m)
        elif (m.mtype == 1):
            self.handle_YouAreMyLeader(m)
        elif (m.mtype == 2):
            self.handle_ProposeValue(m)
        elif (m.mtype == 3):
            self.handle_AcceptValue(m)
        elif (m.mtype == 4):
            self.handle_TimeOut(m)
        elif (m.mtype == 5):
            self.handle_Request(m)

    def sleep_forever(self):
        while True:
            time.sleep(1000)

    def broadcast_msg(self, m):
        for key in self.ports_info.keys():
            if key >= self.view:
                v = self.ports_info[key]
                #print key
                send_message(v[0], v[1], m)
                #time.sleep(0.2)

    # def write_to_disk(self , req_id):
    #     print "replica %d is write to request_id %d to disk" % (self.uid , req_id)))
    #     # print self.learned_list
    #     with open(self.log_file , 'a') as fid:
    #         fid.write('request %d: %s\n'%(req_id , self.learned_list[req_id][0]))

    # def send_response_to_client(self , req_id):
    def send_response_to_client(self , client_id, client_request_id):
        # client_id = self.received_propose_list[req_id][0]
        # client_request_id = self.received_propose_list[req_id][3]
        msg = Message(6, None, None, client_request_id, None, None, None)
        send_message(self.client_ports_info[client_id][0], self.client_ports_info[client_id][1], encode_message(msg))

    def logging(self, req_id, value, client_id, client_request_id):
        # value = m.value
        # req_id = m.request_id
        if self.last_exec_req + 1 == req_id:
            # logging
            self.last_exec_req += 1

            with open(self.log_file , 'a') as fid:
                fid.write('request %d: %s\n'%(req_id , value))
            self.learned_list[req_id] = [value , True, client_id, client_request_id]

            # self.write_to_disk(self.last_exec_req)
            if value != "NOOP":
                #send logging message to client
                self.send_response_to_client(client_id, client_request_id)

            if req_id+1 in self.learned_list and self.learned_list[req_id+1][1] == False:
                self.logging(req_id+1, self.learned_list[req_id+1][0], self.learned_list[req_id+1][2], self.learned_list[req_id+1][3])
        else:
            self.learned_list[req_id] = [value , False, client_id, client_request_id]

    def beProposor(self):
        self.num_followers = 0
        self.request_mapping = {}
        msg = Message(0, None, None, None, self.uid, None, None)
        self.broadcast_msg(encode_message(msg))


    def handle_IAmYourLeader(self, m):
        if self.debug:
            print 'handle_IAmYourLeader', m
        # if sender_id > view, update self.view
        # send YouAreMyLeader back with message = jsonify received_propose_list
        if m.sender_id >= self.view:
            self.view = m.sender_id
            msg = Message(1, None, None, None, self.uid, None, self.received_propose_list)
            print 'Recieve I Am Your Leader!', msg.sender_id, msg.client_id, msg.client_request_id
            #print self.ports_info[self.view][0],self.ports_info[self.view][1]
            send_message(self.ports_info[self.view][0], self.ports_info[self.view][1], encode_message(msg))
            #time.sleep(0.2)

    def handle_YouAreMyLeader(self, m):
        #if self.debug: 
        print 'handle_YouAreMyLeader', m.sender_id, m.client_id, m.client_request_id
        # update the most recent value for each blank in received_propose_list.
        self.num_followers += 1
        for key in m.received_propose_list.keys():
            x = m.received_propose_list[key]
            key = int(key)
            # if update every value to the newest proposer value
            if key not in self.received_propose_list.keys():
                print key , x
                self.received_propose_list[key] = x
            elif x[1] > self.received_propose_list[key][1]:
                self.received_propose_list[key] = x

        if self.num_followers == self.f + 1:
            #   fill the holes with NOOP
            #print "replica %d becomes leader!!! view %d" % (self.uid , self.view)
            if len(self.received_propose_list) > 0:
                for i in range(0,max(self.received_propose_list.keys(), key = int)):
                    if not i in self.received_propose_list:
                        self.received_propose_list[i] = [-1, self.uid, "NOOP", None]
            #print "replica %d becomes leader!!! view %d" % (self.uid , self.view)
            #print 'length:', len(self.received_propose_list.keys())
            #for key in self.received_propose_list.keys():
            #    print key , self.received_propose_list[key]
            #print self.received_propose_list
            #   propose everything in the list
            for key in self.received_propose_list.keys():
                x = self.received_propose_list[key]
                msg = Message(2, key, x[0], x[3], self.uid, x[2], None)
                #print key
                self.broadcast_msg(encode_message(msg))
                #print key
                if x[2] != 'NOOP':
                    self.request_mapping[(x[0] , x[3])] = int(key)
            print "replica %d becomes leader!!! view %d" % (self.uid , self.view)
            print len(self.waiting_request_list)
            #   propose everything in waiting_request_list
            while len(self.waiting_request_list) != 0:
                m = self.waiting_request_list.pop(0)
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
        print 'handle_YouAreMyLeader', m.sender_id, m.client_id, m.client_request_id

    def handle_ProposeValue(self, m):
        if self.debug: print 'handle_ProposeValue', m.client_id, m.client_request_id
        # if sender_id > view, update view & update
        #   update received_propose_list
        #   broadcast AcceptValue(proposorid + req_id + value)
        if m.sender_id >= self.view:
            if self.debug: print 'handle_ProposeValue', m.client_id, m.client_request_id
            self.view = m.sender_id
            if self.debug: print 'handle_ProposeValue', m.client_id, m.client_request_id
            self.received_propose_list[m.request_id] = [m.client_id, m.sender_id, m.value, m.client_request_id]
            if self.debug: print 'handle_ProposeValue', m.client_id, m.client_request_id
            msg = Message(3, m.request_id, m.client_id, m.client_request_id, self.uid, m.value, None)
            if self.debug: print 'handle_ProposeValue', m.client_id, m.client_request_id
            self.broadcast_msg(encode_message(msg))
            if self.debug: print 'handle_ProposeValue', m.client_id, m.client_request_id


    def handle_AcceptValue(self, m):
        if self.debug: print 'handle_AcceptValue', m.client_id, m.client_request_id
        # if any value reach the majority, do logging
        p = (m.request_id , m.value)
        if p not in self.request_count:
            self.request_count[p] = 1
        else:
            self.request_count[p] += 1
        if self.request_count[p] == self.f + 1:
            self.logging(m.request_id, m.value, m.client_id, m.client_request_id)

    def handle_TimeOut(self, m):
        if self.debug: print 'handle_TimeOut', m
        if self.view < m.sender_id: #ugli implementation sender_id here means client view
            self.view = m.sender_id
            if (self.view == self.uid):
                self.beProposor()

    def handle_Request(self, m):
        print 'handle_request', m.client_id, m.client_request_id , self.uid
        if self.view == self.uid:
            if self.num_followers >= self.f + 1:
                # has enough followers
                if (m.client_id , m.client_request_id) not in self.request_mapping.keys():
                    # edit message
                    m.sender_id = self.uid
                    #req_id is next index in request_mapping
                    if len(self.request_mapping) == 0: req_id = 0
                    else: req_id = max(self.request_mapping.values()) + 1
                    m.request_id = req_id
                    # change message type to proposeValue
                    m.mtype = 2
                    #print m.request_id, m.client_id, m.client_request_id, m.value
                    # encode message
                    msg = encode_message(m)
                    # broadcast message
                    self.broadcast_msg(msg)
                    # add req_id to mapping list
                    self.request_mapping[(m.client_id , m.client_request_id)] = req_id
            else:
                # waitting for followers, add request to waitlist
                self.waiting_request_list.append(m)
