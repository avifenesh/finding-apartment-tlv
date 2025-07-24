# 🚀 Backend Deployment Guide

## Quick Deployment Options

### Option 1: Railway (Recommended - Easiest)

Railway offers a generous free tier and automatic deployments from GitHub.

1. **Sign up** at [railway.app](https://railway.app)

2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Deploy from your project folder**:
   ```bash
   cd /home/fedora/finding-apartment-tlv
   railway login
   railway init
   railway up
   ```

4. **Get your URL**:
   ```bash
   railway open
   ```

Your backend will be live at something like: `https://yad2-finder.up.railway.app`

### Option 2: Render (Free Tier Available)

1. **Push latest code to GitHub**:
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Go to** [render.com](https://render.com) and sign up

3. **Create New Web Service**:
   - Connect GitHub account
   - Select `avifenesh/finding-apartment-tlv`
   - Name: `yad2-apartment-finder`
   - Runtime: Docker
   - Branch: main
   - Click "Create Web Service"

4. **Wait for deployment** (takes ~10 minutes)

Your backend will be at: `https://yad2-apartment-finder.onrender.com`

### Option 3: Fly.io (Global Edge Network)

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**:
   ```bash
   fly auth login
   fly launch --dockerfile Dockerfile
   fly deploy
   ```

3. **Open app**:
   ```bash
   fly open
   ```

### Option 4: Quick Heroku Alternative - Koyeb

1. **Sign up** at [koyeb.com](https://www.koyeb.com)

2. **Connect GitHub** and select your repository

3. **Deploy with**:
   - Builder: Dockerfile
   - Port: 8000
   - Health check: /health

## 🔄 Update Frontend After Deployment

Once your backend is deployed, update the frontend:

1. **Edit** `frontend/script.js`:
   ```javascript
   const API_URL = window.location.hostname === 'localhost' 
       ? 'http://localhost:8000/api'
       : 'https://YOUR-BACKEND-URL/api'; // Update this!
   ```

2. **Commit and push**:
   ```bash
   git add frontend/script.js
   git commit -m "Update API URL to production backend"
   git push origin gh-pages
   ```

3. **Wait 2-3 minutes** for GitHub Pages to update

## 🔧 Environment Variables

All platforms support environment variables. Set these:

```
PORT=8000
DATABASE_URL=sqlite:///./data/apartments.db
CORS_ORIGINS=https://avifenesh.github.io
HEADLESS_BROWSER=true
ENVIRONMENT=production
```

## 📊 Monitoring Your Backend

### Health Check
Visit: `https://YOUR-BACKEND-URL/health`

### API Documentation
Visit: `https://YOUR-BACKEND-URL/docs`

### View Logs
- **Railway**: `railway logs`
- **Render**: Dashboard → Logs
- **Fly.io**: `fly logs`

## 🚨 Troubleshooting

### "Application failed to start"
- Check logs for errors
- Ensure PORT environment variable is set
- Verify Dockerfile syntax

### "CORS error in browser"
- Update CORS_ORIGINS environment variable
- Include your GitHub Pages URL

### "Playwright browser not found"
- The Dockerfile already installs Chromium
- If issues persist, try headless: false

### "Database errors"
- Ensure /app/data directory exists
- Check disk space allocation

## 💰 Cost Estimates

| Platform | Free Tier | Paid Starting |
|----------|-----------|---------------|
| Railway | 500 hours/month | $5/month |
| Render | 750 hours/month | $7/month |
| Fly.io | 3 shared VMs | $1.94/month |
| Koyeb | 1 app | $5.40/month |

## 🎯 Recommended: Railway

Railway is recommended because:
- ✅ Easiest setup (5 minutes)
- ✅ Automatic GitHub deployments
- ✅ Good free tier
- ✅ Built-in database support
- ✅ Excellent developer experience

## 📝 Next Steps

1. **Deploy backend** using one of the methods above
2. **Update frontend** with your backend URL
3. **Test the application** end-to-end
4. **Set up monitoring** (optional)
5. **Configure auto-deployments** from GitHub

---

Need help? The deployment script `./deploy-backend.sh` provides interactive guidance!