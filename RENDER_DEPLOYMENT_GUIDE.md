# 🚀 Render Deployment Guide

## Complete guide for deploying Crypto Tracker to Render.com with DevOps best practices

### 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Process](#deployment-process)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Render Account
- Sign up at [render.com](https://render.com)
- Connect your GitHub repository
- Have payment method ready (starter plan: $7/month per service)

### 2. Local Development Setup
- Git repository connected to GitHub
- Docker installed (for local testing)
- Node.js 18+ and Python 3.11+

### 3. GitHub Repository Secrets
Add these secrets in your GitHub repository settings:
```
RENDER_API_KEY=your_render_api_key
```

---

## Initial Setup

### 1. Install Render CLI
```bash
# Install Render CLI
curl -fsSL https://cli.render.com/install | sh

# Add to PATH
export PATH="$HOME/.render/bin:$PATH"

# Authenticate
render auth login
```

### 2. Prepare Your Repository
Ensure these files exist in your repository:
- `render.yaml` (infrastructure configuration)
- `.env.render` (environment template)
- `scripts/render-deploy.sh` (deployment script)

---

## Environment Configuration

### 1. Render Services Configuration

The `render.yaml` file defines your infrastructure:

```yaml
services:
  # Frontend (React)
  - type: web
    name: crypto-tracker-frontend
    runtime: node
    plan: starter
    buildCommand: cd crypto-tracker-frontend && npm ci && npm run build
    staticPublishPath: ./crypto-tracker-frontend/dist
  
  # Backend (Flask)
  - type: web
    name: crypto-tracker-backend
    runtime: python
    plan: starter
    buildCommand: cd crypto-tracker-backend && pip install -r requirements.txt
    startCommand: cd crypto-tracker-backend && gunicorn --bind 0.0.0.0:$PORT app:app

databases:
  - name: crypto-tracker-db
    plan: starter
  - name: crypto-tracker-cache
    type: redis
    plan: starter
```

### 2. Environment Variables

Set these in Render dashboard for each service:

#### Backend Service Environment Variables:
```env
FLASK_ENV=production
DATABASE_URL=(auto-generated)
REDIS_URL=(auto-generated)
SECRET_KEY=(generate random)
JWT_SECRET_KEY=(generate random)
CORS_ORIGINS=https://crypto-tracker-frontend.onrender.com
```

#### Frontend Environment (Build-time):
```env
VITE_API_URL=https://crypto-tracker-backend.onrender.com
VITE_ENV=production
```

---

## Deployment Process

### Method 1: Automated GitHub Actions

Push to `main` branch triggers automatic deployment:

```bash
git push origin main
```

The GitHub Actions workflow will:
1. ✅ Validate code and configuration
2. 🏗️ Build and test both frontend and backend
3. 🚀 Deploy to Render using blueprint
4. 🏥 Run health checks
5. 📢 Send deployment notifications

### Method 2: Manual Deployment

Using the deployment script:

```bash
# Deploy to production
./scripts/render-deploy.sh deploy --env production --wait

# Deploy preview
./scripts/render-deploy.sh preview --force

# Check status
./scripts/render-deploy.sh status

# View logs
./scripts/render-deploy.sh logs --service crypto-tracker-backend
```

### Method 3: Render CLI Direct

```bash
# Deploy using blueprint
render blueprint apply --yes

# Check service status
render service list

# View service logs
render service logs crypto-tracker-backend --tail 100
```

---

## Post-Deployment Verification

### 1. Health Checks

```bash
# Check backend health
curl https://crypto-tracker-backend.onrender.com/api/health

# Check frontend
curl https://crypto-tracker-frontend.onrender.com
```

### 2. Database Migration

If you have database migrations:

```bash
# Connect to service shell
render service shell crypto-tracker-backend

# Run migrations (inside shell)
python manage.py migrate
```

### 3. Verify Core Functionality

Test these endpoints:
- `GET /api/health` - Health check
- `GET /api/prices` - Price data
- `POST /api/transactions` - Add transaction
- `GET /api/portfolio` - Portfolio data

---

## Monitoring & Maintenance

### 1. Render Dashboard

Monitor your services at:
- **Main Dashboard**: https://dashboard.render.com
- **Service Metrics**: CPU, Memory, Request rates
- **Deployment History**: Previous deployments
- **Logs**: Real-time application logs

### 2. Automated Backups

Database backups run daily at 2 AM UTC via cron job:

```yaml
jobs:
  - type: cron
    name: database-backup
    schedule: "0 2 * * *"
    startCommand: python scripts/backup_database.py
```

### 3. Health Monitoring

Set up uptime monitoring:
- **Render Health Checks**: Built-in monitoring
- **External Services**: UptimeRobot, Pingdom
- **Custom Health Endpoint**: `/api/health`

### 4. Scaling

Adjust your service plan based on usage:
- **Starter**: $7/month - 512MB RAM, 0.1 CPU
- **Standard**: $25/month - 2GB RAM, 1 CPU
- **Pro**: $85/month - 4GB RAM, 2 CPU

---

## Troubleshooting

### Common Issues

#### 1. Build Failures

```bash
# Check build logs
render service logs crypto-tracker-backend --deployment

# Common fixes:
# - Check requirements.txt/package.json
# - Verify Python/Node versions
# - Check for missing environment variables
```

#### 2. Database Connection Issues

```bash
# Verify DATABASE_URL is set
render env list crypto-tracker-backend

# Check database status
render database list

# Test connection from service shell
render service shell crypto-tracker-backend
# Then: python -c "import psycopg2; print('DB connection works')"
```

#### 3. CORS Issues

Frontend can't connect to backend:
- Check `CORS_ORIGINS` environment variable
- Ensure frontend URL is correctly set
- Verify API endpoints are accessible

#### 4. Slow Performance

- Enable Redis caching
- Optimize database queries
- Consider upgrading to higher plan
- Implement CDN for static assets

### 5. SSL Certificate Issues

Render provides automatic SSL:
- Custom domains: Add DNS records
- Verify domain ownership
- Certificate auto-renewal

---

## Cost Optimization

### Monthly Cost Breakdown (Starter Plan)

| Service | Cost | Description |
|---------|------|-------------|
| Frontend Web Service | $7 | Static site hosting |
| Backend Web Service | $7 | Flask API server |
| PostgreSQL Database | $7 | 1GB storage |
| Redis Cache | $7 | 30MB memory |
| **Total** | **$28/month** | Full application |

### Cost Saving Tips

1. **Start with Starter Plans**: Upgrade only when needed
2. **Use Preview Deployments**: Test changes before production
3. **Monitor Usage**: Review metrics monthly
4. **Optimize Code**: Reduce resource usage
5. **Consider Scaling**: Only scale up during high traffic

---

## Security Best Practices

### 1. Environment Variables
- Never commit secrets to git
- Use Render's environment variable management
- Rotate secrets regularly

### 2. Database Security
- Use strong passwords (auto-generated)
- Enable SSL connections
- Limit IP access if needed

### 3. Application Security
- Enable CORS with specific origins
- Use HTTPS everywhere
- Implement rate limiting
- Add security headers

### 4. Monitoring
- Enable access logs
- Set up error alerting  
- Monitor for suspicious activity
- Regular security updates

---

## Advanced Configuration

### 1. Custom Domains

```yaml
# In render.yaml
services:
  - type: web
    name: crypto-tracker-frontend
    customDomains:
      - name: crypto-tracker.yourdomain.com
```

### 2. Environment-Specific Configurations

```yaml
# Preview deployments
previewsEnabled: true
blueprints:
  - name: feature-preview
    envVars:
      - key: ENV_NAME
        value: preview
```

### 3. Background Jobs

```yaml
jobs:
  - type: cron
    name: price-updater
    schedule: "*/5 * * * *"  # Every 5 minutes
    startCommand: python update_prices.py
```

---

## Support and Resources

### 1. Documentation
- **Render Docs**: https://render.com/docs
- **API Reference**: https://api-docs.render.com
- **Community Forum**: https://community.render.com

### 2. Getting Help
- **Support**: support@render.com
- **Status Page**: https://status.render.com
- **GitHub Issues**: Report issues in your repo

### 3. Updates and Maintenance
- Monitor Render changelog for updates
- Keep dependencies updated
- Regular security reviews
- Performance optimization

---

## Quick Reference Commands

```bash
# Deployment
./scripts/render-deploy.sh deploy --env production
./scripts/render-deploy.sh preview

# Monitoring  
./scripts/render-deploy.sh status
./scripts/render-deploy.sh logs --service backend
./scripts/render-deploy.sh health

# Management
render service list
render service restart crypto-tracker-backend
render env list crypto-tracker-backend

# Database
render database list
render database backup crypto-tracker-db
```

---

## Summary

This deployment setup provides:

✅ **Automated CI/CD** - GitHub Actions integration  
✅ **Infrastructure as Code** - render.yaml configuration  
✅ **Multi-environment** - Production, staging, preview  
✅ **Monitoring** - Health checks, logs, metrics  
✅ **Security** - SSL, environment variables, CORS  
✅ **Backup** - Automated database backups  
✅ **Scaling** - Easy service plan upgrades  
✅ **Cost-effective** - Starting at $28/month  

Your crypto tracker application is now ready for production deployment with enterprise-grade DevOps practices! 🎉