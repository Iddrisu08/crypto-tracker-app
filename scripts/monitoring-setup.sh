#!/bin/bash

# ===============================================
# MONITORING SETUP SCRIPT
# ===============================================
# Automated setup for crypto tracker monitoring infrastructure.
# Installs and configures Prometheus, Grafana, AlertManager, and ELK stack.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR=$(pwd)
MONITORING_DIR="$PROJECT_DIR/monitoring"
DOCKER_COMPOSE_FILE="$MONITORING_DIR/docker-compose.monitoring.yml"
ENV_FILE="$MONITORING_DIR/.env.monitoring"

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print usage
print_usage() {
    echo "Monitoring Setup Tool for Crypto Tracker"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  setup           - Complete monitoring stack setup"
    echo "  install         - Install monitoring services"
    echo "  configure       - Configure monitoring settings"
    echo "  start           - Start monitoring services"
    echo "  stop            - Stop monitoring services"
    echo "  restart         - Restart monitoring services"
    echo "  status          - Show monitoring service status"
    echo "  logs <service>  - Show logs for specific service"
    echo "  cleanup         - Remove monitoring data (destructive)"
    echo "  backup          - Backup monitoring configuration and data"
    echo ""
    echo "Options:"
    echo "  --minimal       - Install minimal monitoring (Prometheus + Grafana only)"
    echo "  --full          - Install full monitoring stack (default)"
    echo "  --env <file>    - Use custom environment file"
    echo ""
    echo "Examples:"
    echo "  $0 setup --minimal"
    echo "  $0 install --full"
    echo "  $0 logs prometheus"
    echo "  $0 backup"
}

# Function to create monitoring environment file
create_monitoring_env() {
    print_message $BLUE "🔧 Creating monitoring environment configuration..."
    
    cat > "$ENV_FILE" << 'EOF'
# ===============================================
# MONITORING ENVIRONMENT CONFIGURATION
# ===============================================

# -----------------------------------------------
# GRAFANA CONFIGURATION
# -----------------------------------------------
GRAFANA_ADMIN_PASSWORD=crypto_admin_2024
GRAFANA_SECRET_KEY=crypto_grafana_secret_key_2024

# -----------------------------------------------
# DATABASE CONFIGURATION
# -----------------------------------------------
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_password_2024
POSTGRES_DB=crypto_tracker

# -----------------------------------------------
# ALERTING CONFIGURATION
# -----------------------------------------------
# Email settings for alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Alert email addresses
DEFAULT_ALERT_EMAIL=alerts@crypto-tracker.com
CRITICAL_ALERT_EMAIL=critical@crypto-tracker.com
WARNING_ALERT_EMAIL=warnings@crypto-tracker.com
PLATFORM_TEAM_EMAIL=platform@crypto-tracker.com
DATABASE_TEAM_EMAIL=database@crypto-tracker.com
SECURITY_TEAM_EMAIL=security@crypto-tracker.com
PRODUCT_TEAM_EMAIL=product@crypto-tracker.com
INFRASTRUCTURE_TEAM_EMAIL=infra@crypto-tracker.com
ALERT_FROM_EMAIL=monitoring@crypto-tracker.com

# -----------------------------------------------
# SLACK INTEGRATION
# -----------------------------------------------
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CRITICAL_CHANNEL=#critical-alerts
SLACK_WARNING_CHANNEL=#warnings
SLACK_GENERAL_CHANNEL=#monitoring

# -----------------------------------------------
# PAGERDUTY INTEGRATION (OPTIONAL)
# -----------------------------------------------
PAGERDUTY_ROUTING_KEY=your-pagerduty-routing-key

# -----------------------------------------------
# EXTERNAL MONITORING
# -----------------------------------------------
EXTERNAL_PROMETHEUS_URL=
EXTERNAL_GRAFANA_URL=

EOF
    
    print_message $GREEN "✅ Monitoring environment file created: $ENV_FILE"
    print_message $YELLOW "⚠️  Please update the configuration with your actual values!"
}

