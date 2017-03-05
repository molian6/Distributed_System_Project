import config, time, socket
from datetime import datetime, timedelta
from helper import *

# use for sending messages by script.
# use for testing purpose
class Client:
    self.time = None
    e = None
    my_ip = None
    my_port = None
    ports_info = None
    client_id = None
    client_request_id = None
    view = None
    timeout = None
    client_listen_socket = None

    def __init__(self, my_ip, my_port, client_id, ports_info, e):
        self.ports_info = ports_info
        self.client_id = client_id
        self.client_request_id = 0
        self.view = 0
        self.timeout = 2
        self.client_listen_socket = create_listen_sockets(self.my_ip, self.my_port)
        self.e = e
        print 'Client %d starts running at %.2f' % (self.client_id , time.time())
        while True:
            #self.time = time.time()
            e.wait()
            print 'client %d send message %d at time %.2f.' % (self.client_id , self.client_request_id , time.time())
            self.client_send_message()
            e.clear()

    def client_send_message(self):
        m = 'This is message %d from client %d !!!' % (self.client_request_id, self.client_id)
        msg = Message(5, None, self.client_id, self.client_request_id, None, m, None);
        encodeded_msg = encodeded_msg(msg)
        send_message(self.ports_info[self.view][0], self.ports_info[self.view][1], encodeded_msg)

        socket.settimeout(self.timeout)
        # nextTimeout = time.time() + self.timeout
        try:
            replicasocket, address = self.client_listen_socket.accept()
            max_data = 1024
            all_data = ""

            while True:
                message = replicasocket.recv(max_data)
                all_data += message.decode("utf-8")

                if len(message) != max_data:
                    break
            replicasocket.close()

            m = decode_message(all_data)
            print 'Client %d request %d is received in %.2f' % (self.client_id , self.client_request_id , time.time())
            self.client_request_id += 1

        except socket.timeout:
            self.view = self.view + 1
            #broadcast view+1 to every replica
            self.timeout *= 2
            self.client_send_message()
