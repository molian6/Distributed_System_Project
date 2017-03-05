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

def create_ports_map(n, ip_add, ports):
	s = {}
	for i in range(0, n):
		s[i] = [ip_add+str(i), ports+i]
	return s

def Paxoservice():

	server_ports_info = create_ports_map(2*DEFAULT_NUM_FAILURES+1, "127.0.0.", 5000)
	client_ports_info = create_ports_map(DEFAULT_NUM_CLIENTS, "128.0.0.", 5000)

	# create replicas
	client_list = []
	for i in range(DEFAULT_NUM_CLIENTS):
		e = multiprocessing.Event()
		p = multiprocessing.Process(target = client.Client , args = (client_ports_info[i][0] , client_ports_info[i][1], i , server_ports_info , e))
		p.start()
		client_list.append([p , e])

	replica_list = []
	for i in range(2*DEFAULT_NUM_FAILURES+1):
		p = multiprocessing.Process(target=replica.Replica, args = (DEFAULT_NUM_FAILURES , i , server_ports_info , client_ports_info)) #f, ID, port_info
		p.start()
		replica_list.append(p)
	# operation here


if __name__ == "__main__":
  Paxoservice()
