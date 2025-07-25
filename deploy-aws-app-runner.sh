#!/bin/bash

echo "🚀 AWS App Runner Deployment Script"
echo "===================================="
echo ""
echo "AWS App Runner provides a fully managed container service"
echo "Perfect for your Yad2 backend with automatic scaling!"
echo ""

# Configuration
SERVICE_NAME="yad2-apartment-finder"
REGION="us-east-1"

echo "📋 Prerequisites:"
echo "- AWS CLI configured"
echo "- Docker image pushed to ECR"
echo ""

# Check AWS CLI
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Create ECR repository
echo "🐳 Creating ECR repository..."
REPO_URI=$(aws ecr create-repository \
    --repository-name $SERVICE_NAME \
    --region $REGION \
    --query 'repository.repositoryUri' \
    --output text 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "⚠️  ECR repository already exists, using existing one"
    REPO_URI=$(aws ecr describe-repositories \
        --repository-names $SERVICE_NAME \
        --region $REGION \
        --query 'repositories[0].repositoryUri' \
        --output text)
fi

echo "📦 ECR Repository: $REPO_URI"

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REPO_URI

# Build and push Docker image
echo "🏗️  Building Docker image..."
docker build -t $SERVICE_NAME .

echo "📤 Pushing to ECR..."
docker tag $SERVICE_NAME:latest $REPO_URI:latest
docker push $REPO_URI:latest

# Create App Runner service configuration
cat > apprunner.yaml << EOF
version: 1.0
runtime: docker
build:
  commands:
    build:
      - echo "No build commands"
run:
  runtime-version: latest
  command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
    env: PORT
  env:
    - name: DATABASE_URL
      value: "sqlite:///./data/apartments.db"
    - name: CORS_ORIGINS
      value: "https://avifenesh.github.io"
    - name: HEADLESS_BROWSER
      value: "true"
    - name: ENVIRONMENT
      value: "production"
EOF

# Create App Runner service
echo "🚀 Creating App Runner service..."
SERVICE_ARN=$(aws apprunner create-service \
    --service-name $SERVICE_NAME \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'$REPO_URI':latest",
            "ImageConfiguration": {
                "Port": "8000",
                "RuntimeEnvironmentVariables": {
                    "DATABASE_URL": "sqlite:///./data/apartments.db",
                    "CORS_ORIGINS": "https://avifenesh.github.io",
                    "HEADLESS_BROWSER": "true",
                    "ENVIRONMENT": "production"
                }
            },
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": false
    }' \
    --health-check-configuration '{
        "Protocol": "HTTP",
        "Path": "/health",
        "Interval": 10,
        "Timeout": 5,
        "HealthyThreshold": 1,
        "UnhealthyThreshold": 5
    }' \
    --region $REGION \
    --query 'Service.ServiceArn' \
    --output text)

echo "✅ Service created: $SERVICE_ARN"
echo "⏳ Waiting for service to be running..."

# Wait for service to be running
while true; do
    STATUS=$(aws apprunner describe-service \
        --service-arn $SERVICE_ARN \
        --region $REGION \
        --query 'Service.Status' \
        --output text)
    
    if [ "$STATUS" = "RUNNING" ]; then
        break
    fi
    
    echo "Current status: $STATUS"
    sleep 10
done

# Get service URL
SERVICE_URL=$(aws apprunner describe-service \
    --service-arn $SERVICE_ARN \
    --region $REGION \
    --query 'Service.ServiceUrl' \
    --output text)

echo ""
echo "🎉 Deployment complete!"
echo "======================"
echo "Service URL: https://$SERVICE_URL"
echo "API Docs: https://$SERVICE_URL/docs"
echo "Health Check: https://$SERVICE_URL/health"
echo ""
echo "📝 Next steps:"
echo "1. Update frontend/script.js with: https://$SERVICE_URL/api"
echo "2. Push changes to GitHub Pages"
echo ""
echo "💰 Pricing: ~$5/month for light usage"
echo "   - Compute: $0.064/vCPU-hour"
echo "   - Memory: $0.007/GB-hour"
echo "   - Requests: $1 per million requests"

# Clean up
rm -f apprunner.yaml