# Function to create required directories
create_directories() {
    print_message $BLUE "📁 Creating monitoring directories..."
    
    local dirs=(
        "$MONITORING_DIR/grafana/dashboards"
        "$MONITORING_DIR/grafana/provisioning/dashboards"
        "$MONITORING_DIR/grafana/provisioning/datasources"
        "$MONITORING_DIR/grafana/provisioning/notifiers"
        "$MONITORING_DIR/prometheus/rules"
        "$MONITORING_DIR/prometheus/alerts"
        "$MONITORING_DIR/alertmanager/templates"
        "$MONITORING_DIR/logstash/pipeline"
        "$MONITORING_DIR/logstash/config"
        "$MONITORING_DIR/filebeat"
        "$MONITORING_DIR/data/prometheus"
        "$MONITORING_DIR/data/grafana"
        "$MONITORING_DIR/data/alertmanager"
        "$MONITORING_DIR/data/elasticsearch"
        "$MONITORING_DIR/backups"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        print_message $GREEN "✅ Created: $dir"
    done
}

# Function to create Grafana provisioning files
create_grafana_provisioning() {
    print_message $BLUE "⚙️ Creating Grafana provisioning configuration..."
    
    # Datasource configuration
    cat > "$MONITORING_DIR/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "30s"
      queryTimeout: "60s"
      httpMethod: "POST"

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
    jsonData:
      maxLines: 1000

  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "logstash-*"
    jsonData:
      interval: "Daily"
      timeField: "@timestamp"
      esVersion: 70
EOF
    
    # Dashboard provisioning
    cat > "$MONITORING_DIR/grafana/provisioning/dashboards/default.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF
    
    print_message $GREEN "✅ Grafana provisioning configuration created"
}

# Function to create additional configuration files
create_additional_configs() {
    print_message $BLUE "📝 Creating additional configuration files..."
    
    # Blackbox exporter configuration
    cat > "$MONITORING_DIR/blackbox.yml" << 'EOF'
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []  # Defaults to 2xx
      method: GET
      follow_redirects: true
      fail_if_ssl: false
      fail_if_not_ssl: false
      
  http_post_2xx:
    prober: http
    timeout: 5s
    http:
      method: POST
      headers:
        Content-Type: application/json
      body: '{}'

  tcp_connect:
    prober: tcp
    timeout: 5s

  icmp:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"
EOF
    
    # PostgreSQL exporter queries
    cat > "$MONITORING_DIR/postgres-queries.yaml" << 'EOF'
pg_database:
  query: "SELECT pg_database.datname, pg_database_size(pg_database.datname) as size_bytes FROM pg_database"
  master: true
  cache_seconds: 30
  metrics:
    - datname:
        usage: "LABEL"
        description: "Database name"
    - size_bytes:
        usage: "GAUGE"
        description: "Database size in bytes"

pg_stat_user_tables:
  query: "SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, n_tup_del FROM pg_stat_user_tables"
  master: true
  cache_seconds: 30
  metrics:
    - schemaname:
        usage: "LABEL"
        description: "Schema name"
    - tablename:
        usage: "LABEL" 
        description: "Table name"
    - seq_scan:
        usage: "COUNTER"
        description: "Sequential scans"
    - idx_scan:
        usage: "COUNTER"
        description: "Index scans"
EOF
    
    # Filebeat configuration
    cat > "$MONITORING_DIR/filebeat.yml" << 'EOF'
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

output.logstash:
  hosts: ["logstash:5044"]

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
EOF
    
    print_message $GREEN "✅ Additional configuration files created"
}

# Function to install monitoring stack
install_monitoring() {
    local stack_type=${1:-full}
    
    print_message $BLUE "🚀 Installing monitoring stack ($stack_type)..."
    
    # Check if Docker and Docker Compose are available
    if ! command -v docker &> /dev/null; then
        print_message $RED "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_message $RED "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Create network if it doesn't exist
    docker network create crypto_monitoring_network 2>/dev/null || true
    
    # Load environment variables
    if [ -f "$ENV_FILE" ]; then
        export $(cat "$ENV_FILE" | xargs)
    fi
    
    # Start services based on stack type
    cd "$MONITORING_DIR"
    
    if [ "$stack_type" = "minimal" ]; then
        print_message $YELLOW "📦 Starting minimal monitoring stack..."
        docker-compose -f docker-compose.monitoring.yml --profile minimal up -d
    else
        print_message $YELLOW "📦 Starting full monitoring stack..."
        docker-compose -f docker-compose.monitoring.yml up -d
    fi
    
    # Wait for services to start
    print_message $YELLOW "⏳ Waiting for services to start..."
    sleep 30
    
    # Check service health
    check_service_health
}

# Function to check service health
check_service_health() {
    print_message $BLUE "🏥 Checking service health..."
    
    local services=("prometheus:9090" "grafana:3001")
    
    for service in "${services[@]}"; do
        local name=$(echo $service | cut -d':' -f1)
        local port=$(echo $service | cut -d':' -f2)
        
        if curl -f -s "http://localhost:$port" >/dev/null; then
            print_message $GREEN "✅ $name is healthy"
        else
            print_message $RED "❌ $name is not responding"
        fi
    done
}

# Function to show monitoring status
show_status() {
    print_message $BLUE "📊 Monitoring Services Status"
    echo ""
    
    cd "$MONITORING_DIR"
    docker-compose -f docker-compose.monitoring.yml ps
    
    echo ""
    print_message $BLUE "📍 Service URLs:"
    echo "Prometheus:    http://localhost:9090"
    echo "Grafana:       http://localhost:3001 (admin/crypto_admin_2024)"
    echo "AlertManager:  http://localhost:9093"
    echo "Kibana:        http://localhost:5601"
    echo "Elasticsearch: http://localhost:9200"
}

# Function to show logs
show_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        print_message $RED "❌ Please specify a service name"
        print_usage
        exit 1
    fi
    
    cd "$MONITORING_DIR"
    docker-compose -f docker-compose.monitoring.yml logs -f --tail=100 "$service"
}

