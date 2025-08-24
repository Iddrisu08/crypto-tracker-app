#!/bin/bash

# ===============================================
# ENVIRONMENT MANAGER SCRIPT
# ===============================================
# Manages different environments for the crypto tracker application.
# Handles environment switching, validation, and deployment preparation.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=""
ACTION=""
BACKEND_DIR="crypto-tracker-backend"
FRONTEND_DIR="crypto-tracker-frontend"

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print usage
print_usage() {
    echo "Usage: $0 <environment> <action>"
    echo ""
    echo "Environments:"
    echo "  development  - Local development environment"
    echo "  staging      - Staging environment for testing"
    echo "  production   - Production environment"
    echo ""
    echo "Actions:"
    echo "  validate     - Validate environment configuration"
    echo "  setup        - Set up environment files"
    echo "  switch       - Switch to specified environment"
    echo "  deploy       - Prepare for deployment"
    echo "  backup       - Backup current environment config"
    echo "  restore      - Restore environment config from backup"
    echo "  status       - Show current environment status"
    echo ""
    echo "Examples:"
    echo "  $0 development setup"
    echo "  $0 staging validate"
    echo "  $0 production deploy"
}

# Function to validate environment
validate_environment() {
    local env=$1
    print_message $BLUE "🔍 Validating $env environment..."
    
    # Check if environment files exist
    local backend_env="$BACKEND_DIR/.env.$env"
    local frontend_env="$FRONTEND_DIR/.env.$env"
    
    if [ ! -f "$backend_env" ]; then
        print_message $RED "❌ Backend environment file not found: $backend_env"
        return 1
    fi
    
    if [ ! -f "$frontend_env" ]; then
        print_message $RED "❌ Frontend environment file not found: $frontend_env"
        return 1
    fi
    
    # Validate required variables based on environment
    case $env in
        "development")
            validate_development_env "$backend_env" "$frontend_env"
            ;;
        "staging")
            validate_staging_env "$backend_env" "$frontend_env"
            ;;
        "production")
            validate_production_env "$backend_env" "$frontend_env"
            ;;
        *)
            print_message $RED "❌ Unknown environment: $env"
            return 1
            ;;
    esac
    
    print_message $GREEN "✅ Environment validation successful!"
}

# Function to validate development environment
validate_development_env() {
    local backend_env=$1
    local frontend_env=$2
    
    # Required variables for development
    local required_backend_vars=(
        "FLASK_ENV"
        "DATABASE_URL"
        "JWT_SECRET_KEY"
        "SECRET_KEY"
    )
    
    local required_frontend_vars=(
        "VITE_API_BASE_URL"
        "VITE_ENV_NAME"
    )
    
    validate_env_vars "$backend_env" "${required_backend_vars[@]}"
    validate_env_vars "$frontend_env" "${required_frontend_vars[@]}"
}

# Function to validate staging environment
validate_staging_env() {
    local backend_env=$1
    local frontend_env=$2
    
    # Required variables for staging
    local required_backend_vars=(
        "FLASK_ENV"
        "DATABASE_URL"
        "REDIS_URL"
        "JWT_SECRET_KEY"
        "SECRET_KEY"
    )
    
    local required_frontend_vars=(
        "VITE_API_BASE_URL"
        "VITE_ENV_NAME"
    )
    
    validate_env_vars "$backend_env" "${required_backend_vars[@]}"
    validate_env_vars "$frontend_env" "${required_frontend_vars[@]}"
}

# Function to validate production environment
validate_production_env() {
    local backend_env=$1
    local frontend_env=$2
    
    # Required variables for production
    local required_backend_vars=(
        "FLASK_ENV"
        "DATABASE_URL"
        "REDIS_URL"
        "JWT_SECRET_KEY"
        "SECRET_KEY"
        "SENTRY_DSN"
    )
    
    local required_frontend_vars=(
        "VITE_API_BASE_URL"
        "VITE_ENV_NAME"
    )
    
    validate_env_vars "$backend_env" "${required_backend_vars[@]}"
    validate_env_vars "$frontend_env" "${required_frontend_vars[@]}"
    
    # Additional production-specific validations
    check_production_security "$backend_env" "$frontend_env"
}

# Function to validate environment variables
validate_env_vars() {
    local env_file=$1
    shift
    local required_vars=("$@")
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$env_file" || grep -q "^${var}=$" "$env_file"; then
            print_message $RED "❌ Missing or empty variable: $var in $env_file"
            return 1
        fi
    done
}

# Function to check production security
check_production_security() {
    local backend_env=$1
    local frontend_env=$2
    
    # Check for development values in production
    if grep -q "dev-" "$backend_env"; then
        print_message $RED "❌ Development secrets found in production environment!"
        return 1
    fi
    
    # Check debug settings
    if grep -q "FLASK_DEBUG=true" "$backend_env"; then
        print_message $RED "❌ Debug mode enabled in production!"
        return 1
    fi
    
    if grep -q "VITE_ENABLE_DEBUG_LOGGING=true" "$frontend_env"; then
        print_message $YELLOW "⚠️  Debug logging enabled in production"
    fi
}

# Function to set up environment
setup_environment() {
    local env=$1
    print_message $BLUE "🔧 Setting up $env environment..."
    
    # Copy environment files if they don't exist
    local backend_env="$BACKEND_DIR/.env.$env"
    local frontend_env="$FRONTEND_DIR/.env.$env"
    
    if [ -f "$backend_env" ]; then
        print_message $GREEN "✅ Backend environment file already exists: $backend_env"
    else
        print_message $RED "❌ Backend environment file not found: $backend_env"
        return 1
    fi
    
    if [ -f "$frontend_env" ]; then
        print_message $GREEN "✅ Frontend environment file already exists: $frontend_env"
    else
        print_message $RED "❌ Frontend environment file not found: $frontend_env"
        return 1
    fi
    
    print_message $GREEN "✅ Environment setup complete!"
}

