# 🚀 Quick Start Guide - Yad2 Apartment Finder

## 🌐 Your Application is Live!

### Frontend (GitHub Pages)
✅ **URL**: https://avifenesh.github.io/finding-apartment-tlv/

### Login Credentials
📧 **Email**: aviarchi1994@gmail.com  
🔑 **Password**: Af!@#$56789

## 🛠️ Complete Setup Instructions

### 1. Start the Backend Locally

```bash
# Navigate to project directory
cd /home/fedora/finding-apartment-tlv

# Run the backend
./run.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Install Playwright browsers
- Start the backend on http://localhost:8000

### 2. Make Backend Accessible (Choose One)

#### Option A: Use ngrok (Recommended for Testing)
```bash
# Install ngrok if not already installed
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok

# Or download directly
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip

# Run ngrok
./ngrok http 8000
```

Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

#### Option B: Deploy to AWS EC2
- Launch an EC2 instance
- Clone this repository
- Run the backend with systemd
- Configure security groups for port 8000

### 3. Update Frontend with Backend URL

Edit the file: `frontend/script.js`

```javascript
// Change this line:
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : 'https://your-backend-api.com/api'; // TODO: Update with your actual backend URL

// To your ngrok or EC2 URL:
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : 'https://abc123.ngrok.io/api'; // Your actual backend URL
```

### 4. Update GitHub Pages

```bash
# Commit and push changes
git add frontend/script.js
git commit -m "Update API URL"
git push origin gh-pages
```

Wait 2-3 minutes for GitHub Pages to update.

### 5. Test the Application

1. Visit https://avifenesh.github.io/finding-apartment-tlv/
2. Login with the credentials above
3. Click "הפעל סריקה" to start scraping
4. View apartments from the last 3 days

## 🎯 Features

- **Automated Scraping**: Fetches listings from 6 Tel Aviv neighborhoods
- **Recent Listings Only**: Shows apartments from the last 3 days
- **Image Gallery**: Browse apartment photos
- **Filters**: By neighborhood, price, and room count
- **Direct Links**: Click to view on Yad2
- **Secure Login**: Password-protected access

## 🏘️ Neighborhoods Covered

1. נווה צדק (Neve Tzedek)
2. פלורנטין (Florentin)
3. לב העיר (City Center)
4. כרם התימנים (Kerem HaTeimanim)
5. הצפון הישן (Old North)
6. שבזי (Shabazi)

## 📊 Backend API Endpoints

- `GET /api/apartments` - List apartments
- `GET /api/apartments/{id}` - Get apartment details
- `POST /api/scrape` - Trigger scraping
- `GET /api/stats` - Get statistics
- `GET /api/neighborhoods` - List neighborhoods
- `GET /docs` - API documentation

## 🔧 Troubleshooting

### Frontend Issues
- Clear browser cache and cookies
- Check browser console for errors
- Ensure you're using the correct login credentials

### Backend Issues
- Check if port 8000 is available
- Ensure all dependencies are installed
- Check Playwright browser installation

### Scraping Issues
- Yad2 may have rate limits
- Check internet connection
- Review scraper logs in terminal

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones

## 🔐 Security Notes

- Authentication is client-side (for demo)
- For production, implement proper backend auth
- Never expose credentials in public repos
- Use HTTPS for all communications

## 📞 Need Help?

1. Check the console logs
2. Review the error messages
3. Ensure backend is running
4. Verify API URL is correct

---

**Ready to find your dream apartment in Tel Aviv! 🏠**