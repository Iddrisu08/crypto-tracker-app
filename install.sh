#!/bin/bash

# Crypto Tracker Installation Script
echo "🚀 Installing Enhanced Crypto Tracker v2.0"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if required commands exist
check_dependencies() {
    print_header "🔍 Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found. Docker deployment will not be available."
    fi
    
    if ! command -v redis-server &> /dev/null; then
        print_warning "Redis not found. Install Redis for caching support."
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_error "Please install the missing dependencies and run this script again."
        exit 1
    fi
    
    print_status "All required dependencies found!"
}

# Install backend dependencies
install_backend() {
    print_header "🐍 Installing Backend Dependencies..."
    
    cd crypto-tracker-backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python packages..."
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f ".env" ]; then
        print_status "Creating environment configuration..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration!"
    fi
    
    cd ..
    print_status "Backend installation completed!"
}

# Install frontend dependencies
install_frontend() {
    print_header "⚛️ Installing Frontend Dependencies..."
    
    cd crypto-tracker-frontend
    
    # Install npm packages
    print_status "Installing Node.js packages..."
    npm install
    
    # Install additional TypeScript dependencies
    print_status "Installing TypeScript dependencies..."
    npm install zustand typescript @typescript-eslint/eslint-plugin @typescript-eslint/parser
    
    cd ..
    print_status "Frontend installation completed!"
}

# Setup database
setup_database() {
    print_header "🗄️ Setting up Database..."
    
    cd crypto-tracker-backend
    source venv/bin/activate
    
    print_status "Initializing database..."
    python database.py
    
    cd ..
    print_status "Database setup completed!"
}

# Setup Docker (optional)
setup_docker() {
    if command -v docker &> /dev/null; then
        print_header "🐳 Setting up Docker..."
        
        print_status "Building Docker containers..."
        docker-compose build
        
        print_status "Docker setup completed!"
        print_status "Run 'docker-compose up' to start the application in containers"
    else
        print_warning "Docker not available. Skipping Docker setup."
    fi
}

# Main installation process
main() {
    print_header "🎯 Starting Installation Process..."
    
    # Check dependencies
    check_dependencies
    
    # Install backend
    install_backend
    
    # Install frontend
    install_frontend
    
    # Setup database
    setup_database
    
    # Setup Docker (optional)
    setup_docker
    
    print_header "✅ Installation Completed Successfully!"
    echo ""
    echo "🚀 Next Steps:"
    echo "==============="
    echo "1. Edit crypto-tracker-backend/.env with your configuration"
    echo "2. Start the backend: cd crypto-tracker-backend && source venv/bin/activate && python app_enhanced.py"
    echo "3. Start the frontend: cd crypto-tracker-frontend && npm run dev"
    echo "4. Visit http://localhost:5173 to access the application"
    echo ""
    echo "📚 New Features:"
    echo "=================="
    echo "✅ JWT Authentication System"
    echo "✅ PostgreSQL Database with Migration"
    echo "✅ Redis Caching for Performance"
    echo "✅ Rate Limiting & Security"
    echo "✅ API Versioning (/api/v1/)"
    echo "✅ TypeScript Support"
    echo "✅ Centralized State Management (Zustand)"
    echo "✅ Comprehensive Error Handling"
    echo "✅ Docker Containerization"
    echo "✅ Production-Ready Configuration"
    echo ""
    echo "🔐 Default Admin Login:"
    echo "Username: admin"
    echo "Password: admin123"
    echo "⚠️  Change this password immediately!"
    echo ""
    echo "📖 For more information, check the documentation."
}

# Run main function
main "$@"