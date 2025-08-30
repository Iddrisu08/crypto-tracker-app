# 🚀 Step-by-Step Deployment Setup Guide

Follow these steps to deploy your crypto tracker to Render with automated CI/CD.

## 📋 Prerequisites Checklist

- [ ] GitHub repository with your code
- [ ] Docker Hub account (free)
- [ ] Render account (free)
- [ ] 30 minutes of setup time

---

## Step 1: 🐳 Set Up Docker Hub

### 1.1 Create Docker Hub Account
1. Go to [hub.docker.com](https://hub.docker.com)
2. Sign up or log in
3. Verify your email address

### 1.2 Create Repositories
1. Click **"Create Repository"**
2. Create first repository:
   - **Name**: `crypto-tracker-backend`
   - **Visibility**: Public (free) or Private (paid)
   - Click **"Create"**
3. Create second repository:
   - **Name**: `crypto-tracker-frontend`
   - **Visibility**: Public (free) or Private (paid)
   - Click **"Create"**

### 1.3 Generate Access Token
1. Click your profile → **"Account Settings"**
2. Go to **"Security"** tab
3. Click **"New Access Token"**
4. **Description**: `GitHub Actions CI/CD`
5. **Access permissions**: `Read, Write, Delete`
6. Click **"Generate"**
7. **⚠️ IMPORTANT**: Copy the token immediately (you won't see it again!)

**Save these values:**
```
Docker Username: your-dockerhub-username
Docker Token: dckr_pat_xxxxxxxxxxxxxxxxx
```

---

## Step 2: ☁️ Set Up Render Services

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended) or email
3. Verify your account

### 2.2 Connect GitHub Repository
1. In Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Connect"** next to your crypto-tracker repository
5. If not visible, click **"Configure GitHub App"** and grant access

### 2.3 Create Backend Service

1. **Repository**: Select your crypto-tracker repository
2. **Name**: `crypto-tracker-backend`
3. **Region**: `Oregon` (or closest to you)
4. **Branch**: `main`
5. **Root Directory**: `crypto-tracker-backend`
6. **Runtime**: `Docker`
7. **Build Command**: Leave empty
8. **Start Command**: Leave empty (uses Dockerfile)

#### Environment Variables:
Click **"Advanced"** → **"Environment Variables"** → **"Add Environment Variable"**:

```
FLASK_ENV=production
SECRET_KEY=generate-secure-32-char-string
JWT_SECRET_KEY=generate-secure-32-char-string  
CORS_ORIGINS=https://crypto-tracker-frontend.onrender.com
PORT=5000
```

**To generate secure keys, run:**
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

#### Persistent Storage:
1. Scroll to **"Disk"** section
2. Click **"Add Disk"**
3. **Name**: `crypto-data`
4. **Mount Path**: `/app/instance`
5. **Size**: `1` GB

#### Finalize:
1. Click **"Create Web Service"**
2. Wait for initial deployment (5-10 minutes)
3. **Copy the service URL** (e.g., `https://crypto-tracker-backend.onrender.com`)

### 2.4 Create Frontend Service

1. Click **"New +"** → **"Web Service"**
2. **Repository**: Your crypto-tracker repository
3. **Name**: `crypto-tracker-frontend`
4. **Region**: `Oregon` (same as backend)
5. **Branch**: `main`
6. **Root Directory**: `crypto-tracker-frontend`
7. **Runtime**: `Docker`
8. **Build Command**: Leave empty
9. **Start Command**: Leave empty

#### Environment Variables:
```
VITE_API_URL=https://crypto-tracker-backend.onrender.com
```
*Replace with your actual backend URL from Step 2.3*

#### Finalize:
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. **Copy the service URL** (e.g., `https://crypto-tracker-frontend.onrender.com`)

### 2.5 Get Deploy Hook URLs

For **Backend**:
1. Go to backend service → **"Settings"**
2. Scroll to **"Deploy Hook"**
3. Copy the URL (e.g., `https://api.render.com/deploy/srv-xxxxxxxxx`)

For **Frontend**:
1. Go to frontend service → **"Settings"**
2. Scroll to **"Deploy Hook"**
3. Copy the URL (e.g., `https://api.render.com/deploy/srv-yyyyyyyyy`)

---

## Step 3: 🔐 Configure GitHub Secrets

### 3.1 Access Repository Secrets
1. Go to your GitHub repository
2. Click **"Settings"** tab (top right)
3. In left sidebar, click **"Secrets and variables"** → **"Actions"**

### 3.2 Add Repository Secrets
Click **"New repository secret"** for each:

#### Docker Hub Secrets:
```
Name: DOCKER_USERNAME
Secret: your-dockerhub-username

Name: DOCKER_PASSWORD  
Secret: dckr_pat_xxxxxxxxxxxxxxxxx
```

#### Render Deploy Hooks:
```
Name: RENDER_BACKEND_DEPLOY_HOOK
Secret: https://api.render.com/deploy/srv-backend-xxx

Name: RENDER_FRONTEND_DEPLOY_HOOK
Secret: https://api.render.com/deploy/srv-frontend-yyy
```

#### Render Service URLs:
```
Name: RENDER_BACKEND_URL
Secret: https://crypto-tracker-backend.onrender.com

Name: RENDER_FRONTEND_URL
Secret: https://crypto-tracker-frontend.onrender.com
```

### 3.3 Verify Secrets
You should have **6 secrets total**:
- [x] `DOCKER_USERNAME`
- [x] `DOCKER_PASSWORD`
- [x] `RENDER_BACKEND_DEPLOY_HOOK`
- [x] `RENDER_FRONTEND_DEPLOY_HOOK`
- [x] `RENDER_BACKEND_URL`
- [x] `RENDER_FRONTEND_URL`

---

## Step 4: 🚀 Test Deployment

### 4.1 Trigger First Deployment
1. Make a small change to your code (e.g., update a comment)
2. Commit and push to `main` branch:
   ```bash
   git add .
   git commit -m "🚀 Test CI/CD pipeline"
   git push origin main
   ```

### 4.2 Monitor Deployment
1. **GitHub Actions**: Go to your repo → **"Actions"** tab
2. Watch the workflow run (should take 10-15 minutes)
3. **Render Dashboard**: Monitor both services for deployment status

### 4.3 Verify Success
1. **Backend Health**: Visit `https://your-backend.onrender.com/health`
   - Should return: `{"status": "healthy"}`
2. **Frontend**: Visit `https://your-frontend.onrender.com`
   - Should show your crypto tracker app
3. **API Connection**: Check that frontend loads data properly

---

## Step 5: 🎉 Production Ready!

### Your App URLs:
- **🌐 Frontend**: https://crypto-tracker-frontend.onrender.com
- **🔧 Backend API**: https://crypto-tracker-backend.onrender.com
- **🏥 Health Check**: https://crypto-tracker-backend.onrender.com/health

### Automatic Features:
- ✅ **Auto-deploy** on every push to `main`
- ✅ **Docker images** published to Docker Hub
- ✅ **Health monitoring** with automatic checks
- ✅ **SSL certificates** automatically managed
- ✅ **Global CDN** for fast loading
- ✅ **Zero-downtime** deployments

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. "Build failed" in GitHub Actions
- Check the **Actions** tab for error details
- Verify all 6 GitHub secrets are set correctly
- Ensure Docker Hub credentials are valid

#### 2. "Service Unavailable" from Render
- Wait 2-3 minutes for service to start
- Check Render service logs for errors
- Verify environment variables are set correctly

#### 3. Frontend shows "API Error"
- Verify `VITE_API_URL` points to correct backend URL
- Check backend service is running and healthy
- Verify CORS origins in backend include frontend URL

#### 4. Docker push fails
- Verify Docker Hub repositories exist
- Check Docker Hub token has Read/Write/Delete permissions
- Ensure repository names match exactly: `iddris/crypto-tracker-backend`

### Support:
- **GitHub Issues**: [Report problems](https://github.com/Iddrisu08/crypto-tracker-app/issues)
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Docker Hub**: [docs.docker.com](https://docs.docker.com)

---

## 🎯 Next Steps

1. **Custom Domain** (optional): Add your own domain in Render
2. **Monitoring**: Set up Render alerts for downtime
3. **Scaling**: Upgrade to paid plans for better performance
4. **Database**: Consider upgrading to PostgreSQL for production

**🎉 Congratulations! Your crypto tracker is now production-ready with automated CI/CD! 🚀**