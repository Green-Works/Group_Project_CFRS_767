#!/usr/bin/python3
'''
This is the framework for the worker script

The communication piece for the job manager is done. The functions between the comment lines need to be written
'''

#Import modules
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import logging
import subprocess

#Set Logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

#Set Config Variables
PORT = 24998
DICTIONARY_PATH = "/home/$USER/Dictionary/"
HOSTNAME = ""
STATUS = "start"

############################################################################################################
#This function reports back the status of hashcat and whether it is working, failed, or found a password
def get_hashcat_status():
    #STATUS = ("ready")
    #STATUS = ("done[password is: 'password']")
    #STATUS = ("error")
    STATUS = ("working")
    return(STATUS)

#This function kills the hashcat process
def kill_hashcat_process(PID):
    logging.info("Stopping hashcat process")
    #msg = 1 #1 for failure to kill hashcat
    msg = 0 #0 for success killing hashcat
    return(msg)

#This function starts the hashcat process
def start_hashcat(HASH, TYPE, WNUM, TOTAL_WORKERS):
    logging.debug("starting hashcat")
    logging.debug("hash: {}, type: {}, this is worker#: {} of {}".format(HASH, TYPE, WNUM, TOTAL_WORKERS))
    var m = "{} {}".format("-m", TYPE)
    hashcatProc = subprocess.Popen(["./hashcat", m, HASH]);
    #PID = 12345 # this should be replaced with the process ID of hashcat
    PID = hashcatProc.pid
    return(PID)
############################################################################################################

#Configure the WORKER_SERVICE_OPTIONS
class WORKER_SERVICE_OPTIONS(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        #self.send_response(200)
        self.wfile.write(bytes("worker", "utf-8"))
    def do_GET(self):
        if self.path == "/status":
            self._set_response()
            #This is the call to get the status of hashcat.
            msg = get_hashcat_status()
            self.wfile.write(bytes(msg, "utf-8"))
        else:
            self.wfile.write(bytes("Unrecognized request: {}".format(self.path), "utf-8"))
            self.send_response(201)

    '''
    The Job manager sends the hash, type of hash, worker number, and total amount of workers to each worker
    to start processing. The code below parses that information using regular expressions
    '''
    def do_POST(self):
        if self.path == "/start":
            logging.debug("incomming http: {}".format(self.path))
            # This saves the POST request to a string called "post_data"
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logging.debug("The post request is: {}".format(post_data))

            #The section below parses the POST request for the required variables.
            HASH = re.search('(?<=hash\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)
            TYPE = re.search('(?<=type\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)
            WNUM = re.search('(?<=wnum\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)
            TOTAL_WORKERS = re.search('(?<=totalw\=)(.*?)(?=[\&|\'])', str(post_data)).group(1)

            #start the hashcat process and track the process ID
            HASHCAT_PID = start_hashcat(HASH, TYPE, WNUM, TOTAL_WORKERS)
            logging.info("Hashcat started on worker {}. Process ID {}".format(WNUM, HASHCAT_PID))

            self._set_response()

        #Stop commands are also sent via POST
        elif self.path == "/stop":
            logging.debug("incomming http: {}".format(self.path))
            #This saves the POST request to a string called "post_data"
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logging.debug("The post request is: {}".format(post_data))
            #This is the call to kill the hashcat process. The job manager will send a GET /stop request
            # to tell the worker to stop processing because another worker was successful
            HASHCAT_KILL = kill_hashcat_process(HASHCAT_PID)
            logging.debug("Hashcat killed?: {}".format(HASHCAT_KILL))
            self._set_response()

        else:
            self.send_response(201)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            logging.error("Bad Post Request")
            # client.close()

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
