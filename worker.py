#!/usr/bin/python3
'''
############################################################################
#
#   CFRS-767 Group Project - worker.py
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
#       - re
#       - logging
#       - http.server
#       - subprocess
#       - os
#   SCRIPT VER: 1.0
#   REQURIED FILES:
#       - dictionary file. This will be in form 'XofY.txt' from job_manager.py
#   TODO:
#
#
###########################################################################
#
# DESCRIPTION:
#       This script is the worker for a distributed processing
#        engine to crack passwords with hashcat. This script runs as a
#        service that listens for commands from the job_manager.py script
#        then starts an instance of hashcat with data sent form the job
#        manager.
#
###########################################################################
'''

#Import modules
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import base64
import logging
import os
import time
import subprocess
import urllib.parse

#Set Logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

#Set user Config Variables
PORT = 24998
DICTIONARY_PATH = "/home/ec2-user/efs/"
HASHCAT = "/usr/bin/hashcat"

#Non-User Config Variables (don't change these)
HOSTNAME = ""
STATUS = "Waiting for work"

#This function kills the hashcat process
def state_reset(RESET_MSG):
    global STATUS
    if "stop" in RESET_MSG.decode("utf-8"):
        STATUS = "Waiting for work"
        logging.info("Status reset")
        msg = 0
    else:
        logging.error("Error changing status")
        msg = 1
    return(msg)

#This function runs hashcat
def run_hashcat(inputHash, hashTypeNumber, WNUM, TOTAL_WORKERS):
    logging.debug("starting hashcat")
    logging.debug("Hash is {}".format(inputHash))
    DICTIONARY_FILE = str(WNUM) + "of" + str(TOTAL_WORKERS) + ".txt"
    DICTIONARY_PATH_2 = str(DICTIONARY_PATH) + str(DICTIONARY_FILE)
        #Where the password file is on the AWS instance. This variable must stay local.
    PASSWORD_PATH = "/tmp/pass.txt"
    global STATUS
    attackType = 0
    STATUS = 'working'

    #check for a previous version of the temp file pass.txt. if it exists, deletes it
    if os.path.isfile(PASSWORD_PATH):
        logging.debug('Removing previous version of pass.txt file...')
        os.unlink(PASSWORD_PATH)

    logging.debug('Building string to pass to command shell...')

    m = "{0} {1}".format("-m", hashTypeNumber)
    o = "{0} {1}".format("-o", PASSWORD_PATH)
    f = "{0}".format('--outfile-format=2')
    logging.debug('The string passed is: {0} -a {1} {2} {3} {4} \'{5}\' {6} --show'.format(HASHCAT, attackType, m, o, f, inputHash, DICTIONARY_PATH_2))

    #First the program checks the potfile to see if the password has been cracked by running with the --show option
    potFileCheck = subprocess.run('{0} -a {1} {2} {3} {4} \'{5}\' {6} --show'.format(HASHCAT, attackType, m, o, f, inputHash, DICTIONARY_PATH_2), stderr=subprocess.PIPE, shell=True)
    print(potFileCheck.stdout)

    #It then checks the pass.txt file that was created.
    check = open(PASSWORD_PATH, 'r')
    PWD = check.readline()
    check.seek(0)
    check.close()
    #If pass.txt empty it runs hashcat.
    if PWD == "":
        logging.debug('Password not found in potfile. Attempting to crack it...')
        result = subprocess.run('{0} -a {1} {2} {3} {4} \'{5}\' {6}'.format(HASHCAT, attackType, m, o, f, inputHash, DICTIONARY_PATH_2), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        print(result.stdout)
        logging.debug('The string passed was: {0} -a {1} {2} {3} {4} \'{5}\' {6}'.format(HASHCAT, attackType, m, o, f, inputHash, DICTIONARY_PATH_2))

        #Once hashcat is done, it rechecks pass.txt to see if hashcat found a password
        recheck = open(PASSWORD_PATH, 'r')
        PWD2 = recheck.readline()
        recheck.close()
        #If pass.txt is empty, hashcat did not find a password
        if PWD2 == "":
            STATUS = 'Unsuccessful. Password not found'
            logging.info("{}".format(STATUS))
            time.sleep(5)
        #If there is an entry, the program gets the password from the pass.txt file
        else:
            STATUS = 'Work done. Password is: {0}'.format(PWD2)
            logging.info("{}".format(STATUS))
    #If the password is in the potfile, the program gets it from pass.txt
    else:
        STATUS = 'Work done. Password is: {0}'.format(PWD)
        logging.info("{}".format(STATUS))

#Configure the WORKER_SERVICE_OPTIONS
class WORKER_SERVICE_OPTIONS(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self.wfile.write(bytes("worker", "utf-8"))
    def do_GET(self):
        if self.path == "/status":
            self._set_response()
            logging.debug("STATUS is: {}".format(STATUS))
            self.wfile.write(bytes(STATUS, "utf-8"))
        else:
            self.wfile.write(bytes("Unrecognized request: {}".format(self.path), "utf-8"))
            self.send_response(201)

            '''
            The Job manager sends the hash, type of hash, worker number, and total amount of workers to each worker
            to start processing. The code below parses that information using regular expressions
            '''
    def do_POST(self):
        if self.path == "/start":
            logging.info("incoming http: {}".format(self.path))
            # This saves the POST request to a string called "post_data"
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logging.debug("The post request is: {}".format(post_data))

            #The section below parses the POST request for the required variables.
            HASH = re.search('(?<=hash\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)
            HASH2 = urllib.parse.unquote(HASH)
            logging.debug("The string passed to hashcat is: {}".format(HASH2))
            TYPE = re.search('(?<=type\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)
            WNUM = re.search('(?<=wnum\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)
            TOTAL_WORKERS = re.search('(?<=totalw\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)

            #start the hashcat process and track the process ID
            HASHCAT_PID = run_hashcat(HASH2, TYPE, WNUM, TOTAL_WORKERS)
            logging.info("Hashcat started on worker {}. Process ID {}".format(WNUM, HASHCAT_PID))
            self._set_response()

        #Stop commands are also sent via POST
        elif self.path == "/stop":
            logging.info("incoming http: {}".format(self.path))
            #This saves the POST request to a string called "post_data"
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logging.debug("The post request is: {}".format(post_data))
            #This is the call to kill the hashcat process. The job manager will send a GET /stop request
            # to tell the worker to stop processing because another worker was successful
            STATE = state_reset(post_data)
            logging.info("Worker Reset. New state is: {}".format(STATE))
            self._set_response()

        else:
            self.send_response(201)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            logging.error("Bad Post Request")

#Set the worker service name and options
WORKER_SERVICE = HTTPServer((HOSTNAME, PORT), WORKER_SERVICE_OPTIONS)

#Start the service as a loop
try:
    logging.info("Starting worker: {}".format(HOSTNAME))
    logging.info("Worker listening on port: {}".format(PORT))
    WORKER_SERVICE.serve_forever()
except KeyboardInterrupt:
    pass
    WORKER_SERVICE.server_close()
    logging.info("Shutting down worker: {} on port {}".format(HOSTNAME, PORT))
