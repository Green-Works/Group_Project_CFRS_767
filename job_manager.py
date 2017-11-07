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
#       - logging
#       - netifaces
#       - netaddr
#       - socket
#       - requests
#   SCRIPT VER: 1.0a
#   REQURIED FILES:
#       - dictionary file. Set config variable "DICTIONARY" down below.
#   TODO:
#       make dictionary variable a user input OR make the PORT variable a config variable
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
import os
import re

#Set config variables
DICTIONARY = "/tmp/rockyou.txt"
HASH_VALUES = {'MD5': 0, 'MD5CRYPT': 500, 'SHA1': 100, 'SHA512UNIX':1800, 'NTLM': 1000, 'NTLM2': 5600, 'WPA': 2500, 'BCRYPT': 3200 }
PORT = 24998
MANUAL_WORKER_LIST = ['127.0.0.1']

# Set Logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

# Parse inputs
PARSE = argparse.ArgumentParser(description="Distributed dictionary attack on a hash!")
PARSE.add_argument("-s", "--string", help="the hash string to be cracked")
PARSE.add_argument("-t", "--type", help="the type of hash supplied. Supported options are {}".format(HASH_VALUES.keys()))
PARSE.add_argument("-m", "--mode", choices=['auto','manual'], help="Choose worker discovery mode: auto | manual ")
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
'''

def worker_discover(PORT, MODE):
    global MANUAL_WORKER_LIST
    WORKER_LIST = []
    if MODE == "manual":
        logging.debug("Mode is manual. Checking manually entered workers")
        for X in MANUAL_WORKER_LIST:
            is_open = is_port_open(X, PORT)
            if is_open is False:
                logging.error("ERROR: Worker {} is not up. Please start worker on this host or disable this IP. Exiting.".format(X))
                exit(1)
            else:
                logging.debug("All workers present and accounted for. Using these workers {}".format(MANUAL_WORKER_LIST))
                WORKER_LIST = MANUAL_WORKER_LIST
    elif MODE == "auto":
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
    else:
        logging.error("Unknown mode {}".format(MODE))
    return(WORKER_LIST)

#dictionary remover/checker
def removeOldDictionaries(DICTIONARY):
    passwordLoc = os.path.dirname(DICTIONARY) + "/"
    splitDictRegex = re.compile(r'\dof\d.txt')  # this is regex to detect the split dictionaries in the folder.  This will be used to determine which files to delete.
    logging.info("Checking for old split dictionaries to delete...")
    for file in os.listdir(passwordLoc):
        if splitDictRegex.search(file):
            # if a split dictionary is found, remove it
            logging.info("an old dictionary was found: {}. Removing it".format(file))
            os.remove(passwordLoc + file)
        else:
            logging.info("No old dictionaries to delete.")

#This script takes a text file of passwords and divides it into separate documents based on user input.
def dictionary_splitter(NODES, DICTIONARY):
    passwordCounter = 0
    logging.debug("NODES: {}, DICTIONARY: {}".format(NODES, DICTIONARY))
    try:
        #myfile = open(DICTIONARY, 'r', encoding="utf-8", errors="ignore")
        myfile = open(DICTIONARY, 'r', encoding="utf-8", errors="ignore")
        # Count the number of passwords
        for line in myfile:
            passwordCounter += 1
        myfile.close()
    except FileNotFoundError:
        logging.error("Cannot find the dictionary. Exiting program.")
        exit(1)

    countPerNode = int((passwordCounter / NODES))
    myfile = open(DICTIONARY, 'r')

    for i in range(NODES):
        # create a dictionary file for each worker
        filename = os.path.dirname(DICTIONARY) + "/{0}of{1}.txt".format(i + 1, NODES)
        o = open(filename, "w")
        logging.debug("Creating wordlist {}".format(filename))

        # for each new password list that is not the last password list, enter passwords
        for j in range(countPerNode):
            o.write(str(myfile.readline()))
        o.close()
    filename = os.path.dirname(DICTIONARY) + "/{}of{}.txt".format(NODES, NODES)
    o = open(filename, "a")
    for line in myfile:
        o.write(str(line.strip()) + "\n")
    o.close()
    myfile.close()

#This function checks the name of a text file to get the number of worker nodes that were previously used.
def prev_dictionary_test(NODES, DICTIONARY):
    logging.debug("Searching for previous dictionaries")
    PATH = os.path.dirname(DICTIONARY)
    count = 0
    #First, create a list of dictionaries that should be there.
    files_that_should_exist = []
    for x in range(NODES+1):
        if x == 0:
            pass
        else:
            files_that_should_exist.append("{}of{}.txt".format(x, NODES))
    logging.debug("Expecting to see the following files: {}".format(files_that_should_exist))
    #Next, check to see if a file that matches the expected file list exists
    # if it exists increment the counter, if not, pass
    # the logic isn't fool-proof here. TODO: improve this algorithm slightly
    for FILE in os.listdir(PATH):
        if FILE in files_that_should_exist:
            count = count + 1
        else:
            pass
    logging.debug("Found split dictionaries: {}".format(count))
    # if the count of files matches the number of nodes  all the correct dictionaries are in place
    # else, clean up the dictionary folder and create new split dictionaries
    if count == NODES:
        logging.info("All split dictionaries are present.")
        return()
    else:
    #   removeOldDictionaries(DICTIONARY)
        dictionary_splitter(NODES, DICTIONARY)

# This is the part of the script that sends a POST/GET message to the workers with the
def send_work(WORKER_LIST, HASH, TYPE, PORT):
    logging.info("sending work...")
    TOTAL_WORKERS = len(WORKER_LIST)
    i = 1
    for x in WORKER_LIST:
        url = "http://" + str(x) + ":" + str(PORT)
        start = url + "/start"
        logging.debug("sending work to {}".format(url))
        payload = {'hash': HASH, 'type': TYPE, 'wnum': i, 'totalw': TOTAL_WORKERS}
        try:
            r = requests.post(start, data=payload)
            #logging.debug("POST command for worker: {}".format(r.url))
            logging.info("http://{}:{} --- POST: hash: {} type: {} Portion: {}/{}".format(x, PORT, HASH, TYPE, i, TOTAL_WORKERS))
        except requests.exceptions.RequestException:
            logging.info("encountered an error")
        i += 1

#This should send a 'stop' post to the workers and ensure they go down gracefully
## needs some error checking to make sure the servers go back to a 'ready' state
def worker_stop(WORKER_LIST, PORT):
    payload = "stop"
    for X in WORKER_LIST:
        url = "http://" + str(X) + ":" + str(PORT)
        stop = url + "/stop"
        logging.info("Stopping work on {}".format(url))
        try:
            r = requests.post(stop, data=payload)
            logging.debug(r.status_code)
        except requests.exceptions.RequestException:
            logging.info("encountered an error stopping worker {}".format(url))

#This function checks the status of the workers
def worker_status(WORKER_LIST, PORT):
    for X in WORKER_LIST:
        logging.debug("Checcking the status of worker at http://{}:{}".format(X, PORT))
        url = "http://" + str(X) + ":" + str(PORT)
        logging.debug("checking status of worker: {}".format(url))
        try:
            r = requests.get(url + "/status")
            #print(r.content)
            if "working" in str(r.content):
                logging.info("worker http://{}:{} is working".format(X, PORT))
            elif "ready" in str(r.content):
                logging.info("worker http://{}:{} is ready for work".format(X, PORT))
            elif "unsuccessful" in str(r.content):
                print("worker {} completed and did not find the password".format(X))
                WORKER_LIST.remove(X)
            elif "done" in str(r.content):
                print("FOUND: {}".format(str(r.content.decode("utf-8"))))
                worker_stop(WORKER_LIST, PORT)
                exit(0)
            elif "error" in str(r.content):
                logging.error("worker http://{}:{} had an error and is not working".format(X, PORT))
            else:
                logging.error("status of worker {} unknown".format(url))
        except requests.exceptions.RequestException:
            logging.error("there was an error contacting worker http://{}:{}".format(X, PORT))
        return(WORKER_LIST)

# troubleshooting. modified this to use logging. no need to delete as it can be used later during debugging
logging.debug("String is: {}".format(ARGS.string))
logging.debug("Type is: {}".format(ARGS.type))
logging.debug("Mode is: {}".format(ARGS.mode))

# Error check the input
## TODO: there should be a function statement that checks whether or not the string is actually an md5/ntlm/etc.
#Error check the type
if ARGS.type.upper() not in HASH_VALUES:
    logging.error("ERROR. Hash type not in available values\n Please only use these values {}".format(HASH_VALUES.keys()))
    exit(1)
else:
    logging.debug("Hash code is: {}".format(HASH_VALUES[ARGS.type.upper()]))
    HASHCODE = HASH_VALUES[ARGS.type.upper()]
# Main logic

#populate the list of available workers
WORKER_LIST = worker_discover(PORT, ARGS.mode)
logging.info("The workers found are {}".format(WORKER_LIST))
# Check the dictionary file and split the dictionary if it hasn't already been done
prev_dictionary_test(len(WORKER_LIST), DICTIONARY)
# Send work to each worker
send_work(WORKER_LIST, ARGS.string, HASHCODE, PORT)

#Continuously check the workers every five seconds for their status. The worker_status function will shut down
#the workers when it finishes
while True:
    logging.debug("Checking worker status on workers {}".format(WORKER_LIST))
    if WORKER_LIST == []:
        print("done")
        exit(0)
    else:
        WORKER_LIST = worker_status(WORKER_LIST, PORT)
    time.sleep(5)
