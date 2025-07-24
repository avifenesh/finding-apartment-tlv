#!/bin/bash

echo "🚀 Simple AWS EC2 Deployment"
echo "============================"

# Get the default VPC
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region eu-west-1)
echo "Using VPC: $VPC_ID"

# Get a public subnet
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=default-for-az,Values=true" --query 'Subnets[0].SubnetId' --output text --region eu-west-1)
echo "Using subnet: $SUBNET_ID"

# Create new security group
SG_NAME="yad2-finder-sg-$(date +%s)"
SG_ID=$(aws ec2 create-security-group \
    --group-name $SG_NAME \
    --description "Security group for Yad2 Apartment Finder" \
    --vpc-id $VPC_ID \
    --region eu-west-1 \
    --query 'GroupId' \
    --output text)

echo "Created security group: $SG_ID"

# Add rules
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --region eu-west-1
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region eu-west-1
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region eu-west-1

# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters \
        "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
        "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region eu-west-1)

echo "Using AMI: $AMI_ID"

# Create key pair
KEY_NAME="yad2-key-$(date +%s)"
aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text --region eu-west-1 > ${KEY_NAME}.pem
chmod 400 ${KEY_NAME}.pem

# Simple user data
cat > user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install docker git -y
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Clone and run
cd /home/ec2-user
git clone https://github.com/avifenesh/finding-apartment-tlv.git
cd finding-apartment-tlv
docker build -t yad2-finder .
docker run -d -p 80:8000 -p 8000:8000 --name yad2-app -v $(pwd)/data:/app/data yad2-finder
EOF

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t2.micro \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --subnet-id $SUBNET_ID \
    --associate-public-ip-address \
    --user-data file://user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=yad2-finder-simple}]" \
    --query 'Instances[0].InstanceId' \
    --output text \
    --region eu-west-1)

echo "Instance launched: $INSTANCE_ID"
echo "Waiting for instance..."

aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region eu-west-1

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region eu-west-1)

echo ""
echo "✅ Deployment complete!"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Key file: ${KEY_NAME}.pem"
echo ""
echo "Access with: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo "API will be at: http://$PUBLIC_IP/api"
echo ""
echo "⏳ Docker build will take 5-10 minutes. Check logs with:"
echo "ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'docker logs yad2-app'"

# Save details
cat > deployment-info.txt << EOF
INSTANCE_ID=$INSTANCE_ID
PUBLIC_IP=$PUBLIC_IP
KEY_FILE=${KEY_NAME}.pem
SECURITY_GROUP=$SG_ID
REGION=eu-west-1
API_URL=http://$PUBLIC_IP/api
EOF

rm -f user-data.sh