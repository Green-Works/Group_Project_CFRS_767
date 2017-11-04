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
DICTIONARY_PATH = "/home/ec2-user/efs/"
HOSTNAME = ""
STATUS = "Waiting for work"
HASHCAT = "/usr/bin/hashcat"

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

#This function runs hashcat
def run_hashcat(inputHash, hashTypeNumber, DICTIONARY_PATH):
    logging.debug("starting hashcat")
     
        #Set this to where ever we want the password file to be on the AWS instance.  This variable must stay local for this to work
    PASSWORD_PATH = "/tmp/pass.txt"
    global status
    attackType = 0

    status = 'working'

    #check for a previous version of the temp file pass.txt. if it exists, deletes it
    if os.path.isfile(PASSWORD_PATH):
        logging.debug('Removing previous version of pass.txt file...')
        os.unlink(PASSWORD_PATH)

    logging.info('Building string to pass to command shell...')

    m = "{0} {1}".format("-m", hashTypeNumber)
    o = "{0} {1}".format("-o", PASSWORD_PATH)
    f = "{0}".format('--outfile-format=2')
    logging.debug('The string passed is: {0} -a {1} {2} {3} {4} {5} {6} {7} --show'.format(HASHCAT, attackType, m, o, f, '--force', inputHash, DICTIONARY_PATH))

    #First the program checks the potfile to see if the password has been cracked by running with the --show option
    potFileCheck = subprocess.run('{0} -a {1} {2} {3} {4} {5} {6} {7} --show'.format(HASHCAT, attackType, m, o, f, '--force', inputHash, DICTIONARY_PATH), stderr=subprocess.PIPE, shell=True)
    print(potFileCheck.stdout)

    #It then checks the pass.txt file that was created.
    check = open(PASSWORD_PATH, 'r', encoding="utf-8")
    PWD = check.readline()
    check.seek(0)
    check.close()
    #If pass.txt empty it runs hashcat.
    if PWD == "":
        logging.debug('Password not found in potfile. Attempting to crack it...')
        result = subprocess.run('{0} -a {1} {2} {3} {4} {5} {6} {7}'.format(HASHCAT, attackType, m, o, f, '--force', inputHash, DICTIONARY_PATH), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        print(result.stdout)
        logging.debug('The string passed was: {0} -a {1} {2} {3} {4} {5} {6} {7}'.format(HASHCAT, attackType, m, o, f, '--force', inputHash, DICTIONARY_PATH))

        #Once hashcat is done, it rechecks pass.txt to see if hashcat found a password
        recheck = open(PASSWORD_PATH, 'r', encoding="utf-8")
        PWD2 = recheck.readline()
        recheck.close()
        #If pass.txt is empty, hashcat did not find a password
        if PWD2 == "":
            status = 'unsuccessful. Password not found'
            print(status)
        #If there is an entry, the program gets the password from the pass.txt file
        else:
            status = 'Work done. Password is: {0}'.format(PWD2)
            print(status)
    #If the password is in the potfile, the program gets it from pass.txt
    else:
        logging.debug('Password cracked: ' + PWD)
        status = 'Work done. Password is: {0}'.format(PWD)
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
            HASHCAT_PID = run_hashcat(HASH, TYPE, WNUM, TOTAL_WORKERS)
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
