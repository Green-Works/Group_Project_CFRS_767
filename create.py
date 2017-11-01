# Info/Requirements
# AWS CLI needs to be installed and aws configure command needs to be run to have required credentials
# Script can be run either locally or from within AWS

import argparse
import boto3
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser(description="python script to automate EC2 creation")
parser.add_argument("-n", "--num", type=int, help="number of instances to create")
args = parser.parse_args()

number = args.num
ec2 = boto3.resource('ec2')
#user_data_script = """#!/bin/bash
#echo "Hello World" >> /tmp/data.txt"""

#running_instances = ec2.instances.filter(Filters=[{
#    'Name': 'instance-state-name',
#    'Values': ['running']}])

#waiter = ec2.get_waiter('instance_running')

def startup():
    try:
        ec2.create_instances(
            ImageId='<INSERT IMAGE ID HERE>', # AMI with necessary GPU drivers and NFS ready to mount
            InstanceType='<INSERT INSTANCE TYPE HERE>', # can be replaced with GPU based EC2 instance type id
            MinCount=number, # minimum number of instances to create
            MaxCount=number, # maximum number of instances to create
            UserData='file://<USER DATA FILE NAME WITH EXTENSION>', # Place user data script in same directory as create.py
            KeyName='<INSERT KEY NAME HERE>', # key used to SSH into instance(s)
            NetworkInterfaces=[
                {
                    'AssociatePublicIpAddress': True, # auto assigns public IPv4 address
                    'DeleteOnTermination': True, 
                    'DeviceIndex': 0,
                    'Groups': [
                        '<SECURITY GROUP ID HERE>', # Security Group(s) to assign to instance(s)
                    ],
                    'SubnetId': '<SUBNET ID HERE>' # subnet where instance is located
                },
            ],
            DryRun=True) # Dry Run, verifies command will run successfully without creating instance
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    try:
        instances = ec2.create_instances(
            ImageId='<INSERT IMAGE ID HERE>',
            InstanceType='<INSERT INSTANCE TYPE HERE>',
            MinCount=number,
            MaxCount=number,
            UserData='file://<USER DATA FILE NAME WITH EXTENSION>',
            KeyName='<INSERT KEY NAME HERE>',
            NetworkInterfaces=[
                {
                    'AssociatePublicIpAddress': True,
                    'DeleteOnTermination': True, 
                    'DeviceIndex': 0,
                    'Groups': [
                        '<SECURITY GROUP ID HERE>',
                    ],
                    'SubnetId': '<SUBNET ID HERE>'
                },
            ],
           DryRun=False)
    except ClientError as e:
        print(e)

    print("Waiting for machines to fully boot up...")
    for instance in instances:
         instance.wait_until_running()
         instance.reload()
         print((instance.id, instance.state, instance.public_ip_address))

startup()
