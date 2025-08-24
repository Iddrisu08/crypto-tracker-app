#!/bin/bash

# ===============================================
# DOCKER OPTIMIZATION SCRIPT
# ===============================================
# Optimizes Docker images, manages containers, and provides deployment utilities.
# Includes security scanning, image analysis, and performance optimizations.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="crypto-tracker"
REGISTRY="ghcr.io"
DEFAULT_ENV="production"

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print usage
print_usage() {
    echo "Docker Optimization Tool for Crypto Tracker"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  build <env>       - Build optimized images for environment"
    echo "  analyze           - Analyze image sizes and layers"
    echo "  scan             - Security scan images"
    echo "  clean            - Clean up unused Docker resources"
    echo "  deploy <env>     - Deploy with optimized configuration"
    echo "  monitor          - Monitor container performance"
    echo "  backup           - Backup container volumes"
    echo "  restore <backup> - Restore from backup"
    echo ""
    echo "Environments: development, staging, production"
    echo ""
    echo "Examples:"
    echo "  $0 build production"
    echo "  $0 analyze"
    echo "  $0 scan"
    echo "  $0 clean"
}

# Function to build optimized images
build_images() {
    local env=${1:-$DEFAULT_ENV}
    
    print_message $BLUE "🏗️ Building optimized images for $env environment..."
    
    # Set build arguments
    local build_date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    local vcs_ref=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')
    local build_args="--build-arg TARGET_ENV=$env --build-arg BUILD_DATE=$build_date --build-arg VCS_REF=$vcs_ref"
    
    # Determine build target based on environment
    local target="runtime"
    if [ "$env" = "development" ]; then
        target="development"
    fi
    
    print_message $YELLOW "📦 Building backend image..."
    docker build \
        --file crypto-tracker-backend/Dockerfile.optimized \
        --target $target \
        --tag ${PROJECT_NAME}-backend:$env \
        --tag ${PROJECT_NAME}-backend:latest \
        $build_args \
        ./crypto-tracker-backend
    
    print_message $YELLOW "📦 Building frontend image..."
    docker build \
        --file crypto-tracker-frontend/Dockerfile.optimized \
        --target $target \
        --tag ${PROJECT_NAME}-frontend:$env \
        --tag ${PROJECT_NAME}-frontend:latest \
        $build_args \
        ./crypto-tracker-frontend
    
    print_message $GREEN "✅ Image build completed successfully!"
    
    # Show image sizes
    print_message $BLUE "📊 Image Sizes:"
    docker images | grep $PROJECT_NAME | head -10
}

# Function to analyze Docker images
analyze_images() {
    print_message $BLUE "🔍 Analyzing Docker images..."
    
    # Check if dive is installed
    if ! command -v dive &> /dev/null; then
        print_message $YELLOW "⚠️ Installing 'dive' for detailed image analysis..."
        if command -v brew &> /dev/null; then
            brew install dive
        elif command -v apt-get &> /dev/null; then
            wget -O dive.deb https://github.com/wagoodman/dive/releases/download/v0.10.0/dive_0.10.0_linux_amd64.deb
            sudo apt install ./dive.deb
            rm dive.deb
        else
            print_message $YELLOW "Please install 'dive' manually: https://github.com/wagoodman/dive"
        fi
    fi
    
    # Analyze backend image
    print_message $YELLOW "🔍 Backend Image Analysis:"
    if docker images | grep -q "${PROJECT_NAME}-backend"; then
        docker images | grep "${PROJECT_NAME}-backend"
        echo ""
        print_message $BLUE "Run 'dive ${PROJECT_NAME}-backend:latest' for detailed layer analysis"
    else
        print_message $RED "❌ Backend image not found. Run 'build' command first."
    fi
    
    # Analyze frontend image
    print_message $YELLOW "🔍 Frontend Image Analysis:"
    if docker images | grep -q "${PROJECT_NAME}-frontend"; then
        docker images | grep "${PROJECT_NAME}-frontend"
        echo ""
        print_message $BLUE "Run 'dive ${PROJECT_NAME}-frontend:latest' for detailed layer analysis"
    else
        print_message $RED "❌ Frontend image not found. Run 'build' command first."
    fi
    
    # Show Docker system usage
    print_message $YELLOW "💾 Docker System Usage:"
    docker system df
}

# Function to security scan images
scan_images() {
    print_message $BLUE "🛡️ Security scanning Docker images..."
    
    # Check if trivy is installed
    if ! command -v trivy &> /dev/null; then
        print_message $YELLOW "⚠️ Installing 'trivy' for security scanning..."
        if command -v brew &> /dev/null; then
            brew install aquasecurity/trivy/trivy
        elif command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install wget apt-transport-https gnupg lsb-release
            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
            echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
            sudo apt-get update
            sudo apt-get install trivy
        else
            print_message $YELLOW "Please install 'trivy' manually: https://aquasecurity.github.io/trivy/"
        fi
    fi
    
    # Scan backend image
    if docker images | grep -q "${PROJECT_NAME}-backend"; then
        print_message $YELLOW "🔍 Scanning backend image..."
        trivy image --severity HIGH,CRITICAL ${PROJECT_NAME}-backend:latest
    fi
    
    # Scan frontend image
    if docker images | grep -q "${PROJECT_NAME}-frontend"; then
        print_message $YELLOW "🔍 Scanning frontend image..."
        trivy image --severity HIGH,CRITICAL ${PROJECT_NAME}-frontend:latest
    fi
    
    print_message $GREEN "✅ Security scan completed!"
}

