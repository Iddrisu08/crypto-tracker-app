# 🚀 Crypto Tracker - Dockerized

A full-stack cryptocurrency portfolio tracker with real-time analytics.

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Deploy in One Command
```bash
docker-compose up -d
```

### Access Your App
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## Architecture

- **Frontend**: React + Vite (Multi-stage Docker build)  
- **Backend**: Flask API with SQLite (local file storage)
- **No external dependencies** - runs completely self-contained

## Docker Configuration

### Multi-Stage Builds
- **Frontend**: Build with Node.js → Serve with Nginx
- **Backend**: Build with Python → Run with Gunicorn
- **Optimized**: Small production images

### Services
- `frontend`: React app on port 3000
- `backend`: Flask API on port 5000 with SQLite storage

## Production Deployment

1. **Change secrets** in `docker-compose.yml`:
   ```yaml
   SECRET_KEY=your-production-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   ```

2. **Deploy**:
   ```bash
   docker-compose up -d
   ```

## Development

### Build individual services:
```bash
# Backend only
docker build -t crypto-backend ./crypto-tracker-backend

# Frontend only  
docker build -t crypto-frontend ./crypto-tracker-frontend
```

### View logs:
```bash
docker-compose logs -f
```

### Stop services:
```bash
docker-compose down
```

That's it! Your crypto tracker is now running in Docker containers.