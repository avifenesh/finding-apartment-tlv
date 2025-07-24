#!/bin/bash

# AWS S3 and CloudFront deployment script
# Prerequisites: AWS CLI configured with appropriate credentials

echo "🚀 Deploying Yad2 Apartment Finder to AWS..."

# Configuration
S3_BUCKET="yad2-apartment-finder-${RANDOM}"
CLOUDFRONT_COMMENT="Yad2 Apartment Finder"
REGION="us-east-1"  # CloudFront requires us-east-1 for some operations

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

echo "📦 Creating S3 bucket..."
aws s3 mb s3://${S3_BUCKET} --region ${REGION}

# Enable static website hosting
echo "🌐 Configuring S3 bucket for static website hosting..."
aws s3 website s3://${S3_BUCKET} \
    --index-document login.html \
    --error-document error.html

# Create bucket policy for CloudFront access
echo "🔒 Setting bucket policy..."
cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${S3_BUCKET}/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket ${S3_BUCKET} --policy file:///tmp/bucket-policy.json

# Upload frontend files
echo "📤 Uploading frontend files..."
aws s3 sync ../frontend/ s3://${S3_BUCKET}/ \
    --exclude "*.DS_Store" \
    --exclude ".git/*"

# Create CloudFront distribution
echo "☁️ Creating CloudFront distribution..."
DISTRIBUTION_CONFIG=$(cat <<EOF
{
    "CallerReference": "$(date +%s)",
    "Comment": "${CLOUDFRONT_COMMENT}",
    "DefaultRootObject": "login.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-${S3_BUCKET}",
                "DomainName": "${S3_BUCKET}.s3.${REGION}.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${S3_BUCKET}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
        },
        "Compress": true,
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000
    },
    "Enabled": true,
    "PriceClass": "PriceClass_100"
}
EOF
)

# Create distribution
DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config "${DISTRIBUTION_CONFIG}" \
    --query 'Distribution.Id' \
    --output text)

echo "✅ CloudFront distribution created: ${DISTRIBUTION_ID}"

# Get distribution domain name
DOMAIN_NAME=$(aws cloudfront get-distribution \
    --id ${DISTRIBUTION_ID} \
    --query 'Distribution.DomainName' \
    --output text)

echo ""
echo "🎉 Deployment complete!"
echo "📍 S3 Bucket: ${S3_BUCKET}"
echo "🌐 CloudFront Distribution ID: ${DISTRIBUTION_ID}"
echo "🔗 CloudFront URL: https://${DOMAIN_NAME}"
echo ""
echo "⚠️  IMPORTANT:"
echo "1. Update the API_URL in frontend/script.js with your backend URL"
echo "2. CloudFront distribution may take 15-20 minutes to fully deploy"
echo "3. Login credentials:"
echo "   Email: aviarchi1994@gmail.com"
echo "   Password: Af!@#\$56789"
echo ""
echo "To update the frontend later, run:"
echo "aws s3 sync ../frontend/ s3://${S3_BUCKET}/"
echo "aws cloudfront create-invalidation --distribution-id ${DISTRIBUTION_ID} --paths '/*'"

# Save deployment info
cat > deployment-info.txt <<EOF
S3_BUCKET=${S3_BUCKET}
DISTRIBUTION_ID=${DISTRIBUTION_ID}
CLOUDFRONT_URL=https://${DOMAIN_NAME}
REGION=${REGION}
Deployed at: $(date)
EOF

echo ""
echo "Deployment information saved to deployment-info.txt"