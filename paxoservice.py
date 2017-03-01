# Start the entire paxo service
# Manage meta data for replicas
# We may not need it
class Paxoservice:

    # create 2f+1 replicas in init
    def __init__(self, f):
        for i in range(2*f+1):
            p = Process(target=replica.Replica, args = (f, i, someport_info)) #f, ID, port_info
            p.start()

    def somesetup(self):
