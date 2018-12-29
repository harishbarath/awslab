import boto3

def  printS3Info():
	#  get s3 resource type
	print('\n\n\nS3 from function\n')
	s3  = boto3.resource('s3')
	# Print the available buckets
	for bucket in s3.buckets.all():
		print(bucket.name)

def printEc2():
	print('\n\n\nec2 from function\n')
	# Do the same for EC2
	ec2 = boto3.client('ec2')
	response = ec2.describe_instances()
	print(response)

print('S3 related')
print('==========')
#  get s3 resource type
s3  = boto3.resource('s3')
# Print the available buckets
for bucket in s3.buckets.all():
	print(bucket.name)

print('****************')
print('EC2 related')
print('===========')

# Do the same for EC2
ec2 = boto3.client('ec2')
response = ec2.describe_instances()
print(response)
	
printS3Info()
printEc2()