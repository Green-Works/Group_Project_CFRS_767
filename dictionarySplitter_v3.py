#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script takes a text file of passwords and divides it into separate documents
based on user input.
Written in Python 3.6

TODO:
    turn this script into a function to be called by our password cracker program.

"""

import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
# logging.disable(logging.CRITICAL)

nodes = 0
passwordCounter = 0
test = 'false'

# Ensure the user enters an integer greater than 0 for the number of nodes
while test == 'false':
    try:
        nodes = (int(input("Enter the number of AWS instances that will be used (cannot be 0): ")))
        logging.debug("nodes is: " + str(nodes))
    except ValueError:
        print("Entry was not valid")
        logging.error("Incorrect input entered by user")
        continue
    else:
        if nodes > 0:
            test = 'true'

# Read through the password list and build an array of all the passwords
myfile = open('test_dictionary.txt', 'r', encoding="utf-8")

# Count the number of passwords
for line in myfile:
    passwordCounter += 1

myfile.close()


# Determine how many passwords will be passed to each node.
logging.debug("passwordCounter is: " + str(passwordCounter))
countPerNode = int((passwordCounter / nodes))
logging.debug("countPerNode is: " + str(countPerNode))

myfile = open('test_dictionary.txt', 'r', encoding="utf-8")
for i in range(nodes):
    # create a password sheet for each node
    o = open("wordlist_" + str(i + 1) + ".txt", "w", encoding="utf-8")
    logging.debug("Creating wordlist_" + str(i + 1) + ".txt")

    # for each new password list that is not the last password list, enter passwords
    for j in range(countPerNode):
        o.write(str(myfile.readline()))
    o.close()

# for the last password list write all remaining passwords from the original list
for line in myfile:
    o = open("wordlist_" + str(nodes) + ".txt", "w", encoding="utf-8")
    o.write(str(line.strip()) + "\n")

o.close()
myfile.close()










