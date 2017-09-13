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
#   SCRIPT VER: 0.1
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

# Parse inputs
PARSE = argparse.ArgumentParser(description="Distributed dictionary attack on a hash!")
PARSE.add_argument("-s", "--string", help="the hash string to be cracked")
PARSE.add_argument("-t", "--type", help="the type of hash supplied. Supported options are [ ntlm | md5 ]")
PARSE.add_argument("-p", "--port", type=int, help="TCP port workers are using")
ARGS = PARSE.parse_args()

#this module discovers the workers up on the wire
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
#troubleshooting. delete this later
print("String is: %s" % ARGS.string)
print("Type is: %s" % ARGS.type)
print("Port is: %s" % ARGS.port)

# Error check the input
## there could be a function statement that checks whether or not the string is actually an md5/ntlm/etc.
if ARGS.type not in ["ntlm", "md5"]:
    print("ERROR: Invalid input. [%s] is not an acceptable input." % ARGS.type)
    exit(1)

# Main logic
WORKER_LIST = worker_discover(ARGS.port)
print("The workers found are %s" % WORKER_LIST)
send_work(WORKER_LIST, ARGS.string, ARGS.type, ARGS.port)
