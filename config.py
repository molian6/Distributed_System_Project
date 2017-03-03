class Message():
    mtype = None
    #Sender_id = None
    request_id = None
    #mcontent = None
    sender_id = None
    value = None
    IAmYourLeader = 0 # Sender_id
    YouAreMyLeader = 1 # previous Sender_id, value
    ProposeValue = 2 # Sender_id value
    AcceptValue = 3 # value
    TimeOut = 4
    Request = 5 # value
    def __init__(mtype = None , request_id = None , mcontent):
        self.mtype = mtype
        self.request_id = request_id
        self.mcontent = mcontent
