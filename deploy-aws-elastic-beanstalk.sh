#!/bin/bash

echo "🚀 AWS Elastic Beanstalk Deployment Script"
echo "=========================================="
echo ""
echo "Elastic Beanstalk provides managed platform for your application"
echo "with automatic scaling, monitoring, and load balancing!"
echo ""

# Configuration
APP_NAME="yad2-apartment-finder"
ENV_NAME="yad2-apartment-finder-env"
PLATFORM="Docker"
REGION="us-east-1"

echo "📋 Prerequisites:"
echo "- AWS CLI configured"
echo "- EB CLI installed (pip install awsebcli)"
echo ""

# Check AWS CLI
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check EB CLI
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Installing..."
    pip install awsebcli --user
    export PATH=$PATH:~/.local/bin
fi

# Create Dockerrun.aws.json for Elastic Beanstalk
echo "📝 Creating Elastic Beanstalk configuration..."
cat > Dockerrun.aws.json << 'EOF'
{
  "AWSEBDockerrunVersion": "1",
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 80
    }
  ],
  "Volumes": [
    {
      "HostDirectory": "/var/app/data",
      "ContainerDirectory": "/app/data"
    }
  ],
  "Logging": "/var/log/eb-docker"
}
EOF

# Create .ebextensions for configuration
mkdir -p .ebextensions
cat > .ebextensions/01_instance.config << 'EOF'
option_settings:
  aws:autoscaling:launchconfiguration:
    InstanceType: t2.micro
    EC2KeyName: yad2-finder-key
  aws:elasticbeanstalk:application:environment:
    DATABASE_URL: sqlite:///./data/apartments.db
    CORS_ORIGINS: https://avifenesh.github.io
    HEADLESS_BROWSER: true
    ENVIRONMENT: production
    PORT: 8000
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py
  aws:elasticbeanstalk:environment:process:default:
    HealthCheckPath: /health
    Port: 8000
    Protocol: HTTP
EOF

# Create .elasticbeanstalk directory
mkdir -p .elasticbeanstalk
cat > .elasticbeanstalk/config.yml << EOF
branch-defaults:
  main:
    environment: $ENV_NAME
global:
  application_name: $APP_NAME
  default_ec2_keyname: yad2-finder-key
  default_platform: $PLATFORM
  default_region: $REGION
  workspace_type: Application
EOF

# Initialize Elastic Beanstalk application
echo "🎯 Initializing Elastic Beanstalk application..."
eb init $APP_NAME --platform docker --region $REGION --keyname yad2-finder-key || true

# Create the environment
echo "🌍 Creating Elastic Beanstalk environment..."
eb create $ENV_NAME \
    --instance-type t2.micro \
    --region $REGION \
    --cname $APP_NAME \
    --timeout 20 || {
    echo "⚠️  Environment might already exist, continuing..."
}

# Deploy the application
echo "📦 Deploying application..."
eb deploy $ENV_NAME --timeout 20

# Get environment URL
echo "🔍 Getting environment details..."
ENV_URL=$(eb status $ENV_NAME | grep "CNAME:" | awk '{print $2}')

echo ""
echo "🎉 Deployment complete!"
echo "======================"
echo "Environment URL: http://$ENV_URL"
echo "API Docs: http://$ENV_URL/docs"
echo "Health Check: http://$ENV_URL/health"
echo ""
echo "📊 Elastic Beanstalk Dashboard:"
echo "https://console.aws.amazon.com/elasticbeanstalk/home?region=$REGION#/environment/dashboard?environmentName=$ENV_NAME"
echo ""
echo "📝 Next steps:"
echo "1. Update frontend/script.js with: http://$ENV_URL/api"
echo "2. Push changes to GitHub Pages"
echo ""
echo "🔧 Useful commands:"
echo "- View logs: eb logs"
echo "- SSH into instance: eb ssh"
echo "- Open in browser: eb open"
echo "- Deploy updates: eb deploy"
echo ""
echo "💰 Cost: FREE with AWS Free Tier!"
echo "   - t2.micro instance: 750 hours/month free"
echo "   - Load balancer: Free for 12 months"
echo "   - Storage: 10GB free"