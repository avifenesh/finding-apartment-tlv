#!/bin/bash

echo "🚀 AWS EC2 Deployment Script for Yad2 Apartment Finder"
echo "======================================================"
echo ""

# Configuration
INSTANCE_TYPE="t2.micro"  # Free tier eligible
AMI_ID="ami-0c02fb55956c7d316"  # Amazon Linux 2023 (update based on region)
KEY_NAME="yad2-finder-key"
SECURITY_GROUP="yad2-finder-sg"
INSTANCE_NAME="yad2-apartment-finder"

echo "📋 Prerequisites:"
echo "- AWS CLI configured (aws configure)"
echo "- EC2 key pair created or available"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get current region
REGION=$(aws configure get region)
echo "🌍 Using region: $REGION"

# Create security group
echo "🔒 Creating security group..."
SG_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP \
    --description "Security group for Yad2 Apartment Finder" \
    --query 'GroupId' \
    --output text 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Security group created: $SG_ID"
    
    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
else
    echo "⚠️  Security group already exists, using existing one"
    SG_ID=$(aws ec2 describe-security-groups --group-names $SECURITY_GROUP --query 'SecurityGroups[0].GroupId' --output text)
fi

# Create key pair if it doesn't exist
echo "🔑 Checking SSH key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &> /dev/null; then
    echo "Creating new key pair..."
    aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Key pair created and saved to ${KEY_NAME}.pem"
else
    echo "✅ Using existing key pair: $KEY_NAME"
fi

# Get latest Amazon Linux 2 AMI
echo "🔍 Finding latest Amazon Linux 2023 AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters \
        "Name=name,Values=al2023-ami-*" \
        "Name=state,Values=available" \
        "Name=architecture,Values=x86_64" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

echo "📦 Using AMI: $AMI_ID"

# Create user data script
cat > user-data.sh << 'EOF'
#!/bin/bash
# Update system
yum update -y

# Install Docker
yum install docker -y
systemctl start docker
systemctl enable docker

# Install Git
yum install git -y

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone the repository
cd /home/ec2-user
git clone https://github.com/avifenesh/finding-apartment-tlv.git
cd finding-apartment-tlv

# Build and run with Docker
docker build -t yad2-finder .
docker run -d \
    -p 80:8000 \
    --name yad2-app \
    --restart unless-stopped \
    -v $(pwd)/data:/app/data \
    yad2-finder

# Setup CloudWatch logging
yum install amazon-cloudwatch-agent -y

# Create a simple health check endpoint responder
echo "Backend is starting... Check back in a few minutes." > /var/www/html/index.html
EOF

# Launch EC2 instance
echo "🚀 Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --user-data file://user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"
echo "⏳ Waiting for instance to be running..."

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "🎉 Deployment complete!"
echo "========================"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "URL: http://$PUBLIC_IP"
echo ""
echo "📝 Next steps:"
echo "1. Wait 3-5 minutes for Docker to build and start"
echo "2. Access your API at: http://$PUBLIC_IP/docs"
echo "3. Update frontend/script.js with: http://$PUBLIC_IP/api"
echo ""
echo "SSH access:"
echo "ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "View logs:"
echo "ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'docker logs yad2-app'"

# Clean up
rm -f user-data.sh