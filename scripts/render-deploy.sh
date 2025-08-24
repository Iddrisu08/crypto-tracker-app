#!/bin/bash

# ===============================================
# RENDER DEPLOYMENT SCRIPT
# ===============================================
# Manual deployment script for Render.com with environment management,
# database migrations, and deployment verification.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR=$(pwd)
RENDER_CONFIG_FILE="render.yaml"
ENV_FILE=".env.production"

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print usage
print_usage() {
    echo "Render Deployment Script for Crypto Tracker"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  deploy          - Deploy to Render using blueprint"
    echo "  preview         - Create preview deployment"
    echo "  status          - Check deployment status"
    echo "  logs            - View service logs"
    echo "  migrate         - Run database migrations"
    echo "  rollback        - Rollback to previous deployment"
    echo "  cleanup         - Clean up preview deployments"
    echo "  setup           - Initial Render setup"
    echo ""
    echo "Options:"
    echo "  --env <env>     - Environment (production, staging, preview)"
    echo "  --service <svc> - Specific service to target"
    echo "  --force         - Force deployment without confirmation"
    echo "  --wait          - Wait for deployment to complete"
    echo ""
    echo "Examples:"
    echo "  $0 deploy --env production --wait"
    echo "  $0 preview --force"
    echo "  $0 logs --service crypto-tracker-backend"
    echo "  $0 migrate --env production"
}

# Function to check prerequisites
check_prerequisites() {
    print_message $BLUE "🔍 Checking prerequisites..."
    
    # Check if render CLI is installed
    if ! command -v render &> /dev/null; then
        print_message $YELLOW "📦 Installing Render CLI..."
        curl -fsSL https://cli.render.com/install | sh
        export PATH="$HOME/.render/bin:$PATH"
        
        if ! command -v render &> /dev/null; then
            print_message $RED "❌ Failed to install Render CLI"
            exit 1
        fi
    fi
    
    # Check if authenticated
    if ! render auth whoami &> /dev/null; then
        print_message $YELLOW "🔐 Please authenticate with Render..."
        print_message $CYAN "Run: render auth login"
        exit 1
    fi
    
    # Check if render.yaml exists
    if [ ! -f "$RENDER_CONFIG_FILE" ]; then
        print_message $RED "❌ render.yaml not found in current directory"
        exit 1
    fi
    
    print_message $GREEN "✅ Prerequisites check passed"
}

