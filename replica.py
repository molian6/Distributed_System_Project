# Implement the protocol each replica will run
class Replica(object):
    uid = None
    f = None
    view = None
    ports_info = None #a map uid-> ip & ports
    request_list = {}

    def __init__(self, f, uid, ports_info):
        self.uid = uid
        self.f = f
        self.ports_info = ports_info

        if (self.uid == 0):
            propose...

        while True:
            msg = receive messages
            handle_message()
        
