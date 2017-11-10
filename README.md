Distributed Password Cracker
============================

Introduction
------------

This implementation of a distributed password cracker is essentially a
management script with a wrapper script for hashcat. These scripts are meant to
be run on an Amazon Web Services (AWS) platform as the job_manager.py script
contains options to start multiple systems for additional cracking power.

The script framework is coded in Python 3 and has been extensively tested within
Kali Linux on an AWS platform. Usage outside of AWS is completely possible with
some minor modification.

Prerequisites
-------------

**Shared Storage**

To properly take advantage of this framework, shared storage for the dictionary
file should be used. Ideally, a ECS share that contains the dictionary would be
ideal. In this way the job_manager.py script can create dictionaries for the
workers to use. All error checking on dictionaries is done by the job_manager.py
so if an improper dictionary is supplied to the worker.py script or if the
dictionary the worker.py script is non-existent, the script will fail. To ensure
this does not happen, shared storage should be used.

**Modules**

The job_manager.py script requires the following modules:

-   argparse, logging, netifaces, netaddr, socket, requests, time, os

The worker.py script requires the following modules:

-   re, logging, os, subprocess, codecs, HTTPServer

 

job_manager.py
--------------

### Usage

This script is the user interface for this framework. In order to get started, a
user must supply the job_manager.py script with a few arguments as input:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-s / --string - The hash string
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

### Job_manager.py Configuration

The job_manager.py script has 4 configurable options:

1.  DICTIONARY - This is the location of the full dictionary used.

2.  HASH_VALUES - This is a dictionary of hash types along with their
    corresponding hashcat code. Technically, any supported hashcat hash-type can
    be placed in this dictionary along with its corresponding code.

3.  PORT - This is the TCP port in which to look for workers on the network. The
    default value is 24998

4.  MANUAL_WORKER_LIST - This is the pre-populated list of worker IP addresses.
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

1.  PORT - This is the TCP port the worker listens on. TCP port 24998 is the
    default configuration.

2.  DICTIONARY_PATH - This is the *path* to the dictionary the worker is
    supposed to use. Do not include the file itself (i.e. /tmp/dictionary.txt)
    as this will generate an error.

3.  HASHCAT - This is the complete path to the hashcat binary (e.g.
    /usr/bin/hashcat)

### worker.service/worker.init

Since the worker script is meant to act as a perpetual service, supplied are two
startup scripts. The worker.init is meant for systems that use SysV startup
scripts and the worker.service is meant for systems that use SystemD.

**SystemD **
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

 

ToDo
----

 
