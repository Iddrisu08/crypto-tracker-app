#!/bin/bash

# 🚀 Crypto Tracker Deployment Script
# This script helps deploy your crypto tracker to Render

set -e

echo "🚀 Crypto Tracker Deployment Helper"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if required tools are installed
check_requirements() {
    print_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_status "All requirements satisfied"
}

# Build Docker images locally
build_images() {
    print_info "Building Docker images..."
    
    # Build backend
    print_info "Building backend image..."
    docker build -t iddris/crypto-tracker-backend:latest ./crypto-tracker-backend
    
    # Build frontend  
    print_info "Building frontend image..."
    docker build --build-arg VITE_API_URL=https://crypto-tracker-backend.onrender.com \
                 -t iddris/crypto-tracker-frontend:latest ./crypto-tracker-frontend
    
    print_status "Docker images built successfully"
}

# Push images to Docker Hub
push_images() {
    print_info "Pushing images to Docker Hub..."
    
    if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_PASSWORD" ]; then
        print_warning "Docker credentials not set. Please run 'docker login' first."
        return 1
    fi
    
    docker push iddris/crypto-tracker-backend:latest
    docker push iddris/crypto-tracker-frontend:latest
    
    print_status "Images pushed to Docker Hub"
}

# Deploy to Render via webhook
deploy_to_render() {
    print_info "Deploying to Render..."
    
    if [ -z "$RENDER_BACKEND_DEPLOY_HOOK" ]; then
        print_warning "RENDER_BACKEND_DEPLOY_HOOK not set. Skipping backend deployment."
    else
        print_info "Deploying backend..."
        curl -X POST "$RENDER_BACKEND_DEPLOY_HOOK"
        print_status "Backend deployment triggered"
    fi
    
    if [ -z "$RENDER_FRONTEND_DEPLOY_HOOK" ]; then
        print_warning "RENDER_FRONTEND_DEPLOY_HOOK not set. Skipping frontend deployment."
    else
        print_info "Waiting 30s for backend to deploy..."
        sleep 30
        
        print_info "Deploying frontend..."
        curl -X POST "$RENDER_FRONTEND_DEPLOY_HOOK"
        print_status "Frontend deployment triggered"
    fi
}

# Health check
health_check() {
    print_info "Performing health check..."
    
    if [ -z "$RENDER_BACKEND_URL" ]; then
        print_warning "RENDER_BACKEND_URL not set. Skipping health check."
        return 0
    fi
    
    print_info "Waiting for services to be ready..."
    sleep 60
    
    # Check backend
    if curl -f "$RENDER_BACKEND_URL/health" > /dev/null 2>&1; then
        print_status "Backend is healthy"
    else
        print_error "Backend health check failed"
    fi
    
    # Check frontend
    if [ -n "$RENDER_FRONTEND_URL" ]; then
        if curl -f "$RENDER_FRONTEND_URL" > /dev/null 2>&1; then
            print_status "Frontend is healthy"
        else
            print_error "Frontend health check failed"
        fi
    fi
}

# Main deployment flow
main() {
    echo ""
    print_info "Starting deployment process..."
    echo ""
    
    check_requirements
    
    # Ask user what they want to do
    echo ""
    echo "What would you like to do?"
    echo "1) Build images only"
    echo "2) Build and push images"
    echo "3) Full deployment (build, push, deploy)"
    echo "4) Deploy only (requires images already pushed)"
    echo "5) Health check only"
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            build_images
            ;;
        2)
            build_images
            push_images
            ;;
        3)
            build_images
            push_images
            deploy_to_render
            health_check
            ;;
        4)
            deploy_to_render
            health_check
            ;;
        5)
            health_check
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
    
    echo ""
    print_status "Deployment script completed!"
    
    if [ -n "$RENDER_FRONTEND_URL" ]; then
        echo ""
        print_info "🌐 Your app should be available at:"
        print_info "   Frontend: $RENDER_FRONTEND_URL"
        if [ -n "$RENDER_BACKEND_URL" ]; then
            print_info "   Backend:  $RENDER_BACKEND_URL"
        fi
    fi
    
    echo ""
    print_info "📈 Happy crypto tracking! 🚀"
}

# Run main function
main "$@"