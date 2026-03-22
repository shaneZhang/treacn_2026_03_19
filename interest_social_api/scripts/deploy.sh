#!/bin/bash
# Interest Social API - Deployment Script
# Usage: ./deploy.sh [staging|production]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy-$(date +%Y%m%d-%H%M%S).log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        log_error ".env file not found! Please create it from .env.example"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running!"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed!"
        exit 1
    fi
    
    # Check if required directories exist
    for dir in logs data/postgres data/redis nginx/ssl; do
        if [[ ! -d "$dir" ]]; then
            log_warning "Creating missing directory: $dir"
            mkdir -p "$dir"
        fi
    done
    
    # Check SSL certificates
    if [[ ! -f "nginx/ssl/cert.pem" ]] || [[ ! -f "nginx/ssl/key.pem" ]]; then
        log_warning "SSL certificates not found. Using self-signed certificates..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    fi
    
    log_success "Pre-deployment checks passed"
}

# Backup before deployment
backup_before_deploy() {
    log_info "Creating backup before deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if it's running
    if docker-compose ps | grep -q "postgres.*Up"; then
        BACKUP_FILE="$BACKUP_DIR/pre-deploy-$(date +%Y%m%d-%H%M%S).sql.gz"
        log_info "Backing up database to $BACKUP_FILE..."
        docker-compose exec -T postgres pg_dump -U appuser interest_social | gzip > "$BACKUP_FILE"
        log_success "Database backup created: $BACKUP_FILE"
    else
        log_warning "Database not running, skipping backup"
    fi
}

# Deploy services
deploy_services() {
    log_info "Deploying services for $ENVIRONMENT environment..."
    
    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose pull
    
    # Build images
    log_info "Building images..."
    docker-compose build --no-cache
    
    # Stop existing services gracefully
    log_info "Stopping existing services..."
    docker-compose down --timeout 30
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    local retries=0
    local max_retries=30
    
    while [[ $retries -lt $max_retries ]]; do
        if curl -fsS http://localhost:5000/health > /dev/null 2>&1; then
            log_success "API is healthy"
            break
        fi
        
        retries=$((retries + 1))
        log_info "Waiting for API to be healthy... ($retries/$max_retries)"
        sleep 5
    done
    
    if [[ $retries -eq $max_retries ]]; then
        log_error "API failed to become healthy within timeout"
        rollback
        exit 1
    fi
    
    log_success "Services deployed successfully"
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for database to be ready
    local retries=0
    local max_retries=10
    
    while [[ $retries -lt $max_retries ]]; do
        if docker-compose exec -T postgres pg_isready -U appuser > /dev/null 2>&1; then
            log_success "Database is ready"
            break
        fi
        
        retries=$((retries + 1))
        log_info "Waiting for database... ($retries/$max_retries)"
        sleep 3
    done
    
    # Run migrations
    if docker-compose exec -T api flask db upgrade; then
        log_success "Migrations completed successfully"
    else
        log_warning "No migrations to run or migration failed"
    fi
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check all services are running
    local failed_services
    failed_services=$(docker-compose ps | grep -c "Exit" || true)
    
    if [[ $failed_services -gt 0 ]]; then
        log_error "Some services failed to start"
        docker-compose ps
        rollback
        exit 1
    fi
    
    # Health check
    if curl -fsS http://localhost:5000/health > /dev/null 2>&1; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        rollback
        exit 1
    fi
    
    # Check SSL
    if curl -fsSk https://localhost/health > /dev/null 2>&1; then
        log_success "SSL is working"
    else
        log_warning "SSL check failed or not configured"
    fi
    
    log_success "Deployment verification complete"
}

# Rollback function
rollback() {
    log_error "Deployment failed! Initiating rollback..."
    
    # Find latest backup
    local latest_backup
    latest_backup=$(ls -t "$BACKUP_DIR"/pre-deploy-*.sql.gz 2>/dev/null | head -1)
    
    if [[ -n "$latest_backup" ]]; then
        log_info "Restoring from backup: $latest_backup"
        gunzip < "$latest_backup" | docker-compose exec -T postgres psql -U appuser -d interest_social
        log_success "Rollback complete"
    else
        log_warning "No backup found for rollback"
    fi
    
    # Restart with previous version
    log_info "Restarting services..."
    docker-compose restart
}

# Post-deployment tasks
post_deployment() {
    log_info "Running post-deployment tasks..."
    
    # Clean up old backups (keep last 7 days)
    find "$BACKUP_DIR" -name "pre-deploy-*.sql.gz" -mtime +7 -delete 2>/dev/null || true
    
    # Clean up old logs (keep last 30 days)
    find logs -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    # Prune unused Docker resources
    docker system prune -f > /dev/null 2>&1 || true
    
    log_success "Post-deployment tasks complete"
}

# Send notification (customize as needed)
send_notification() {
    local status=$1
    local message="Deployment to $ENVIRONMENT: $status"
    
    # Example: Send to Slack
    # curl -X POST -H 'Content-type: application/json' \
    #     --data "{\"text\":\"$message\"}" \
    #     "$SLACK_WEBHOOK_URL"
    
    log_info "Notification: $message"
}

# Main deployment flow
main() {
    log_info "Starting deployment to $ENVIRONMENT environment..."
    log_info "Log file: $LOG_FILE"
    
    # Create log directory
    mkdir -p logs
    
    # Run deployment steps
    pre_deployment_checks
    backup_before_deploy
    deploy_services
    run_migrations
    verify_deployment
    post_deployment
    
    log_success "Deployment to $ENVIRONMENT completed successfully!"
    send_notification "SUCCESS"
    
    # Display status
    echo ""
    log_info "Deployment Summary:"
    echo "=================="
    docker-compose ps
    echo ""
    log_info "API Health: $(curl -s http://localhost:5000/health | jq -r '.status' 2>/dev/null || echo 'Unknown')"
}

# Handle errors
trap 'log_error "Deployment script failed at line $LINENO"' ERR

# Run main function
main "$@"
