# Frontend Deployment Guide

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws --version
   aws configure
   ```

2. **AWS IAM permissions for:**
   - S3 bucket creation and management
   - CloudFront distribution creation
   - IAM role creation (for CloudFront OAC)

## Deployment Steps

### 1. Initial Deployment

```bash
cd deploy
./deploy-to-aws.sh
```

This will:
- Create an S3 bucket for static hosting
- Upload all frontend files
- Create a CloudFront distribution
- Output the CloudFront URL

### 2. Update Backend API URL

After deployment, you need to update the API URL in the frontend:

1. Edit `frontend/script.js`
2. Replace `'https://your-backend-api.com/api'` with your actual backend URL
3. Run the update script:
   ```bash
   ./update-frontend.sh
   ```

### 3. Backend Deployment Options

Since the frontend needs to connect to your backend API, you have several options:

#### Option A: Deploy Backend to AWS EC2
- Launch an EC2 instance
- Install Python, clone your repo
- Run the backend with a process manager (systemd, supervisor)
- Set up Nginx as reverse proxy
- Configure security groups for port 8000

#### Option B: Use AWS Lambda + API Gateway
- Package the FastAPI app for Lambda
- Create API Gateway endpoints
- More complex but serverless

#### Option C: Keep Backend Local (Development Only)
- Use ngrok to expose local backend:
  ```bash
  ngrok http 8000
  ```
- Update frontend with ngrok URL
- Note: This is temporary and for testing only

## Access the Application

1. **CloudFront URL**: Check `deployment-info.txt` or deployment output
2. **Login Credentials**:
   - Email: `aviarchi1994@gmail.com`
   - Password: `Af!@#$56789`

## Updating the Frontend

After making changes to frontend files:

```bash
cd deploy
./update-frontend.sh
```

This will sync changes and invalidate CloudFront cache.

## Important Notes

- CloudFront distributions take 15-20 minutes to fully deploy
- The backend API must be accessible from the internet
- CORS is configured to allow all origins (update for production)
- Authentication is handled client-side (consider server-side for production)

## Troubleshooting

1. **403 Forbidden**: Check S3 bucket policy and CloudFront settings
2. **API Connection Failed**: Verify backend URL and CORS settings
3. **Login Issues**: Check browser console for errors

## Security Considerations

For production use:
- Implement proper backend authentication (JWT tokens)
- Use environment variables for sensitive data
- Restrict CORS to specific domains
- Consider AWS WAF for additional protection
- Use HTTPS for backend API