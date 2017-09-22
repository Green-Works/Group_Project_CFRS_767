#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 10:04:22 2017
This script removes the old split dictionaries from the shared storage area in
the instance when the user wants to re-run the password cracker, but there is a
different number of worker nodes than there were previously. As of now this
script does not check if the shared storage location exists, as that will have
been previously done by the passwordListTest script that calls this script.
"""

import os
import re
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
logging.disable(logging.CRITICAL)

# This is the location of the shared storage. Will need to change this code to accept this value as a variable from the job manager
passwordLoc = ('J:\\CFRS 767\\GroupProject\\testDictLocation\\')

splitDictRegex = re.compile(r'\dof\d.txt')  # this is regex to detect the split dictionaries in the folder.  This will be used to determine which files to delete.

logging.info("Checking for old split dictionaries to delete...")
for file in os.listdir(passwordLoc):
    if splitDictRegex.search(file):
        # if a split dictionary is found, remove it
        print("an old dictionary was found: {}. Removing it".format(file))
        os.remove(passwordLoc + file)
    else:
        print("No old dictionaries to delete. Exiting.")






