#!/usr/bin/python3
'''
############################################################################
#
#   CFRS-767 Group Project - JobManager
#        - MC
#        - BD
#        - TM
#        - AM
#
###########################################################################
#
#   LANGUAGE: Python 3
#   PYTHON VERSION: 3.5 (tested)
#   MODULES REQUIRED:
#       - argparse
#       - http.server
#		- logging
#       - netifaces
#       - netaddr
#       - socket
#   SCRIPT VER: 0.3
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
import netifaces
import netaddr
import socket
import requests

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

# credit to https://gist.github.com/gkbrk/99442e1294a6c83368f5#file-scanner-py-L46 for this function
# it scans a ip:port and returns whether or not the port is open.
def is_port_open(host, port): #Return boolean
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        sock.connect((host, port))
    except socket.error:
        return False
    return True
'''
This module discovers the workers up on the wire based on a specific open port.
Further error checking could be done on this to make sure a worker was listening on the given port
and not some other service (i.e. a specific GET request)
'''
def worker_discover(PORT):
    WORKER_LIST = []
    logging.debug("Searching for workers on local network using tcp port %s" % PORT)
    for X in netifaces.interfaces():
        INTERFACE_DATA = netifaces.ifaddresses(X).get(netifaces.AF_INET)
        IP = INTERFACE_DATA[0]['addr']
        NETMASK = INTERFACE_DATA[0]['netmask']
        CIDR = netaddr.IPAddress(NETMASK).netmask_bits()
        netaddr.IPAddress(IP)
        NETWORK = IP + "/" + str(CIDR)
        netaddr.IPNetwork(NETWORK)
        logging.debug("Interface: %s \tIP: %s\tNETMASK: %s" % (X, IP, CIDR))
        type(IP)
        #Special check for the local host otherwise the scan would take forever since localhost CIDR is /8
        if IP[0:3] == "127":
            is_open = is_port_open(IP, PORT)
            if is_open is True:
                WORKER_LIST.extend([str(IP)])
                logging.debug("port %s open on localhost" % (PORT))
            else:
                logging.debug("port %s is NOT open on localhost" % (PORT))
        #this is the scan for all other interfaces. Variable 'Y' contains a single ip address in the CIDR range
        else:
            for Y in netaddr.IPNetwork(NETWORK):
                if str(Y) == IP:
                    logging.debug("skipping scan on IP: %s" % str(Y))
                else:
                    is_open = is_port_open(str(Y), PORT)
                    if is_open is True:
                        WORKER_LIST.extend([str(Y)])
                        logging.debug("port %s open on IP %s" % (PORT, str(Y)))
        logging.debug("Workers found: %s" % WORKER_LIST)
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
        url = "http://" + str(x) + ":" + str(PORT)
        start = url + "/start"
        print(url)
        print(start)
        payload = {'hash': HASH, 'type': TYPE, 'wnum': i, 'totalw': TOTAL_WORKERS}
        try:
            r = requests.post(start, data=payload)
            print(r.url)
            print("http://%s:%s --- POST: hash: %s type: %s Portion: %s/%s" % (x, PORT, HASH, TYPE, i, TOTAL_WORKERS))
        except requests.exceptions.RequestException:
            print("encountered an error")
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
