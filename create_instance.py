# This program will create an ec2 instance using the stored credentials
# and leave the instance running.
import os
import boto3


# Create a key-pair for the web server. The following lines of code will
# create a keypair and store it in a file in the directory.

# Before attempting to create a keypair, let us detele the key if it exists.
ec2client = boto3.client('ec2')
response = ec2client.delete_key_pair(KeyName='WebServerKey')
print('Deleted existing key')

# Now create a KeyPair called WebServerKey
ec2 = boto3.resource('ec2')

outfile = open('WebServer.pem','w')
key_pair = ec2.create_key_pair(KeyName='WebServerKey')
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)
os.chmod('WebServer.pem', 0o400)

print('Created KeyPair')

# Spin up an instance and see it come alive in dashboard.
instances = ec2.create_instances(
    ImageId='ami-07f9ebd98e32b6dfd', 
    MinCount=1, 
    MaxCount=1,
    KeyName="WebServerKey",
    InstanceType="t2.micro"
)

print('Instance Created')

for instance in instances:
    print(instance.id, instance.instance_type)
