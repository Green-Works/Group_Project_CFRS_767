#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script takes a text file of passwords and divides it into separate documents
based on user input.
Written in Python 3.6

TODO:
    turn this script into a function to be called by our password cracker program.

"""

import sys
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# Comment out the line below to enable logging to the terminal
logging.disable(logging.CRITICAL)

nodes = 0
passwordCounter = 0
test = 'False'
logging.info(type(test))

# Ensure the user enters an integer greater than 0 for the number of nodes
while test == 'False':
    try:
        nodes = (int(input("Enter the number of AWS instances that will be used (cannot be 0): ")))
        logging.debug("nodes is: " + str(nodes))
    except ValueError:
        print("Entry was not valid")
        logging.error("Incorrect input entered by user")
        continue
    else:
        if nodes > 0:
            test = 'True'

# Read through the password list and build an array of all the passwords
# Right now the destination to the dictionary is hard coded, but can be changed
# to accept user input
try:
    myfile = open('J:\\CFRS 767\\GroupProject\\test_dictionary.txt', 'r', encoding="utf-8")
    # Count the number of passwords
    for line in myfile:
        passwordCounter += 1
    myfile.close()
except FileNotFoundError:
    msg = "Cannot find the dictionary. Exiting program."
    print(msg)
    logging.error(msg)
    sys.exit(1)


# Determine how many passwords will be passed to each node.
logging.debug("passwordCounter is: " + str(passwordCounter))
countPerNode = int((passwordCounter / nodes))
logging.debug("countPerNode is: " + str(countPerNode))

myfile = open('J:\\CFRS 767\\GroupProject\\test_dictionary.txt', 'r', encoding="utf-8")
for i in range(nodes):
    # create a password sheet for each node
    filename = "{0}of{1}.txt".format(i + 1, nodes)
    o = open(filename, "w", encoding="utf-8")
    logging.debug("Creating wordlist " + filename)

    # for each new password list that is not the last password list, enter passwords
    for j in range(countPerNode):
        o.write(str(myfile.readline()))
    o.close()

# for the last password list write all remaining passwords from the original list
for line in myfile:
    o = open("{}of{}.txt".format(nodes, nodes), "a", encoding="utf-8")
    o.write(str(line.strip()) + "\n")

o.close()
myfile.close()
print("The program has completed. You should have {} newly created split password lists.".format(nodes))
