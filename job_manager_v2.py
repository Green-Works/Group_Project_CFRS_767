#!/usr/bin/python3
'''
############################################################################
#
#   CFRS-767 Group Project - JobManager
#        - Marcus Coates
#        - Brian Daugette
#        - Tom Mahony
#        - Adam McKelvey
#
###########################################################################
#
#   LANGUAGE: Python 3
#   PYTHON VERSION: 3.5 (tested)
#   MODULES REQUIRED:
#       - argparse
#       - http.server
#		   - logging
#   SCRIPT VER: 0.2
#   REQURIED FILES:
#       - /etc/job_manager/job_manager.config
#
###########################################################################
#
# DESCRIPTION:
#       This script is the job manager for a distributed processing
#        engine to crack passwords with hashcat. This script runs as a
#        service that takes in user input and delegates work to processes
#        known as "workers" for password cracking.
#
###########################################################################
'''

import argparse
import http.server
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

# Parse inputs
# Question: do we only want to pass a single hash or have the option to pass
# a text file of several hashes (as long as the hashes are the same type)?
PARSE = argparse.ArgumentParser(description="Distributed dictionary attack on a hash!")
PARSE.add_argument("-s", "--string", help="the hash string to be cracked")
PARSE.add_argument("-t", "--type", help="the type of hash supplied. Supported options are [ ntlm | md5 ]")
PARSE.add_argument("-p", "--port", type=int, help="TCP port workers are using")
ARGS = PARSE.parse_args()

# this module discovers the workers up on the wire
def worker_discover(PORT):
    print("This part of the script should discover the workers running on the network")
    print("Searching for workers on tcp port %s" % PORT)
    WORKER_LIST = ["worker1", "worker2", "worker3"]
    return(WORKER_LIST)

# this listens for responses from the workers and responds
def worker_monitor(WORKER_LIST):
    print("listen for response")
    print("answer found/kill jobs")
    return("ANSWER")

# This is the part of the script that sends a POST/GET message to the workers with the
def send_work(WORKER_LIST, HASH, TYPE, PORT):
    print("send work...")
    TOTAL_WORKERS = len(WORKER_LIST)
    i = 1
    for x in WORKER_LIST:
        print("http://%s:%s --- POST: hash: %s type: %s Portion: %s/%s" % (x, PORT, HASH, TYPE, i, TOTAL_WORKERS))
        i += 1


# troubleshooting. modified this to use logging. no need to delete as it can be used later during debugging
logging.debug("String is: %s" % ARGS.string)
logging.debug("Type is: %s" % ARGS.type)
logging.debug("Port is: %s" % ARGS.port)

# Error check the input
## there could be a function statement that checks whether or not the string is actually an md5/ntlm/etc.
if ARGS.type not in ["ntlm", "md5"]:
    print("ERROR: Invalid input. [%s] is not an acceptable input." % ARGS.type)
    exit(1)

# Main logic
WORKER_LIST = worker_discover(ARGS.port)
print("The workers found are %s" % WORKER_LIST)
send_work(WORKER_LIST, ARGS.string, ARGS.type, ARGS.port)