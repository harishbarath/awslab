# This program is intended to create a VPC and assign subnets as necessary.

# import os
import boto3
import os
import sys

# get a ec2 resource object
ec2 = boto3.resource('ec2')
ec2client = boto3.client('ec2')

# create a vpc 
vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16', AmazonProvidedIpv6CidrBlock=True)

# Add a name H-vpc to the vpc created.
vpc.create_tags(Tags=[{"Key": "Name", "Value": "H-vpc"}])
vpc.wait_until_available()
print(vpc.id)
ch = sys.stdin.read(1)

# Assign IPv6 block for subnet using CIDR provided by Amazon, except different size (must use /64)
ipv6_subnet_cidr = vpc.ipv6_cidr_block_association_set[0]['Ipv6CidrBlock'] 
print(ipv6_subnet_cidr)

# Look at https://stackoverflow.com/questions/7983820/get-the-last-4-characters-of-a-string for python 
# syntax on substring.
ipv6_subnet_cidr = ipv6_subnet_cidr[:-2] + '64'
# The /24 in the following line of code is Cidr notation. It basically tells that the mask 255.255.255.0
# should be used for routing. This is called Cidr notation.
subnet_web = vpc.create_subnet(CidrBlock='10.0.0.0/24', Ipv6CidrBlock=ipv6_subnet_cidr)
# Modify subnet attributes such that only IPV6 address is used.
ec2client.modify_subnet_attribute(SubnetId=subnet_web.id, AssignIpv6AddressOnCreation={'Value': True})

print('created subnet')
ch = sys.stdin.read(1)

# Create an internat gateway and attach to the vpc.
internet_gateway = ec2.create_internet_gateway()  
internet_gateway.attach_to_vpc(VpcId=vpc.vpc_id)

# Create route table
route_table = vpc.create_route_table()  
route_ig_ipv4 = route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internet_gateway.internet_gateway_id)  
route_ig_ipv6 = route_table.create_route(DestinationIpv6CidrBlock='::/0', GatewayId=internet_gateway.internet_gateway_id)  
# Associate route with subnet_web
route_table.associate_with_subnet(SubnetId=subnet_web.id)

print('Route tables created')
ch = sys.stdin.read(1)

# Security groups
web_sg = vpc.create_security_group(GroupName="H-WEB-SG", Description="Security Group to allow access to Webserver")
db_sg = vpc.create_security_group(GroupName="H-DB-SG", Description="Security Group for DB server")

# Security group parameters for web server
ip_ranges = [{  
    'CidrIp': '0.0.0.0/0'
}]

ip_v6_ranges = [{  
    'CidrIpv6': '::/0'
}]

perms = [{  
    'IpProtocol': 'TCP',
    'FromPort': 80,
    'ToPort': 80,
    'IpRanges': ip_ranges,
    'Ipv6Ranges': ip_v6_ranges
}, {
    'IpProtocol': 'TCP',
    'FromPort': 443,
    'ToPort': 443,
    'IpRanges': ip_ranges,
    'Ipv6Ranges': ip_v6_ranges
}, {
    'IpProtocol': 'TCP',
    'FromPort': 22,
    'ToPort': 22,
    'IpRanges': ip_ranges,
    'Ipv6Ranges': ip_v6_ranges
}]

web_sg.authorize_ingress(IpPermissions=perms)
print('web sg created')
ch = sys.stdin.read(1)

# Define parameters for db security group

# Anywhere from webserver subnet
to_db_ip_v6_ranges = [{  
    'CidrIpv6': ipv6_subnet_cidr
}]

db_perms = [{  
    'IpProtocol': 'TCP',
    'FromPort': 80,
    'ToPort': 80,
    'Ipv6Ranges':to_db_ip_v6_ranges
}, {
    'IpProtocol': 'TCP',
    'FromPort': 443,
    'ToPort': 443,
    'Ipv6Ranges': to_db_ip_v6_ranges
}, {
    'IpProtocol': 'TCP',
    'FromPort': 22,
    'ToPort': 22,
    'Ipv6Ranges': to_db_ip_v6_ranges
}, {
    'IpProtocol': 'TCP',
    'FromPort': 3306,
    'ToPort': 3306,
    'Ipv6Ranges': to_db_ip_v6_ranges
}]

db_sg.authorize_ingress(IpPermissions=db_perms)
print('db sg created')
ch = sys.stdin.read(1)


# Before attempting to create a keypair, let us detele the key if it exists.
response = ec2client.delete_key_pair(KeyName='HWebServerKey')
db_response = ec2client.delete_key_pair(KeyName='HDBServerKey')
print('Deleted existing key')

outfile = open('HWebServer.pem','w')
key_pair = ec2.create_key_pair(KeyName='HWebServerKey')
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)
outfile.close()
os.chmod('HWebServer.pem', 0o400)

outfile = open('HDBServer.pem', 'w')
key_pair = ec2.create_key_pair(KeyName='HDBServerKey')
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)
outfile.close()
os.chmod('HDBServer.pem', 0o400)

print('Created KeyPair')

# Spin up an instance and see it come alive in dashboard.
instances = ec2.create_instances(
    ImageId='ami-07f9ebd98e32b6dfd', 
    MinCount=1, 
    MaxCount=1,
    KeyName="HWebServerKey",
    InstanceType="t2.micro",
    NetworkInterfaces=[
        {
            'AssociatePublicIpAddress': True,
            'SubnetId': subnet_web.id,
            'DeviceIndex': 0,
            'Groups': [web_sg.group_id]
        }
    ]
)

print('Instance Created. Waiting for instance to be in run state....')
instances[0].wait_until_running()

for instance in instances:
    print(instance.id, instance.instance_type)

instances = ec2.create_instances(
    ImageId='ami-07f9ebd98e32b6dfd', 
    MinCount=1, 
    MaxCount=1,
    KeyName="HDBServerKey",
    InstanceType="t2.micro",
    NetworkInterfaces=[
        {
            'AssociatePublicIpAddress': True,
            'SubnetId': subnet_web.id,
            'DeviceIndex': 0,
            'Groups': [db_sg.group_id]
        }
    ]
)

print('Instance Created. Waiting for instance to be in run state....')
instances[0].wait_until_running()

for instance in instances:
    print(instance.id, instance.instance_type)


