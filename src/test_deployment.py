from src.ec2.vpc import VPC
from src.ec2.ec2 import EC2
from src.client_locator import EC2Client
import time


def main():
    # Create a VPC
    ec2_client = EC2Client().get_client()
    vpc = VPC(ec2_client)

    vpc_response = vpc.create_vpc()

    print('VPC created: ' + str(vpc_response))
    # Previously used sleep method to pause the program to wait for vpc to be available.

    # time.sleep(4)

    # Add name tag to VPC
    vpc_name = 'Boto3-VPC'
    vpc_id = vpc_response['Vpc']['VpcId']
    # Used boto3's waiter method to wait for VPC to be available until adding name tags
    ec2_client.get_waiter('vpc_available').wait(VpcIds=[vpc_id])
    vpc.add_name_tag(vpc_id, vpc_name)

    print('Added ' + vpc_name + ' to ' + vpc_id)

    # Create an IGW
    igw_response = vpc.create_internet_gateway()
    igw_id = igw_response['InternetGateway']['InternetGatewayId']

    # Attach IGW to VPC
    vpc.attach_igw_to_vpc(vpc_id, igw_id)

    # Create a public subnet
    public_subnet_response = vpc.create_subnet(vpc_id, '10.0.1.0/24')
    public_subnet_id = public_subnet_response['Subnet']['SubnetId']
    print('Subnet created for VPC ' + vpc_id + ': ' + str(public_subnet_response))

    # Sleep method used to allow subnet to be created by aws
    time.sleep(4)

    # Add name tag to public subnet
    vpc.add_name_tag(public_subnet_id, 'Boto3-Public-Subnet')

    # Create a public route table
    public_route_table_response = vpc.create_public_route_table(vpc_id)
    rtb_id = public_route_table_response['RouteTable']['RouteTableId']

    # Adding IGW to Public Route Table
    vpc.create_igw_route_to_public_route_table(rtb_id, igw_id)

    # Associate Public Subnet with Route Table
    vpc.associate_subnet_with_route_table(public_subnet_id, rtb_id)

    # Allow auto-assign public ip addresses for subnet
    vpc.allow_auto_assign_ip_addresses_for_subnet(public_subnet_id)

    # Create a private subnet
    private_subnet_response = vpc.create_subnet(vpc_id, '10.0.2.0/24')
    private_subnet_id = private_subnet_response['Subnet']['SubnetId']

    print('Created private subnet ' + private_subnet_id + ' for VPC ' + vpc_id)

    # Sleep method used to allow aws to create subnet
    time.sleep(4)

    # Add name tag to private Subnet
    vpc.add_name_tag(private_subnet_id, 'Boto3-Private-Subnet')

    # EC2 Instances

    # Create EC2 Instances
    ec2 = EC2(ec2_client)

    # Create a key pair
    key_pair_name = 'Boto3-KeyPair'
    key_pair_response = ec2.create_key_pair(key_pair_name)

    print('Created Key Pair with name ' + key_pair_name + ': ' + str(key_pair_response))

    # Create a Security Group
    public_security_group_name = 'Boto3-Public-SG'
    public_security_group_description = 'Public Security Group for Public Subnet Internet Access'
    public_security_group_response = ec2.create_security_group(public_security_group_name, public_security_group_description, vpc_id)

    # Sleep method used to allow aws to create security group before adding rules
    time.sleep(4)

    public_security_group_id = public_security_group_response['GroupId']

    # Add Public Access to Security Group
    ec2.add_inbound_rule_to_sg(public_security_group_id)

    print('Added public access rule to Security Group ' + public_security_group_name)

    # Course Correction: Replace 'httpd24' with 'httpd'
    user_data = """#!/bin/bash
                yum update -y
                yum  install httpd -y
                service httpd start
                chkconfig httpd on
                echo "<html><body><h1>Hello from <b>Boto3</b> using Python!</h1></body></html>" > /var/www/html/index.html"""

    ami_id = 'ami-08e4e35cccc6189f4'

    # Launch a public EC2 Instance
    ec2.launch_ec2_instance(ami_id, key_pair_name, 1, 1, public_security_group_id, public_subnet_id, user_data)

    print('Launching Public EC2 Instance using AMI ' + ami_id)

    # Adding another Security Group for Private EC2 Instance
    private_security_group_name = 'Boto3-Private_SG'
    private_security_group_description = 'Private Security Group for Private Subnet'

    # Course Correction: added vpc_id to method call to match parameter list
    private_security_group_response = ec2.create_security_group(private_security_group_name, private_security_group_description, vpc_id)

    time.sleep(4)

    private_security_group_id = private_security_group_response['GroupId']

    # Add rule to private Security Group
    ec2.add_inbound_rule_to_sg(private_security_group_id)

    time.sleep(4)

    # Course Correction: Added user data to match method parameters
    # Launch a private EC2 Instance
    ec2.launch_ec2_instance(ami_id, key_pair_name, 1, 1, private_security_group_id, private_subnet_id, user_data)


# Course Correction: Created an object of class EC2Client
def describe_instances():
    ec2client = EC2Client()
    ec2_client = ec2client.get_client()
    ec2 = EC2(ec2_client)

    ec2_response = ec2.describe_ec2_instances()
    print(str(ec2_response))


# Course Correction: Created an object of class EC2Client
def modify_instance():
    ec2client = EC2Client()
    ec2_client = ec2client.get_client()
    ec2 = EC2(ec2_client)

    ec2.modify_ec2_instances('i-0ecaabb3609e2a9c9')


def stop_instance():
    ec2client = EC2Client()
    ec2_client = ec2client.get_client()
    ec2 = EC2(ec2_client)
    ec2.stop_instance('i-0d42f52c72e6817b5')


def start_instance():
    ec2client = EC2Client()
    ec2_client = ec2client.get_client()
    ec2 = EC2(ec2_client)
    ec2.start_instance('i-0d42f52c72e6817b5')


def terminate_instance():
    ec2client = EC2Client()
    ec2_client = ec2client.get_client()
    ec2 = EC2(ec2_client)
    ec2.terminate_instance('i-0d42f52c72e6817b5')


if __name__ == '__main__':
    main()
    # describe_instances()
    # modify_instance()
    # stop_instance()
    # start_instance()
    # terminate_instance()
