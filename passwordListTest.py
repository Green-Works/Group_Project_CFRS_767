#!usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 08:48:41 2017

@author: Brian Daugette
python 3.6
This script determines if the password list needs to be split. It checks the
password storage location, if that location does not exist, or is empty then
the script will tell the main program to run the dictionary splitter script.
If the shared storage location does exist, it checks for previously split
password lists. If they do not exist, it tells the main program to run the
dictionary splitter. If they do exist it uses the name of the text files (xofy.txt)
to determine how many workers there previously were (the y value in the text
file's name).  TODO:  If that is the same as the current number of workers, then this
script notifies the main program to go ahead and run, as the workers will already
have the correct split password lists. If they are different then this script
will tell the main program to run the dictionary splitter script again.

TODO: Determine if this script needs to delete the old password lists if they
exist, or if it should call another script or function to do this work.
"""

import os
import re
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

def callDictionarySplitter():
    """This function calls the dictionary splitter script to create new dictionaries"""
    logging.debug("This script has determined that new dictionaries need to be created.\nCalling the dictionary splitter script.")


def getNodeNumber(file):
    """This function checks the name of a text file to get the number of worker nodes that were previously used."""
    logging.info("file received: {}".format(file))
    logging.info("Getting previous number of nodes from the file..")
    nodes = file[-5]
    logging.info("Previous number of nodes used was: {}".format(nodes))
    # TODO: this should return the number of nodes to the main program


passwordLoc = 'J:\\CFRS 767\\GroupProject\\testDictLocation\\' # change this to match the password list location
splitDictRegex = re.compile(r'\dof\d.txt')  # this is regex to detect the split dictionaries in the folder

# check if the password storage location exists (this location needs to match
# the location of the password lists)
if os.path.isdir(passwordLoc):
    logging.debug("Directory exists.")
    # test if the directory contains files
    # TODO: check for condition if directory exists, but is completely empty. This should not happen as there should always be the master password list in this directory if it exists.
    # create a list of files in the directory
    for file in os.listdir(passwordLoc):
        # check if there are dictionaries already in the directory by reviewing the list of files for files that match the naming scheme of the split dictionaries
        if splitDictRegex.search(file):
            # if a dictionary is found, call the getNodeNumber function
            logging.info("a dictionary was found: {}. Getting the node number.".format(file))
            getNodeNumber(file)
            break
        else:
            # if there are no dictionaries, call the dictionary spliiter function
            callDictionarySplitter()
else:
    logging.debug("Directory does not exist.\nRun the dictionary splitter function to create new dictionaries.")
    callDictionarySplitter()



