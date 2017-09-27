#!/usr/bin/python3

'''
This program uses the current number of nodes and a file location to check if it has the dictionaries necessary
to perform the job
'''

import os
import re
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

DICTIONARY = "/home/mckelvey/Dictionary/dictionary.txt"
WORKER_LIST = ['127.0.0.1', '192.168.246.141', '192.168.246.142', '192.168.246.143']
#WORKER_LIST = ['127.0.0.1', '192.168.246.141']

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
        myfile = open(DICTIONARY, 'r', encoding="utf-8")
        # Count the number of passwords
        for line in myfile:
            passwordCounter += 1
        myfile.close()
    except FileNotFoundError:
        logging.error("Cannot find the dictionary. Exiting program.")
        exit(1)

    countPerNode = int((passwordCounter / NODES))
    myfile = open(DICTIONARY, 'r', encoding="utf-8")

    for i in range(NODES):
        # create a dictionary file for each worker
        filename = os.path.dirname(DICTIONARY) + "/{0}of{1}.txt".format(i + 1, NODES)
        o = open(filename, "w", encoding="utf-8")
        logging.debug("Creating wordlist {}".format(filename))

        # for each new password list that is not the last password list, enter passwords
        for j in range(countPerNode):
            o.write(str(myfile.readline()))
        o.close()
    filename = os.path.dirname(DICTIONARY) + "/{}of{}.txt".format(NODES, NODES)
    o = open(filename, "a", encoding="utf-8")
    for line in myfile:
        o.write(str(line.strip()) + "\n")
    o.close()
    myfile.close()

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
        removeOldDictionaries(DICTIONARY)
        dictionary_splitter(NODES, DICTIONARY)


prev_dictionary_test(len(WORKER_LIST), DICTIONARY)