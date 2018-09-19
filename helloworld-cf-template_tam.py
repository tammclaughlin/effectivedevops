from troposphere import ( 
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template, 
)

from ipaddress import  ip_network
from ipify import get_ip

ApplicationPort="3000"
PublicCidrIp =  str(ip_network(get_ip()))

t=Template()

t.add_description("Effective DevOps in AWS: HelloWorld application")

t.add_parameter (Parameter(
    "KeyPair",
    Description="Name of an existing keypair to ssh",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

t.add_resource(ec2.SecurityGroup(
   "SecurityGroup",
    GroupDescription="Allow ssh and TCP / {} access".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
             IpProtocol="tcp",
             FromPort="22",
             ToPort="22",
             CidrIp=PublicCidrIp,
        ),
        ec2.SecurityGroupRule(
             IpProtocol="tcp",
             FromPort=ApplicationPort,
             ToPort=ApplicationPort,
             CidrIp="0.0.0.0/0",
        )
    ],
))

ud = Base64(Join('\n', [
     "#!/bin/bash",
     "sudo yum install --enablerepo=epel -y nodejs",
     "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
     "wget http://bit.ly/2vVcT18 -O /etc/init/helloworld.conf",
     "start helloworld"
]))

t.add_resource(ec2.Instance(
   "instance",
   ImageId="ami-0ff8a91507f77f867",
   InstanceType="t2.micro",
   SecurityGroups=[Ref("SecurityGroup")],
   KeyName=Ref("KeyPair"),
   UserData=ud,
 )
)

t.add_output (Output (
  "InstancePublicIP",
  Description="Public IP of our instance",
  Value=GetAtt("instance", "PublicIp"),
 ))

t.add_output (Output (
   "WebUrl",
   Description="Application endpoint",
   Value=Join("", [
    "http://", GetAtt("instance", "PublicDnsName"),
   ":", ApplicationPort
   ]),
 ))

print t.to_json()
   
