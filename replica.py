import config
from helper import *
# Implement the protocol each replica will run
class Replica(object):
    uid = None
    f = None
    view = None
    ports_info = None #a map uid-> [ip, ports]
    request_list = {} #(clientid, req_id)->value
    num_followers = None

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

    def parse_message(msg):
        l = msg.split(msg)
        mtype = int(l[0])
        request_id = int(l[1])
        mcontent = l[2:]
        m = config.Message(mtype, request_id, mcontent)
        return m

    def broadcast(self, m):

    def beProposor(self):

    def handle_IAmYourLeader(self, m):

    def handle_YouAreMyLeader(self, m):

    def handle_ProposeValue(self, m):

    def handle_AcceptValue(self, m):

    def handle_TimeOut(self, m):
        self.view += 1
        if (self.view == self.uid):
            self.beProposor()

    def handle_Request(self, m):