# Function to backup monitoring data
backup_monitoring() {
    print_message $BLUE "💾 Creating monitoring backup..."
    
    local backup_dir="$MONITORING_DIR/backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup Grafana data
    if docker ps | grep -q crypto_grafana; then
        print_message $YELLOW "📊 Backing up Grafana data..."
        docker exec crypto_grafana grafana-cli admin export-dashboard > "$backup_dir/grafana-dashboards.json" 2>/dev/null || true
    fi
    
    # Backup Prometheus data
    print_message $YELLOW "📈 Backing up Prometheus data..."
    docker run --rm -v crypto_prometheus_data:/source -v "$backup_dir":/backup alpine \
        tar czf /backup/prometheus-data.tar.gz -C /source . 2>/dev/null || true
    
    # Backup configuration files
    print_message $YELLOW "⚙️ Backing up configuration..."
    cp -r "$MONITORING_DIR"/*.yml "$backup_dir/" 2>/dev/null || true
    cp "$ENV_FILE" "$backup_dir/" 2>/dev/null || true
    
    # Create backup manifest
    cat > "$backup_dir/manifest.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "1.0.0",
  "services": [
    "prometheus",
    "grafana",
    "alertmanager",
    "elasticsearch"
  ],
  "files": [
    "prometheus-data.tar.gz",
    "grafana-dashboards.json",
    "prometheus.yml",
    "alertmanager.yml",
    ".env.monitoring"
  ]
}
EOF
    
    print_message $GREEN "✅ Backup completed: $backup_dir"
}

# Function to cleanup monitoring data
cleanup_monitoring() {
    print_message $YELLOW "⚠️  This will remove all monitoring data and containers!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message $RED "🧹 Cleaning up monitoring stack..."
        
        cd "$MONITORING_DIR"
        docker-compose -f docker-compose.monitoring.yml down -v --remove-orphans
        
        # Remove named volumes
        docker volume rm crypto_prometheus_data 2>/dev/null || true
        docker volume rm crypto_grafana_data 2>/dev/null || true
        docker volume rm crypto_alertmanager_data 2>/dev/null || true
        docker volume rm crypto_elasticsearch_data 2>/dev/null || true
        
        print_message $GREEN "✅ Cleanup completed"
    else
        print_message $BLUE "ℹ️ Cleanup cancelled"
    fi
}

# Function to complete setup
complete_setup() {
    local stack_type=${1:-full}
    
    print_message $PURPLE "🚀 Starting complete monitoring setup..."
    
    # Create environment file
    if [ ! -f "$ENV_FILE" ]; then
        create_monitoring_env
    fi
    
    # Create directories
    create_directories
    
    # Create Grafana provisioning
    create_grafana_provisioning
    
    # Create additional configs
    create_additional_configs
    
    # Install and start services
    install_monitoring "$stack_type"
    
    # Show final status
    echo ""
    print_message $GREEN "🎉 Monitoring setup completed successfully!"
    echo ""
    show_status
    
    echo ""
    print_message $BLUE "📚 Next Steps:"
    echo "1. Update $ENV_FILE with your actual configuration"
    echo "2. Access Grafana at http://localhost:3001 (admin/crypto_admin_2024)"
    echo "3. Import dashboards from monitoring/grafana/dashboards/"
    echo "4. Configure alert notification channels in AlertManager"
    echo "5. Test alerts by triggering some conditions"
    
    print_message $YELLOW "⚠️  Don't forget to change default passwords!"
}

# Main script logic
STACK_TYPE="full"
ENV_FILE_CUSTOM=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --minimal)
            STACK_TYPE="minimal"
            shift
            ;;
        --full)
            STACK_TYPE="full"
            shift
            ;;
        --env)
            ENV_FILE_CUSTOM="$2"
            shift 2
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Use custom env file if provided
if [ -n "$ENV_FILE_CUSTOM" ]; then
    ENV_FILE="$ENV_FILE_CUSTOM"
fi

# Execute command
case "${COMMAND:-help}" in
    "setup")
        complete_setup "$STACK_TYPE"
        ;;
    "install")
        install_monitoring "$STACK_TYPE"
        ;;
    "configure")
        create_monitoring_env
        create_grafana_provisioning
        create_additional_configs
        ;;
    "start")
        cd "$MONITORING_DIR"
        if [ "$STACK_TYPE" = "minimal" ]; then
            docker-compose -f docker-compose.monitoring.yml --profile minimal up -d
        else
            docker-compose -f docker-compose.monitoring.yml up -d
        fi
        ;;
    "stop")
        cd "$MONITORING_DIR"
        docker-compose -f docker-compose.monitoring.yml down
        ;;
    "restart")
        cd "$MONITORING_DIR"
        docker-compose -f docker-compose.monitoring.yml restart
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "backup")
        backup_monitoring
        ;;
    "cleanup")
        cleanup_monitoring
        ;;
    "help"|*)
        print_usage
        ;;
esac