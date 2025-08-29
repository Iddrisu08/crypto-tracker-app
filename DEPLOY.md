# 🚀 Simple Deployment Guide

## Deploy in 3 Steps:

### Step 1: Go to Render
Visit: https://dashboard.render.com

### Step 2: Create Blueprint
- Click "New +" → "Blueprint"  
- Connect GitHub and select: `Iddrisu08/crypto-tracker-app`
- Click "Apply Blueprint"

### Step 3: Set Environment Variables
In the backend service, add:
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

Generate keys:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## That's it! 
Your app will be deployed automatically.

**Cost:** ~$14/month (Frontend + Backend + Database)
**Time:** 10-15 minutes