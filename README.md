This is an brief implementation of PAXOS algorithms from Mingzhe Wang and Lian Mo.

To test our system, please run the following commands:

pip install ruamel.yaml
python start.py -num_failures 7 -num_clients 5 -mode 1

You can indicate the number of failures with '-num_failures', indicate the number of clients with '-num_clients'. You can also configure the ip and ports of clients and replicas with '-client_ports', '-server_ports'.

You can also modify test mode from 1 to 4, which implements test case 1 to 4. Please refer to print information for the use of each test mode.
