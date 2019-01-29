# This program will create an ec2 instance using the stored credentials
# and leave the instance running.
import os
import boto3


# Create a key-pair for the web server. The following lines of code will
# create a keypair and store it in a file in the directory.

# Before attempting to create a keypair, let us detele the key if it exists.
ec2client = boto3.client('ec2')
response = ec2client.delete_key_pair(KeyName='HSWebServerKey')
print('Deleted existing key')

# Now create a KeyPair called WebServerKey
ec2 = boto3.resource('ec2')

outfile = open('HSWebServer.pem','w')
key_pair = ec2.create_key_pair(KeyName='HSWebServerKey')
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)
os.chmod('HSWebServer.pem', 0o400)

print('Created KeyPair')

# Before creating an instance, let us create a security group
# and set the necessary permissions.  
sg = ec2.create_security_group(
        GroupName="H-SG-EC2",
        Description="Security group to demonstrate setting rules")

# Define route for all instances in the security group.
ip_ranges = [{  
    'CidrIp': '0.0.0.0/0'
}]

# Opens up port 80 (http), 443 (https) and 22 (ssh) on the instances
# associated with security groups.
permissions = [{  
    'IpProtocol': 'TCP',
    'FromPort': 80,
    'ToPort': 80,
    'IpRanges': ip_ranges,
}, {
    'IpProtocol': 'TCP',
    'FromPort': 443,
    'ToPort': 443,
    'IpRanges': ip_ranges,
}, {
    'IpProtocol': 'TCP',
    'FromPort': 22,
    'ToPort': 22,
    'IpRanges': ip_ranges,
}]

# Use these rules in the security group that got created
sg.authorize_ingress(IpPermissions=permissions)

print('security group created')

# Spin up an instance and see it come alive in dashboard.
instances = ec2.create_instances(
    ImageId='ami-07f9ebd98e32b6dfd', 
    MinCount=1, 
    MaxCount=1,
    KeyName="HSWebServerKey",
    SecurityGroupIds=[sg.id],
    InstanceType="t2.micro"
)
instances[0].wait_until_running()

print('Instance Created')

for instance in instances:
    print(instance.id, instance.instance_type, instance.public_dns_name)
