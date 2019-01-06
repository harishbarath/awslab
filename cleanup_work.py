# This program is expected to clean up every thing that is done in aws.
import os
import boto3

# Delete KeyPair for WebServer
ec2Client = boto3.client('ec2')
response = ec2Client.delete_key_pair(KeyName='WebServerKey')

# Delete all instances
ec2 = boto3.resource('ec2')
for instance in ec2.instances.all():
    print(instance.id, instance.state)
    response = instance.terminate()
    print(response)

#Delete the Keypair
os.chmod('WebServer.pem', 0o777)
os.remote('WebServer.pem')
