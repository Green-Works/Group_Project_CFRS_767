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
import time

#Set Logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

#Set Config Variables
PORT = 24998
DICTIONARY_PATH = "/home/$USER/Dictionary/"
HOSTNAME = ""
STATUS = "start"
HASHCAT = "./usr/local/bin/hashcat"

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
def start_hashcat(inputHash, hashType, WNUM, TOTAL_WORKERS):
    logging.debug("starting hashcat")
    logging.debug("hash: {}, type: {}, this is worker#: {} of {}".format(HASH, TYPE, WNUM, TOTAL_WORKERS))
    m = "{} {}".format("-m", TYPE)
    
    #force hashType to uppercase to match the dictionary
    hashType = hashType.upper()
    
    # hastTypes is a dictionary that links the hash algorithm to its hashcat hash number
    hashTypes = {'MD5' : '0', 'MD5Crypt' : '500', 'SHA1' : '100', 'SHA-512(Unix)' : '1800', 'NTLMV1' : '1000', 'NTLMV2' : '1000', 'WPA' : '2500', 'WPA2' : '2500', 'Bcrypt': '3200', 'NTLM' : '1000'}

    attackType = 0

    #edit the below line to match your dictionary location
    DICTIONARY_PATH = "/usr/share/wordlists/rockyou.txt"
    HOSTNAME = ""
    STATUS = "start"
    
    #edit the below line to match your hashcat location
    HASHCAT = "/usr/bin/hashcat"

    logging.info('Building string to pass to command shell...')

    m = "{0} {1}".format("-m", hashTypes[hashType])
    o = "{0} {1}".format("-o", '~/Desktop/pass.txt')
    f = "{0}".format('--outfile-format=2')
    logging.debug(hashType)
    logging.debug(inputHash)
    logging.debug('The string passed is: {0} -a {1} {2} {3} {4} {5} {6} {7} --show'.format(HASHCAT, attackType, m, o, f, '--force', inputHash, DICTIONARY_PATH))
    
    #First the program checks the potfile to see if the password has been cracked by running with the --show option
    subprocess.call('{0} -a {1} {2} {3} {4} {5} {6} {7} --show'.format(HASHCAT, attackType, m, o, f, '--force', inputHash, DICTIONARY_PATH), shell=True)

    # Wait to create the pass.txt file, otherwise the program fails
    time.sleep(2)
    
    #It then checks the pass.txt file that was created. If it is empty it runs hashcat. If there is an entry, that means the password had been seen before and it gets the password from the pass.txt file
    check = open('pass.txt', 'r', encoding="utf-8")
    PWD = check.readline()
    logging.debug('Password from pass.txt is: ' + PWD)
    if  PWD == "":
        logging.debug('Password not found in potfile. Attempting to crack it...')
        subprocess.call('{0} -a {1} {2} {3} {4} {5} {6} {7}'.format(HASHCAT, attackType, m, o, f, '--force', inputHash, DICTIONARY_PATH), shell=True)
    else:
        logging.debug('Password cracked: ' + PWD)
    check.close()
    #get_PID()
    
############################################################################################################
#def get_PID():
#    """This function returns the PID of hashcat as a string.  It requires the pgrep tool. Be sure to change the file path of pgrep to that of the machine this will be used on."""
#    #pgrepFilePath = '/usr/bin/pgrep'
#    PID = proc.pid
#    #PID = subprocess.call('{0} -f {1}'.format(pgrepFilePath, 'hashcat'), shell=True)
#    print('Hashcat PID is: {}'.format(str(PID)))
#    #return(PID)   
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
