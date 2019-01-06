# This file is expected to create a security group and set rules

import boto3

ec2 = boto3.client('ec2')

response = ec2.describe_security_groups()
print(response)
