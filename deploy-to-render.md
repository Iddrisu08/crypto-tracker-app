# 🚀 Deploy Crypto Tracker to Render

This guide will help you deploy your crypto tracker application to Render using the automated GitHub Actions pipeline.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **Docker Hub Account**: Sign up at [hub.docker.com](https://hub.docker.com)
3. **GitHub Repository**: Your code should be pushed to GitHub

## 🔧 Setup Instructions

### Step 1: Configure Docker Hub

1. Create a Docker Hub account
2. Create two repositories:
   - `crypto-tracker-backend`
   - `crypto-tracker-frontend`

### Step 2: Set GitHub Secrets

In your GitHub repository, go to Settings → Secrets and Variables → Actions, and add:

```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password
RENDER_BACKEND_DEPLOY_HOOK=https://api.render.com/deploy/srv-xxx
RENDER_FRONTEND_DEPLOY_HOOK=https://api.render.com/deploy/srv-yyy  
RENDER_BACKEND_URL=https://crypto-tracker-backend.onrender.com
RENDER_FRONTEND_URL=https://crypto-tracker-frontend.onrender.com
```

### Step 3: Deploy Backend to Render

1. **Log into Render Dashboard**
2. **Create New Web Service**
   - Connect your GitHub repository
   - Choose "Docker" as runtime
   - Set these configurations:

```yaml
Name: crypto-tracker-backend
Region: Oregon (or closest to you)
Branch: main
Root Directory: crypto-tracker-backend
Dockerfile Path: ./Dockerfile
```

3. **Environment Variables:**
```
FLASK_ENV=production
SECRET_KEY=<generate-secure-key>
JWT_SECRET_KEY=<generate-secure-key>
CORS_ORIGINS=https://crypto-tracker-frontend.onrender.com
PORT=5000
```

4. **Add Persistent Disk:**
   - Name: crypto-data
   - Mount Path: /app/instance
   - Size: 1GB

### Step 4: Deploy Frontend to Render

1. **Create New Web Service**
   - Connect your GitHub repository
   - Choose "Docker" as runtime
   - Set these configurations:

```yaml
Name: crypto-tracker-frontend
Region: Oregon (or closest to you)
Branch: main
Root Directory: crypto-tracker-frontend
Dockerfile Path: ./Dockerfile
```

2. **Build Arguments:**
```
VITE_API_URL=https://crypto-tracker-backend.onrender.com
```

### Step 5: Configure Deploy Hooks

1. In each Render service, go to Settings
2. Find the "Deploy Hook" URL
3. Add these to your GitHub secrets:
   - `RENDER_BACKEND_DEPLOY_HOOK`
   - `RENDER_FRONTEND_DEPLOY_HOOK`

## 🚀 Deployment Options

### Option 1: Automated CI/CD (Recommended)
- Push code to `main` branch
- GitHub Actions will automatically:
  - Test the application
  - Build Docker images
  - Push to Docker Hub  
  - Deploy to Render
  - Run health checks

### Option 2: Manual Deployment
```bash
# Deploy using render.yaml
render deploy

# Or deploy individually
render deploy --service crypto-tracker-backend
render deploy --service crypto-tracker-frontend
```

### Option 3: Direct Render Dashboard
- Use the Render dashboard to manually trigger deployments
- Monitor logs and deployment status

## 📊 Post-Deployment

After successful deployment, your app will be available at:
- **Frontend**: `https://crypto-tracker-frontend.onrender.com`
- **Backend API**: `https://crypto-tracker-backend.onrender.com`

### Health Check Endpoints:
- Backend: `https://crypto-tracker-backend.onrender.com/health`
- Frontend: `https://crypto-tracker-frontend.onrender.com`

## 🔧 Environment Configuration

### Production Environment Variables:
```bash
# Backend
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
CORS_ORIGINS=https://crypto-tracker-frontend.onrender.com

# Frontend Build Args
VITE_API_URL=https://crypto-tracker-backend.onrender.com
```

## 🐛 Troubleshooting

### Common Issues:

1. **CORS Errors**: Ensure backend CORS_ORIGINS includes frontend URL
2. **API Connection Failed**: Verify VITE_API_URL points to correct backend
3. **Build Failures**: Check Docker build logs in Render dashboard
4. **Database Issues**: Ensure persistent disk is mounted at `/app/instance`

### Monitoring:
- Check Render service logs
- Monitor GitHub Actions workflow runs
- Use health check endpoints

## 🚀 Advanced Features

### Auto-scaling (Paid Plans):
```yaml
scaling:
  minInstances: 1
  maxInstances: 3
  targetCPU: 70
```

### Custom Domains:
- Add custom domain in Render dashboard
- Update CORS_ORIGINS and build args accordingly

### Background Jobs:
- Uncomment worker service in render.yaml
- Set up cron jobs for price updates

## 📈 Monitoring & Analytics

- **Render Metrics**: Built-in monitoring dashboard
- **Health Checks**: Automated endpoint monitoring  
- **Logs**: Centralized logging with search
- **Alerts**: Configure notifications for downtime

Your crypto tracker is now production-ready! 🎉