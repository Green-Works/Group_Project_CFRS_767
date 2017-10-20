#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 10:57:43 2017
SEE THE INLINE COMMENTS FOR CHANGES THAT NEED TO BE MADE FOR THIS TO RUN IN A
NON-VM ENVIRONMENT.

TODO: remember to remove the --force line from the string in the final version
or it will greatly slow down the cracking
"""
import subprocess
import logging
import os

# Set Logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

inputHash = '98ad1a951a54c8369807f8e0b4adb781'
status = 'Waiting for work...'
hashTypeNumber = 0
#edit the below line to match your dictionary location
DICTIONARY_PATH = "/usr/share/wordlists/rockyou.txt"
#edit the below line to match your hashcat location
HASHCAT = "/usr/bin/hashcat"


def run_hashcat(inputHash, hashTypeNumber, DICTIONARY_PATH):

    #Set this to where ever we want the password file to be on the AWS instance.  This variable must stay local for this to work
    PASSWORD_PATH = "/root/Desktop/pass.txt"
    global status
    attackType = 0

    status = 'Working'

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
            status = 'Work completed. Password not found'
            print(status)
        #If there is an entry, the program gets the password from the pass.txt file
        else:
            status = 'Work completed. Password is: {0}'.format(PWD2)
            print(status)
    #If the password is in the potfile, the program gets it from pass.txt
    else:
        logging.debug('Password cracked: ' + PWD)
        status = 'Work completed. Password is: {0}'.format(PWD)

run_hashcat(inputHash, hashTypeNumber, DICTIONARY_PATH,)
