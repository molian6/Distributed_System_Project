# start the paxo service
# Start the entire paxo service, start 2f+1 replicas
# Manage meta data for replicas


import click, config, replica, os, shutil, client
import time, multiprocessing
import random

# Configure command line options
DEFAULT_NUM_FAILURES = 3
DEFAULT_NUM_CLIENTS = 1
DEFAULT_PORT_NUM = 6000
DEBUG = False
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def create_ports_map(n, ip_add, ports):
	s = {}
	for i in range(0, n):
		s[i] = [ip_add, ports+i]
	return s

def Paxoservice():

	server_ports_info = create_ports_map(2*DEFAULT_NUM_FAILURES+1, "127.0.0.1", 5500)
	client_ports_info = create_ports_map(DEFAULT_NUM_CLIENTS, "127.0.0.1", 6500)
	print server_ports_info
	print client_ports_info
	# create replicas
	client_list = []
	for i in range(DEFAULT_NUM_CLIENTS):
		e = multiprocessing.Event()
		p = multiprocessing.Process(target = client.Client , args = (client_ports_info[i][0] , client_ports_info[i][1], i , server_ports_info , e))
		p.start()
		client_list.append([p , e])
	print 'Create %d clients successfully!' % (DEFAULT_NUM_CLIENTS)
	replica_list = []
	for i in range(2*DEFAULT_NUM_FAILURES+1):
		p = multiprocessing.Process(target=replica.Replica, args = (DEFAULT_NUM_FAILURES , i , server_ports_info , client_ports_info , DEBUG)) #f, ID, port_info
		p.start()
		replica_list.append(p)
	print 'Create %d replicas successfully!' % (2*DEFAULT_NUM_FAILURES+1)
	# operation here

	time.sleep(3)
	t = time.time() + 2
	while time.time() < t:
		a = random.randint(0,DEFAULT_NUM_CLIENTS-1)
		if client_list[a][1].is_set() == False:
			client_list[a][1].set()
	time.sleep(2)

	replica_list[0].terminate()
	t = time.time() + 15
	while time.time() < t:
		a = random.randint(0,DEFAULT_NUM_CLIENTS-1)
		if client_list[a][1].is_set() == False:
			client_list[a][1].set()
	time.sleep(5)

	# terminate
	for p in client_list:
		if p[0].is_alive():
			p[0].terminate()
		p[0].join()
	for p in replica_list:
		if p.is_alive():
			p.terminate()
		p.join()

	# check log files.
	flag = True
	with open('log0.txt') as fid:
		logs1 = fid.readlines()[1:]
	for i in range(2*DEFAULT_NUM_FAILURES):
		with open('log%d.txt'%(i+1)) as fid:
			logs2 = fid.readlines()[1:]
			for j in range(len(logs1)):
				if logs1[j] != logs2[j]:
					flag = False
					print 'Fault: '
					print 'log 1 line %d : %s' % (j , logs1[j])
					print 'log %d line %d : %s' % (i+1, j , logs2[j])
	if flag:
		print 'Check successfully!'


if __name__ == "__main__":
  Paxoservice()
