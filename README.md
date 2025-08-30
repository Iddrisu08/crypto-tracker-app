# 🚀 Crypto Investment Tracker

A modern, full-stack cryptocurrency portfolio tracking application with real-time data, advanced analytics, and automated deployment.

![Crypto Tracker](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green)
![Deploy](https://img.shields.io/badge/Deploy-Render-purple)

## ✨ Features

### 📊 Core Functionality
- **Real-time Portfolio Tracking** - Live BTC and ETH price updates
- **Profit/Loss Analytics** - Daily and cumulative P&L calculations  
- **Transaction Management** - Add, edit, and track manual transactions
- **Historical Data** - Portfolio value trends over time
- **Advanced Analytics** - Performance metrics and insights

### 🎨 User Experience
- **Progressive Web App (PWA)** - Install on mobile and desktop
- **Dark/Light Theme** - Automatic and manual theme switching
- **Responsive Design** - Works on all device sizes
- **Offline Support** - Service worker for offline functionality
- **Real-time Updates** - Live data refresh every 5 minutes

### 📈 Analytics & Reports
- **Portfolio Allocation** - Asset distribution visualization
- **Price Alerts** - Email notifications for price targets
- **CSV Export** - Download portfolio and transaction data
- **Performance Metrics** - ROI, volatility, and trend analysis

### 🔐 Security & Performance
- **Secure API** - Rate limiting and CORS protection
- **Caching** - Optimized API response caching
- **Health Checks** - Automated monitoring and alerts
- **Error Boundaries** - Graceful error handling

## 🏗️ Architecture

### Frontend Stack
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and development server
- **React Icons** - Comprehensive icon library
- **CSS3** - Custom styling with CSS variables
- **PWA** - Service worker and manifest configuration

### Backend Stack  
- **Flask** - Python web framework
- **Gunicorn** - WSGI HTTP server
- **SQLite** - Lightweight database
- **Flask-CORS** - Cross-origin resource sharing
- **APScheduler** - Background job scheduling

### DevOps & Deployment
- **Docker** - Containerized applications
- **GitHub Actions** - CI/CD automation
- **Render** - Cloud deployment platform
- **Docker Hub** - Container image registry

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone Repository
```bash
git clone https://github.com/Iddrisu08/crypto-tracker-app.git
cd crypto-tracker-app
```

### 2. Run with Docker (Recommended)
```bash
# Start the application
docker compose up -d

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:5002
```

### 3. Local Development
```bash
# Backend
cd crypto-tracker-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run --port=5002

# Frontend (new terminal)
cd crypto-tracker-frontend
npm install
npm run dev
```

## 🌐 Deployment

### Automated Deployment (CI/CD)

1. **Fork the repository**
2. **Set up GitHub Secrets:**
   ```
   DOCKER_USERNAME=your-dockerhub-username
   DOCKER_PASSWORD=your-dockerhub-password
   RENDER_BACKEND_DEPLOY_HOOK=your-backend-webhook
   RENDER_FRONTEND_DEPLOY_HOOK=your-frontend-webhook
   RENDER_BACKEND_URL=https://your-backend.onrender.com
   RENDER_FRONTEND_URL=https://your-frontend.onrender.com
   ```

3. **Push to main branch** - Automatic deployment begins!

### Manual Deployment

1. **Deploy to Render:**
   ```bash
   # Use the deployment script
   ./scripts/deploy.sh
   
   # Or manually with Docker
   docker build -t your-username/crypto-tracker-backend ./crypto-tracker-backend
   docker build -t your-username/crypto-tracker-frontend ./crypto-tracker-frontend
   docker push your-username/crypto-tracker-backend
   docker push your-username/crypto-tracker-frontend
   ```

2. **Configure Render services** using the provided YAML files

### Deployment Options
- 🔄 **GitHub Actions** - Automated CI/CD
- 🐳 **Docker Hub** - Container registry
- ☁️ **Render** - Cloud deployment
- 🛠️ **Manual** - Custom deployment script

## 📖 API Documentation

### Core Endpoints
```
GET  /portfolio              - Current portfolio data
GET  /transactions           - Transaction history
GET  /daily_profit_loss      - Daily P&L data
GET  /live_profit_loss       - Real-time P&L
GET  /current_prices         - Latest crypto prices
POST /add_transaction        - Add new transaction
GET  /alerts                 - Price alerts
POST /alerts                 - Create price alert
GET  /export/portfolio       - CSV export
```

### Health & Monitoring
```
GET /health                  - Service health check
GET /performance_metrics     - Performance data
GET /transaction_analysis    - Transaction insights
```

## 🔧 Configuration

### Environment Variables

#### Backend
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
CORS_ORIGINS=https://your-frontend-url.com
```

#### Frontend Build Args
```bash
VITE_API_URL=https://your-backend-url.com
```

### Database
- **Development**: SQLite database in `instance/crypto_tracker.db`
- **Production**: Persistent disk mounted at `/app/instance`

## 📊 Monitoring

### Health Checks
- Backend: `/health` endpoint
- Frontend: HTTP 200 response
- Database: SQLite file accessibility

### Logging
- Structured logging with timestamps
- Request/response logging
- Error tracking and monitoring

### Performance Metrics
- API response times
- Database query performance
- Cache hit rates
- Error rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Guidelines
- Follow existing code style
- Add comments for complex logic
- Update documentation
- Test thoroughly before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CoinGecko API** - Cryptocurrency price data
- **React Community** - UI framework and ecosystem
- **Flask Community** - Backend framework
- **Render** - Deployment platform

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Iddrisu08/crypto-tracker-app/issues)
- **Documentation**: [Deployment Guide](deploy-to-render.md)
- **CI/CD**: [GitHub Actions Workflow](.github/workflows/deploy.yml)

## 🚀 Live Demo

- **Frontend**: https://crypto-tracker-frontend.onrender.com
- **Backend API**: https://crypto-tracker-backend.onrender.com
- **Health Check**: https://crypto-tracker-backend.onrender.com/health

---

**Built with ❤️ by [Iddrisu](https://github.com/Iddrisu08)**

*Happy crypto tracking! 📈🚀*