import time, socket
from datetime import datetime, timedelta
from helper import *
from config import Message

# use for sending messages by script.
# use for testing purpose
class Client:
    time = None
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
        self.my_port = my_port
        self.my_ip = my_ip
        self.client_request_id = 0
        self.view = 0
        self.timeout = 2
        self.client_listen_socket = create_listen_sockets(self.my_ip, self.my_port)
        self.e = e
        print 'Client %d starts running at %s' % (self.client_id , time.ctime(int(time.time())))
        while True:
            #self.time = time.time()
            e.wait()
            print 'Client %d send message %d at time %s.' % (self.client_id , self.client_request_id , time.ctime(int(time.time())))
            self.client_send_message()
            e.clear()

    def client_send_message(self):
        m = 'This is message %d from client %d !!!' % (self.client_request_id, self.client_id)
        msg = Message(5, None, self.client_id, self.client_request_id, None, m, None);
        encoded_msg = encode_message(msg)
        send_message(self.ports_info[self.view][0], self.ports_info[self.view][1], encoded_msg)
        nextTimeout = self.timeout
        # nextTimeout = time.time() + self.timeout
        while True:    
            self.client_listen_socket.settimeout(nextTimeout)
            try:
                t = time.time()
                replicasocket, address = self.client_listen_socket.accept()
                max_data = 1024
                all_data = ""
                while True:
                    try: 
                        message = replicasocket.recv(max_data)
                        all_data += message.decode("utf-8")
                        if len(message) != max_data:
                            break
                    except socket.error, e:
                        if str(e) == "[Errno 35] Resource temporarily unavailable": 
                            time.sleep(0.1)
                        else:
                            raise e
                replicasocket.close()
                m = decode_message(all_data)
                if m.client_request_id == self.client_request_id:
                    print 'Client %d request %d is received in %s' % (self.client_id , self.client_request_id , time.ctime(int(time.time())))
                    self.client_request_id += 1
                    break
                else:
                    nextTimeout = nextTimeout - (time.time() - t)

            except socket.timeout:
                print 'Client %d request %d timeout.' % (self.client_id , self.client_request_id)
                self.view = self.view + 1
                msg = Message(4, None, None, None, None, None, None)
                self.broadcast_msg(encode_message(msg))
                self.timeout *= 2
                self.client_send_message()

    def broadcast_msg(self, m):
        for key in self.ports_info.keys():
            v = self.ports_info[key]
            send_message(v[0], v[1], m)
