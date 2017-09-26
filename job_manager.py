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
#       - time
#		- logging
#       - netifaces
#       - netaddr
#       - socket
#       - requests
#   SCRIPT VER: 0.6
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
import logging
import netifaces
import netaddr
import socket
import requests
import time
import sys
import re

#Set config variables
#enter location of the dictionary file
DICTIONARY = ""
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)



'''
# Parse inputs
# Question: do we only want to pass a single hash or have the option to pass
# a text file of several hashes (as long as the hashes are the same type)?
'''

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
    logging.debug("Searching for workers on local network using tcp port {}".format(PORT))
    for X in netifaces.interfaces():
        INTERFACE_DATA = netifaces.ifaddresses(X).get(netifaces.AF_INET)
        IP = INTERFACE_DATA[0]['addr']
        NETMASK = INTERFACE_DATA[0]['netmask']
        CIDR = netaddr.IPAddress(NETMASK).netmask_bits()
        netaddr.IPAddress(IP)
        NETWORK = IP + "/" + str(CIDR)
        netaddr.IPNetwork(NETWORK)
        logging.debug("Interface: {} \tIP: {}\tNETMASK: {}".format(X, IP, CIDR))
        type(IP)
        #Special check for the local host otherwise the scan would take forever since localhost CIDR is /8
        if IP[0:3] == "127":
            is_open = is_port_open(IP, PORT)
            if is_open is True:
                WORKER_LIST.extend([str(IP)])
                logging.debug("port {} open on localhost".format(PORT))
            else:
                logging.debug("port {} is NOT open on localhost".format(PORT))
        #this is the scan for all other interfaces. Variable 'Y' contains a single ip address in the CIDR range
        else:
            for Y in netaddr.IPNetwork(NETWORK):
                if str(Y) == IP:
                    logging.debug("skipping scan on IP: {}".format(str(Y)))
                else:
                    is_open = is_port_open(str(Y), PORT)
                    if is_open is True:
                        WORKER_LIST.extend([str(Y)])
                        logging.debug("port {} open on IP {}".format(PORT, str(Y)))
        logging.debug("Workers found: {}".format(WORKER_LIST))
    return(WORKER_LIST)

#### this is where brian's dictionary remover/checker goes
def removeOldDictionaries():
    print("some stuff goes here")

#This script takes a text file of passwords and divides it into separate documents based on user input.
def dictionarySplitter(nodes, DICTIONARY):
    passwordCounter = 0
    logging.debug("The worker count is : {} and the dictionary file is {}".format(nodes, DICTIONARY))
    try:
        myfile = open(DICTIONARY, 'r', encoding="utf-8")
        # Count the number of passwords
        for line in myfile:
            passwordCounter += 1
        myfile.close()
    except FileNotFoundError:
        msg = "Cannot find the dictionary. Exiting program."
        print(msg)
        logging.error(msg)
        exit(1)
    logging.debug("passwordCounter is: " + str(passwordCounter))
    countPerNode = int((passwordCounter / nodes))
    logging.debug("countPerNode is: " + str(countPerNode))

###### this section needs debugging. the dictionary is split, but placed in the wrong path #########
    myfile = open(DICTIONARY, 'r', encoding="utf-8")
    for i in range(nodes):
        # create a password sheet for each node
        filename = "{0}of{1}.txt".format(i + 1, nodes)
        o = open(filename, "w", encoding="utf-8")
        logging.debug("Creating wordlist {}".format(filename))

        # for each new password list that is not the last password list, enter passwords
        for j in range(countPerNode):
            o.write(str(myfile.readline()))
        o.close()

    # for the last password list write all remaining passwords from the original list
    for line in myfile:
        o = open("{}of{}.txt".format(nodes, nodes), "a", encoding="utf-8")
        o.write(str(line.strip()) + "\n")

    o.close()
    myfile.close()
    print("The program has completed. You should have {} newly created split password lists.".format(nodes))

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
            print("http://{}:{} --- POST: hash: {} type: {} Portion: {}/{}".format(x, PORT, HASH, TYPE, i, TOTAL_WORKERS))
        except requests.exceptions.RequestException:
            print("encountered an error")
        i += 1

#This should send a 'stop' post to the workers and ensure they go down gracefully
## needs some error checking to make sure the servers go back to a 'ready' state
def worker_stop(WORKER_LIST, PORT):
    payload = "stop"
    for X in WORKER_LIST:
        url = "http://" + str(X) + ":" + str(PORT)
        stop = url + "/stop"
        print("Stopping work on {}".format(url))
        try:
            r = requests.post(stop, data=payload)
            print(r.status_code)
        except requests.exceptions.RequestException:
            print("encountered an error stopping worker {}".format(url))


#This function checks the status of the workers
def worker_status(WORKER_LIST, PORT):
    for X in WORKER_LIST:
        logging.debug("Checcking the status of worker at http://{}:{}".format(X, PORT))
        url = "http://" + str(X) + ":" + str(PORT)
        print(url)
        try:
            r = requests.get(url + "/status")
            print(r.content)
            if "working" in str(r.content):
                print("worker http://{}:{} is working".format(X, PORT))
            elif "ready" in str(r.content):
                print("worker http://{}:{} is ready for work".format(X, PORT))
            elif "done" in str(r.content):
                ##### needs formatting #####
                print("password found! {}".format(r.content))
                worker_stop(WORKER_LIST, PORT)
                exit(0)
            elif "error" in str(r.content):
                print("worker http://{}:{} had an error and is not working".format(X, PORT))
            else:
                print("status unknown")
        except requests.exceptions.RequestException:
            print("there was an error contacting worker http://{}:{}".format(X, PORT))


# troubleshooting. modified this to use logging. no need to delete as it can be used later during debugging
logging.debug("String is: {}".format(ARGS.string))
logging.debug("Type is: {}".format(ARGS.type))
logging.debug("Port is: {}".format(ARGS.port))

# Error check the input
## there could be a function statement that checks whether or not the string is actually an md5/ntlm/etc.
if ARGS.type not in ["ntlm", "md5"]:
    print("ERROR: Invalid input. [{}] is not an acceptable input.".format(ARGS.type))
    exit(1)

# Main logic

#populate the list of available workers
WORKER_LIST = worker_discover(ARGS.port)
print("The workers found are {}".format(WORKER_LIST))
'''
THis is where a call to brian's dictionary divider goes
Some logic needs to be added to determine when each these functions needs to be ran
'''
dictionarySplitter(len(WORKER_LIST), DICTIONARY)
#Send out the work
send_work(WORKER_LIST, ARGS.string, ARGS.type, ARGS.port)

#Continuously check the workers every five seconds for their status. The worker_status function will shut down
#the workers when it finishes
while True:
    logging.debug("Checking worker status")
    worker_status(WORKER_LIST, ARGS.port)
    time.sleep(5)
