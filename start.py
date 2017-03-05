# start the paxo service
# Start the entire paxo service, start 2f+1 replicas
# Manage meta data for replicas


import click, config, replica, os, shutil, client
import time, multiprocessing

# Configure command line options
DEFAULT_NUM_FAILURES = 2
DEFAULT_NUM_CLIENTS = 2
DEFAULT_PORT_NUM = 6000
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def Paxoservice():
    # create replicas
    client_list = [] #[process , event]
    for i in range(DEFAULT_NUM_CLIENTS):
    	e = multiprocessing.Event()
    	p = multiprocessing.Process(target = client.Client , args = (None , None, i , None , e))
    	p.start()
    	client_list.append([p , e])
    replica_list = []
    for i in range(2*DEFAULT_NUM_FAILURES+1):
        p = multiprocessing.Process(target=replica.Replica, args = (DEFAULT_NUM_FAILURES , i , None , None)) #f, ID, port_info
        p.start()
        replica_list.append(p)
    # operation here

if __name__ == "__main__":
  Paxoservice()