# Function to clean up Docker resources
clean_docker() {
    print_message $BLUE "🧹 Cleaning up Docker resources..."
    
    # Show current usage
    print_message $YELLOW "📊 Current Docker Usage:"
    docker system df
    echo ""
    
    # Remove unused containers
    print_message $YELLOW "🗑️ Removing stopped containers..."
    docker container prune -f
    
    # Remove unused images
    print_message $YELLOW "🗑️ Removing unused images..."
    docker image prune -f
    
    # Remove unused volumes
    print_message $YELLOW "🗑️ Removing unused volumes..."
    docker volume prune -f
    
    # Remove unused networks
    print_message $YELLOW "🗑️ Removing unused networks..."
    docker network prune -f
    
    # Remove build cache (Docker 18.09+)
    print_message $YELLOW "🗑️ Removing build cache..."
    docker builder prune -f
    
    # Show space saved
    echo ""
    print_message $GREEN "✅ Cleanup completed!"
    print_message $YELLOW "📊 New Docker Usage:"
    docker system df
}

# Function to deploy with optimized configuration
deploy_optimized() {
    local env=${1:-$DEFAULT_ENV}
    
    print_message $BLUE "🚀 Deploying optimized containers for $env environment..."
    
    # Set environment variables
    export TARGET_ENV=$env
    export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    export VCS_REF=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')
    
    # Load environment-specific variables
    if [ -f ".env.$env" ]; then
        set -a  # automatically export all variables
        source ".env.$env"
        set +a
        print_message $GREEN "✅ Loaded environment variables from .env.$env"
    fi
    
    # Use optimized compose file
    local compose_file="docker-compose.optimized.yml"
    
    if [ ! -f "$compose_file" ]; then
        print_message $RED "❌ Optimized compose file not found: $compose_file"
        exit 1
    fi
    
    # Deploy with specific profile
    if [ "$env" = "development" ]; then
        docker-compose -f $compose_file --profile development up -d --build
    elif [ "$env" = "production" ]; then
        docker-compose -f $compose_file --profile production up -d --build
    else
        docker-compose -f $compose_file up -d --build
    fi
    
    print_message $GREEN "✅ Deployment completed!"
    
    # Show running containers
    print_message $YELLOW "📊 Running Containers:"
    docker-compose -f $compose_file ps
}

# Function to monitor container performance
monitor_containers() {
    print_message $BLUE "📊 Monitoring container performance..."
    
    # Check if ctop is installed
    if command -v ctop &> /dev/null; then
        print_message $YELLOW "🔍 Launching ctop for real-time monitoring..."
        ctop
    else
        # Use docker stats as fallback
        print_message $YELLOW "📈 Container Resource Usage:"
        docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" --no-stream
        
        echo ""
        print_message $BLUE "For better monitoring, install ctop: brew install ctop"
    fi
    
    # Show container logs summary
    print_message $YELLOW "📝 Recent Container Logs:"
    for container in $(docker ps --format "{{.Names}}" | grep crypto-tracker); do
        echo "--- $container ---"
        docker logs --tail 5 $container
        echo ""
    done
}

# Function to backup container volumes
backup_volumes() {
    print_message $BLUE "💾 Backing up container volumes..."
    
    local backup_dir="backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database volume
    if docker volume ls | grep -q postgres_data; then
        print_message $YELLOW "📦 Backing up database..."
        docker run --rm \
            -v crypto_postgres_data:/source:ro \
            -v "$(pwd)/$backup_dir":/backup \
            alpine tar czf /backup/postgres_data.tar.gz -C /source .
        print_message $GREEN "✅ Database backup completed"
    fi
    
    # Backup Redis volume
    if docker volume ls | grep -q redis_data; then
        print_message $YELLOW "📦 Backing up Redis..."
        docker run --rm \
            -v crypto_redis_data:/source:ro \
            -v "$(pwd)/$backup_dir":/backup \
            alpine tar czf /backup/redis_data.tar.gz -C /source .
        print_message $GREEN "✅ Redis backup completed"
    fi
    
    # Create backup manifest
    cat > "$backup_dir/manifest.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "environment": "${TARGET_ENV:-production}",
  "volumes": [
    "postgres_data.tar.gz",
    "redis_data.tar.gz"
  ]
}
EOF
    
    print_message $GREEN "✅ Backup completed: $backup_dir"
}

# Function to optimize Docker daemon
optimize_daemon() {
    print_message $BLUE "⚙️ Optimizing Docker daemon configuration..."
    
    local daemon_config="/etc/docker/daemon.json"
    
    # Check if daemon.json exists
    if [ ! -f "$daemon_config" ]; then
        print_message $YELLOW "📝 Creating optimized daemon.json..."
        
        sudo mkdir -p /etc/docker
        sudo tee $daemon_config > /dev/null << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "live-restore": true,
  "userland-proxy": false,
  "experimental": false,
  "metrics-addr": "127.0.0.1:9323",
  "max-concurrent-downloads": 6,
  "max-concurrent-uploads": 5
}
EOF
        
        print_message $GREEN "✅ Daemon configuration created"
        print_message $YELLOW "⚠️ Restart Docker daemon to apply changes: sudo systemctl restart docker"
    else
        print_message $YELLOW "ℹ️ Daemon configuration already exists at $daemon_config"
        cat $daemon_config
    fi
}

# Main script logic
case "${1:-help}" in
    "build")
        build_images "$2"
        ;;
    "analyze")
        analyze_images
        ;;
    "scan")
        scan_images
        ;;
    "clean")
        clean_docker
        ;;
    "deploy")
        deploy_optimized "$2"
        ;;
    "monitor")
        monitor_containers
        ;;
    "backup")
        backup_volumes
        ;;
    "optimize-daemon")
        optimize_daemon
        ;;
    "help"|*)
        print_usage
        ;;
esac