# Function to validate configuration
validate_config() {
    print_message $BLUE "🔍 Validating configuration..."
    
    # Check render.yaml syntax
    if command -v python3 &> /dev/null; then
        python3 -c "import yaml; yaml.safe_load(open('$RENDER_CONFIG_FILE', 'r'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_message $GREEN "✅ render.yaml syntax is valid"
        else
            print_message $RED "❌ Invalid render.yaml syntax"
            exit 1
        fi
    fi
    
    # Check required files
    local required_files=(
        "crypto-tracker-backend/requirements.txt"
        "crypto-tracker-frontend/package.json"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_message $GREEN "✅ $file exists"
        else
            print_message $RED "❌ Required file not found: $file"
            exit 1
        fi
    done
}

# Function to deploy to Render
deploy_to_render() {
    local environment=${1:-production}
    local force=${2:-false}
    local wait=${3:-false}
    
    print_message $PURPLE "🚀 Starting deployment to $environment..."
    
    # Confirmation unless force is true
    if [ "$force" != "true" ]; then
        echo ""
        print_message $YELLOW "⚠️  You are about to deploy to $environment environment."
        read -p "Are you sure? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message $BLUE "ℹ️ Deployment cancelled"
            return 0
        fi
    fi
    
    # Deploy using blueprint
    if [ "$environment" = "preview" ]; then
        print_message $BLUE "🔄 Creating preview deployment..."
        render blueprint apply --preview --yes
    else
        print_message $BLUE "🔄 Deploying to $environment..."
        render blueprint apply --yes
    fi
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "✅ Deployment initiated successfully!"
        
        # Wait for deployment if requested
        if [ "$wait" = "true" ]; then
            wait_for_deployment "$environment"
        fi
        
        # Show service URLs
        show_service_urls "$environment"
    else
        print_message $RED "❌ Deployment failed"
        return 1
    fi
}

# Function to wait for deployment to complete
wait_for_deployment() {
    local environment=$1
    
    print_message $YELLOW "⏳ Waiting for deployment to complete..."
    
    # Wait for services to be deployed (timeout after 10 minutes)
    local timeout=600
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        # Check service status
        local services_ready=true
        
        # Get service status (this is a simplified check)
        if ! render service list | grep -q "Live"; then
            services_ready=false
        fi
        
        if [ "$services_ready" = "true" ]; then
            print_message $GREEN "✅ Deployment completed successfully!"
            break
        fi
        
        sleep 30
        elapsed=$((elapsed + 30))
        print_message $CYAN "⏳ Still deploying... ($elapsed/$timeout seconds)"
    done
    
    if [ $elapsed -ge $timeout ]; then
        print_message $YELLOW "⚠️ Deployment timeout reached. Check Render dashboard for status."
    fi
}

# Function to show service URLs
show_service_urls() {
    local environment=$1
    
    print_message $BLUE "📍 Service URLs:"
    
    # Get service information
    render service list --format json > /tmp/render_services.json 2>/dev/null || true
    
    if [ -f "/tmp/render_services.json" ] && [ -s "/tmp/render_services.json" ]; then
        # Parse and display URLs
        if command -v jq &> /dev/null; then
            local frontend_url=$(jq -r '.[] | select(.name=="crypto-tracker-frontend") | .url' /tmp/render_services.json 2>/dev/null || echo "")
            local backend_url=$(jq -r '.[] | select(.name=="crypto-tracker-backend") | .url' /tmp/render_services.json 2>/dev/null || echo "")
            
            if [ -n "$frontend_url" ] && [ "$frontend_url" != "null" ]; then
                echo "🌐 Frontend: $frontend_url"
            fi
            
            if [ -n "$backend_url" ] && [ "$backend_url" != "null" ]; then
                echo "🔗 Backend:  $backend_url"
            fi
        fi
    fi
    
    rm -f /tmp/render_services.json
    
    echo ""
    print_message $CYAN "📊 View deployment status: https://dashboard.render.com"
}

# Function to check deployment status
check_status() {
    print_message $BLUE "📊 Checking deployment status..."
    
    render service list --format table
    
    echo ""
    print_message $BLUE "📈 Recent deployments:"
    render service list --format json | jq -r '.[] | "\(.name): \(.status) (Updated: \(.updatedAt))"' 2>/dev/null || echo "Status information not available"
}

# Function to view service logs
view_logs() {
    local service_name=${1:-""}
    
    if [ -z "$service_name" ]; then
        print_message $RED "❌ Please specify a service name"
        print_message $CYAN "Available services: crypto-tracker-frontend, crypto-tracker-backend"
        return 1
    fi
    
    print_message $BLUE "📄 Viewing logs for: $service_name"
    render service logs "$service_name" --tail 100 --follow
}

# Function to run database migrations
run_migrations() {
    local environment=${1:-production}
    
    print_message $BLUE "🗄️ Running database migrations for $environment..."
    
    # This would typically run migrations on the deployed service
    print_message $YELLOW "⚠️ Manual migration process:"
    echo "1. Connect to your Render service shell"
    echo "2. Run: python manage.py migrate"
    echo "3. Or use the database migration job if configured"
    
    print_message $CYAN "💡 To automate migrations, consider adding a migration job to render.yaml"
}

# Function to rollback deployment
rollback_deployment() {
    local service_name=${1:-""}
    
    if [ -z "$service_name" ]; then
        print_message $RED "❌ Please specify a service name for rollback"
        return 1
    fi
    
    print_message $YELLOW "⚠️ Rolling back service: $service_name"
    
    # Get previous deployment
    print_message $BLUE "🔄 Initiating rollback..."
    
    # Note: Render CLI doesn't have direct rollback, so this would need to be done via dashboard
    print_message $YELLOW "⚠️ Rollback must be done through Render dashboard:"
    echo "1. Go to https://dashboard.render.com"
    echo "2. Select the service: $service_name"
    echo "3. Go to the 'Deploys' tab"
    echo "4. Click 'Redeploy' on a previous successful deployment"
}

# Function to cleanup preview deployments
cleanup_previews() {
    print_message $BLUE "🧹 Cleaning up preview deployments..."
    
    # List preview services
    render service list --format json | jq -r '.[] | select(.name | contains("preview")) | .name' 2>/dev/null || true
    
    print_message $YELLOW "⚠️ Preview cleanup must be done manually through Render dashboard"
    print_message $CYAN "💡 Go to https://dashboard.render.com and delete unused preview services"
}

# Function for initial setup
initial_setup() {
    print_message $PURPLE "⚙️ Initial Render setup..."
    
    # Check if user is authenticated
    if ! render auth whoami &> /dev/null; then
        print_message $YELLOW "🔐 Authenticating with Render..."
        render auth login
    fi
    
    # Validate configuration
    validate_config
    
    # Create initial deployment
    print_message $BLUE "🚀 Creating initial deployment..."
    deploy_to_render "production" "false" "true"
    
    print_message $GREEN "✅ Initial setup completed!"
    
    echo ""
    print_message $CYAN "📚 Next steps:"
    echo "1. Configure environment variables in Render dashboard"
    echo "2. Set up custom domains if needed"
    echo "3. Configure monitoring and alerts"
    echo "4. Test your application thoroughly"
}

# Function to run health checks
run_health_checks() {
    print_message $BLUE "🏥 Running health checks..."
    
    # Get service URLs
    local frontend_url=""
    local backend_url=""
    
    if command -v jq &> /dev/null; then
        render service list --format json > /tmp/render_services.json 2>/dev/null || true
        if [ -f "/tmp/render_services.json" ]; then
            frontend_url=$(jq -r '.[] | select(.name=="crypto-tracker-frontend") | .url' /tmp/render_services.json 2>/dev/null || echo "")
            backend_url=$(jq -r '.[] | select(.name=="crypto-tracker-backend") | .url' /tmp/render_services.json 2>/dev/null || echo "")
        fi
        rm -f /tmp/render_services.json
    fi
    
    # Test frontend
    if [ -n "$frontend_url" ] && [ "$frontend_url" != "null" ]; then
        if curl -f -s "$frontend_url" > /dev/null; then
            print_message $GREEN "✅ Frontend is healthy: $frontend_url"
        else
            print_message $RED "❌ Frontend health check failed: $frontend_url"
        fi
    fi
    
    # Test backend
    if [ -n "$backend_url" ] && [ "$backend_url" != "null" ]; then
        if curl -f -s "$backend_url/api/health" > /dev/null; then
            print_message $GREEN "✅ Backend is healthy: $backend_url/api/health"
        else
            print_message $RED "❌ Backend health check failed: $backend_url/api/health"
        fi
    fi
}

# Main script logic
COMMAND=""
ENVIRONMENT="production"
SERVICE=""
FORCE="false"
WAIT="false"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --service)
            SERVICE="$2"
            shift 2
            ;;
        --force)
            FORCE="true"
            shift
            ;;
        --wait)
            WAIT="true"
            shift
            ;;
        *)
            if [ -z "$COMMAND" ]; then
                COMMAND="$1"
            fi
            shift
            ;;
    esac
done

# Check prerequisites for most commands
case "$COMMAND" in
    "help"|"")
        print_usage
        exit 0
        ;;
    *)
        check_prerequisites
        ;;
esac

# Execute command
case "$COMMAND" in
    "deploy")
        validate_config
        deploy_to_render "$ENVIRONMENT" "$FORCE" "$WAIT"
        ;;
    "preview")
        validate_config
        deploy_to_render "preview" "$FORCE" "$WAIT"
        ;;
    "status")
        check_status
        ;;
    "logs")
        view_logs "$SERVICE"
        ;;
    "migrate")
        run_migrations "$ENVIRONMENT"
        ;;
    "rollback")
        rollback_deployment "$SERVICE"
        ;;
    "cleanup")
        cleanup_previews
        ;;
    "setup")
        initial_setup
        ;;
    "health")
        run_health_checks
        ;;
    *)
        print_message $RED "❌ Unknown command: $COMMAND"
        print_usage
        exit 1
        ;;
esac