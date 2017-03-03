# start the paxo service
# Start the entire paxo service, start 2f+1 replicas
# Manage meta data for replicas


import click, paxoservice, os, shutil

# Configure command line options
DEFAULT_NUM_FAILURES = 2
DEFAULT_PORT_NUM = 6000
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)

@click.option("--num_failures", "-f", "num_failures",
    default=DEFAULT_NUM_FAILURES,
    help="Number of failures this server can tolerate, default " + str(DEFAULT_NUM_WORKERS))

def main(num_failures=DEFAULT_NUM_FAILURES):
    for i in range(2*num_failures+1):
        p = Process(target=replica.Replica, args = (f, i, someport_info)) #f, ID, port_info
        p.start()
  # Create a new master and let it take over
  # master_ = paxoservice.Paxoservice(num_failures)

if __name__ == "__main__":
  main()
