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
import time
import logging

# Set Logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)


def run_hashcat(inputHash, hashType):

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

    # Wait to create the pass.txt file
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

#def get_PID():
#    """This function returns the PID of hashcat as a string.  It requires the pgrep tool. Be sure to change the file path of pgrep to that of the machine this will be used on."""
#    #pgrepFilePath = '/usr/bin/pgrep'
#    PID = proc.pid
#    #PID = subprocess.call('{0} -f {1}'.format(pgrepFilePath, 'hashcat'), shell=True)
#    print('Hashcat PID is: {}'.format(str(PID)))
#    #return(PID)


inputHash = 'ec48d0c9d35e855c53d2409d0a5a9c2f'
run_hashcat(inputHash, 'md5')
#get_PID()