# Function to switch environment
switch_environment() {
    local env=$1
    print_message $BLUE "🔄 Switching to $env environment..."
    
    # Backup current .env files
    if [ -f "$BACKEND_DIR/.env" ]; then
        cp "$BACKEND_DIR/.env" "$BACKEND_DIR/.env.backup"
    fi
    
    if [ -f "$FRONTEND_DIR/.env" ]; then
        cp "$FRONTEND_DIR/.env" "$FRONTEND_DIR/.env.backup"
    fi
    
    # Copy environment-specific files to .env
    cp "$BACKEND_DIR/.env.$env" "$BACKEND_DIR/.env"
    cp "$FRONTEND_DIR/.env.$env" "$FRONTEND_DIR/.env"
    
    print_message $GREEN "✅ Switched to $env environment!"
    print_message $YELLOW "⚠️  Remember to restart your development servers"
}

# Function to prepare for deployment
prepare_deployment() {
    local env=$1
    print_message $BLUE "🚀 Preparing $env deployment..."
    
    # Validate environment first
    validate_environment "$env"
    
    # Create deployment artifacts directory
    mkdir -p "deployment-artifacts/$env"
    
    # Copy environment files to deployment artifacts
    cp "$BACKEND_DIR/.env.$env" "deployment-artifacts/$env/backend.env"
    cp "$FRONTEND_DIR/.env.$env" "deployment-artifacts/$env/frontend.env"
    
    # Generate deployment info
    cat > "deployment-artifacts/$env/deployment-info.json" << EOF
{
  "environment": "$env",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
  "user": "$(whoami)"
}
EOF
    
    # Create deployment checklist
    create_deployment_checklist "$env"
    
    print_message $GREEN "✅ Deployment preparation complete!"
    print_message $BLUE "📁 Artifacts available in: deployment-artifacts/$env/"
}

# Function to create deployment checklist
create_deployment_checklist() {
    local env=$1
    local checklist_file="deployment-artifacts/$env/deployment-checklist.md"
    
    cat > "$checklist_file" << EOF
# Deployment Checklist - $env Environment

## Pre-Deployment
- [ ] All tests pass
- [ ] Environment variables validated
- [ ] Database migrations ready
- [ ] Secrets properly configured
- [ ] Backup plan in place

## During Deployment
- [ ] Deploy backend first
- [ ] Verify backend health checks
- [ ] Deploy frontend
- [ ] Verify frontend loads correctly
- [ ] Run smoke tests

## Post-Deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify all features working
- [ ] Update documentation
- [ ] Notify team of successful deployment

## Rollback Plan
- [ ] Database rollback scripts ready
- [ ] Previous version tagged
- [ ] Rollback procedure documented
EOF
    
    print_message $GREEN "✅ Deployment checklist created: $checklist_file"
}

# Function to backup environment configuration
backup_environment() {
    print_message $BLUE "💾 Backing up environment configuration..."
    
    local backup_dir="environment-backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup all environment files
    if [ -d "$BACKEND_DIR" ]; then
        cp "$BACKEND_DIR"/.env.* "$backup_dir/" 2>/dev/null || true
    fi
    
    if [ -d "$FRONTEND_DIR" ]; then
        cp "$FRONTEND_DIR"/.env.* "$backup_dir/" 2>/dev/null || true
    fi
    
    # Create backup manifest
    cat > "$backup_dir/manifest.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "files": [$(find "$backup_dir" -name ".env.*" -exec basename {} \; | sed 's/^/    "/' | sed 's/$/"/' | paste -sd,)]
}
EOF
    
    print_message $GREEN "✅ Backup created: $backup_dir"
}

# Function to show environment status
show_status() {
    print_message $BLUE "📊 Environment Status"
    echo ""
    
    # Show current environment
    if [ -f "$BACKEND_DIR/.env" ]; then
        local current_env=$(grep "^ENV_NAME=" "$BACKEND_DIR/.env" | cut -d'=' -f2 || echo "unknown")
        print_message $GREEN "Current Backend Environment: $current_env"
    else
        print_message $RED "No active backend environment"
    fi
    
    if [ -f "$FRONTEND_DIR/.env" ]; then
        local current_env=$(grep "^VITE_ENV_NAME=" "$FRONTEND_DIR/.env" | cut -d'=' -f2 || echo "unknown")
        print_message $GREEN "Current Frontend Environment: $current_env"
    else
        print_message $RED "No active frontend environment"
    fi
    
    echo ""
    print_message $BLUE "Available Environment Files:"
    
    # List available environment files
    find . -name ".env.*" -not -name ".env.backup" | sort
}

# Main script logic
if [ $# -ne 2 ]; then
    print_usage
    exit 1
fi

ENVIRONMENT=$1
ACTION=$2

# Validate environment parameter
case $ENVIRONMENT in
    "development"|"staging"|"production")
        ;;
    *)
        print_message $RED "❌ Invalid environment: $ENVIRONMENT"
        print_usage
        exit 1
        ;;
esac

# Execute action
case $ACTION in
    "validate")
        validate_environment "$ENVIRONMENT"
        ;;
    "setup")
        setup_environment "$ENVIRONMENT"
        ;;
    "switch")
        switch_environment "$ENVIRONMENT"
        ;;
    "deploy")
        prepare_deployment "$ENVIRONMENT"
        ;;
    "backup")
        backup_environment
        ;;
    "status")
        show_status
        ;;
    *)
        print_message $RED "❌ Invalid action: $ACTION"
        print_usage
        exit 1
        ;;
esac