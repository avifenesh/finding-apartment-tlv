#!/bin/bash

# Script to update frontend after initial deployment

if [ ! -f "deployment-info.txt" ]; then
    echo "❌ deployment-info.txt not found. Run deploy-to-aws.sh first."
    exit 1
fi

# Read deployment info
source deployment-info.txt

echo "📤 Syncing frontend files to S3..."
aws s3 sync ../frontend/ s3://${S3_BUCKET}/ \
    --exclude "*.DS_Store" \
    --exclude ".git/*" \
    --delete

echo "🔄 Creating CloudFront invalidation..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id ${DISTRIBUTION_ID} \
    --paths '/*' \
    --query 'Invalidation.Id' \
    --output text)

echo "✅ Invalidation created: ${INVALIDATION_ID}"
echo "⏳ Changes will be visible in 5-10 minutes"
echo "🔗 URL: ${CLOUDFRONT_URL}"