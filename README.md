Distributed Password Cracker
============================

Introduction
------------

This implementation of a distributed password cracker is essentially a
management script with a wrapper script for hashcat. These scripts are meant to
be run on an Amazon Web Services (AWS) platform as the job_manager.py script
contains options to start multiple systems for additional cracking power.

The script framework is coded in Python 3 and has been extensively tested within
Kali Linux on an AWS platform. The script works inside or outside AWS, however,
the ‘-i’ feature will only work within AWS.

 

Prerequisites
-------------

**AWS Command Line Interface**

Prior using the job manager and worker, the AWS Command Line interface (CLI) must be installed on the base image in order to support the creation of new GPU backed instances on the fly.  At a minimum Access and Secret keys must be supplied to the main image that allow for EC2 start/stop actions as well as all EC2 Describe actions.  For instructions on how to install and configure the AWS CLI please read Amazon’s documentation found here: https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html 

**Shared Storage**

To properly take advantage of this framework, shared storage for the dictionary
file should be used. Ideally, an AWS EFS share that contains the dictionary would be
ideal. In this way the job_manager.py script can create dictionaries for the
workers to use. All error checking on dictionaries is done by the job_manager.py
so if an improper dictionary is supplied to the worker.py script or if the
dictionary the worker.py script is non-existent, the script will fail. To ensure
this does not happen, shared storage should be used.

**Modules**

The job_manager.py script requires the following modules:

-   argparse, logging, netifaces, netaddr, socket, requests, time, os, boto3, botocore.exceptions

The worker.py script requires the following modules:

-   re, logging, os, subprocess, HTTPServer, threading, urllib.parse

 

job_manager.py
--------------

Essentially, the job manager is designed to perform the following steps:

1.  Search and/or tests each discovered worker discovered in the subnet

2.  Split the dictionary into smaller files for each worker (e.g. 1of1.txt,
    1of2.txt, 2of2.txt, and so on).

3.  Spin up cloned instances of itself within the AWS framework

4.  Send, via HTTP, to each worker the following information:

    1.  The hash

    2.  The hashcat hash-code

    3.  The worker number (i.e. 1, 2, 3, and so on)

    4.  The total number of workers (i.e. 4, 5, 6, etc.)

5.  Check the work status of each worker

6.  Present the user with the results from each worker

### Usage

This script is the user interface for this framework. In order to get started, a
user must supply the job_manager.py script with a few arguments as input:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-s / --string - The hash string in quotes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-t / --type - The hash type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   The options for this section are case insensitive, but can only be one of
    the following options:

    -   md5, md5crypt, sha1, sha512unix, ntlm, ntlm2, wpa, or bcrypt

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-m / --mode - The mode of worker discovery.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   This determines whether or not the script will automatically discover
    workers on the network or use a pre-populated variable (MANUAL_WORKER_LIST)

    -   The options for “mode” are either “auto” or “manual”

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-i / --instances - number of addtional instances to create
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   This will start *additional* cloned AWS instances. For instantce, -i 3 will
    start 3 *additional* instances bringing the total to 4 AWS instances.
    Currently, there is no feature to match the number of instances to the
    number of hosts present on the network. This option is best used with the
    “-m auto” mode.

### Job_manager.py Configuration

The job_manager.py script has 4 configurable options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DICTIONARY = "/tmp/rockyou.txt"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  DICTIONARY - This is the location of the full dictionary used.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
HASH_VALUES = {'MD5': 0, 'MD5CRYPT': 500, 'SHA1': 100, 'SHA512UNIX':1800, 'NTLM': 1000, 'NTLM2': 5600, 'WPA': 2500, 'BCRYPT': 3200 }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  HASH_VALUES - This is a dictionary of hash types along with their
    corresponding hashcat code. Technically, any supported hashcat hash-type can
    be placed in this dictionary along with its corresponding code.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PORT = 24998
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  PORT - This is the TCP port in which to look for workers on the network. The
    default value is 24998

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MANUAL_WORKER_LIST = ['127.0.0.1', '10.10.10.10']
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  MANUAL_WORKER_LIST - This is the pre-populated list of worker IP addresses.
    This should be set if the user *already* knows the IP addresses of all the
    workers. That way when the user uses the “manual” option, the job_manager.py
    skips a full subnet portscan and operates with just the list described here.

 

worker.py
---------

The worker.py script is meant to be run as a service without any user input. The
script can be installed as a stand-alone script or as a service. The SystemD and
SysV startup scripts are included as a part of the package and installation
instructions are included below.

The worker.py script listens for HTTP GET and POST commands from the job manager
and responds accordingly. If the worker.py script receives a hash, hash-type,
assigned worker number, and total number of workers, the script will attempt to
perform a dictionary attack on the supplied hash using a specific dictionary.

 

### Worker.py Configuration

There are three user configurable variables:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PORT = 24998
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  PORT - This is the TCP port the worker listens on. TCP port 24998 is the
    default configuration.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DICTIONARY_PATH = "/tmp/"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  DICTIONARY_PATH - This is the *path* to the dictionary the worker is
    supposed to use. Do not include the file itself (i.e. /tmp/dictionary.txt)
    as this will generate an error.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
HASHCAT = "/usr/bin/hashcat"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  HASHCAT - This is the complete path to the hashcat binary (e.g.
    /usr/bin/hashcat)

 

### worker.service/worker.init

Since the worker script is meant to act as a perpetual service, supplied are two
startup scripts. The worker.init is meant for systems that use SysV startup
scripts and the worker.service is meant for systems that use SystemD.

 

**SystemD**

To install worker.py as a service on SystemD systems use the following code:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sudo cp worker.py /usr/local/bin/
sudo chmod +x /usr/local/bin/worker.py
sudo cp worker.service /usr/lib/systemd/system/
sudo systemctl enable worker.service
sudo systemctl start worker.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**SysV**

To install worker.py on SysV systems use the following code:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sudo cp worker.py /usr/local/bin/
sudo chmod +x /usr/local/bin/worker.py
sudo cp worker.init /etc/init.d/
sudo chkconfig worker.init on
sudo service worker.init start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example uses
------------

**Cracking an MD5 password**

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./job_manager.py -s '5f4dcc3b5aa765d61d8327deb882cf99' -t md5 -m manual
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command above will employ the job_manager and worker scripts to crack an md5
password. In this scenario the job_manager.py script will only use workers
identified in the “MANUAL_WORKER_LIST” variable.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./job_manager.py -s '5f4dcc3b5aa765d61d8327deb882cf99' -t md5 -m auto
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command above will attempt to crack an md5 password using the automatic
worker discover feature. In this case the “MANUAL_WORKER_LIST” variable is
ignored and the job_manager will auto discover workers present on the network.
Use this option if you are unsure or do not know the IP addresses of systems
with the worker.py script installed and running.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./job_manager.py --string '5f4dcc3b5aa765d61d8327deb882cf99' --type md5 --mode manual
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The example above shows an alternate way of running the first scenario.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./job_manager.py -s '5f4dcc3b5aa765d61d8327deb882cf99' -t md5 -m auto -i 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The above command will start the process and add 2 additional AWS instances for
extra processing power.

ToDo:
-----

1.  bcrypt and wpa aren't working currently

2.  Error check hash input vs. type

3.  update readme.md with AWS stuff

4.  write a testing script

5.  high level visio diagrams for worker, job_manager and complete system.

 
