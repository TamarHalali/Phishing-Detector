#!/bin/bash

# Phishing Detector EC2 Deployment Script
# This script pulls latest Docker images and deploys the application

set -e  # Exit on any error

LOG_FILE="/home/ec2-user/deploy.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "🚀 Starting deployment at $(date)"
echo "==========================================="

# Configuration
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-yourusername}"  # Will be passed as env var
EC2_HOST="${EC2_HOST:-localhost}"

# Environment variables (should be set in EC2 environment)
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"
GEMINI_API_KEY="${GEMINI_API_KEY}"
VIRUSTOTAL_API_KEY="${VIRUSTOTAL_API_KEY}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if image exists locally
image_exists() {
    local image=$1
    docker image inspect "$image" >/dev/null 2>&1
}

# Function to pull image with error handling
pull_image() {
    local image=$1
    local name=$2

    if image_exists "$image"; then
        log_info "$name image already exists locally - skipping pull"
        return 0
    fi

    log_info "Pulling $name image..."
    if docker pull "$image"; then
        log_info "$name image pulled successfully"
        return 0
    else
        log_error "Failed to pull $name image"
        return 1
    fi
}

# Emergency cleanup function
emergency_cleanup() {
    log_warn "Performing emergency cleanup..."

    # Stop all containers
    docker stop $(docker ps -aq 2>/dev/null) 2>/dev/null || true

    # Remove all containers
    docker rm -f $(docker ps -aq 2>/dev/null) 2>/dev/null || true

    # Quick cleanup
    docker system prune -f 2>/dev/null || true

    log_info "Emergency cleanup completed"
}

# Main deployment function
main() {
    log_info "Checking Docker availability..."
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running or not accessible"
        exit 1
    fi
    log_info "Docker is available"

    # Emergency cleanup at start
    emergency_cleanup

    # Pull Docker images
    log_info "Pulling latest Docker images..."

    # MySQL (largest first)
    if ! pull_image "mysql:8.0.35" "MySQL"; then
        log_error "Failed to pull MySQL image"
        exit 1
    fi

    # Application images in parallel
    log_info "Pulling application images..."

    pull_image "${DOCKERHUB_USERNAME}/phishing-detector-backend:latest" "Backend" &
    BACKEND_PID=$!

    pull_image "${DOCKERHUB_USERNAME}/phishing-detector-frontend:latest" "Frontend" &
    FRONTEND_PID=$!

    pull_image "${DOCKERHUB_USERNAME}/phishing-detector-nginx:latest" "Nginx" &
    NGINX_PID=$!

    # Wait for all pulls to complete
    BACKEND_OK=0
    FRONTEND_OK=0
    NGINX_OK=0

    if wait $BACKEND_PID 2>/dev/null; then BACKEND_OK=1; fi
    if wait $FRONTEND_PID 2>/dev/null; then FRONTEND_OK=1; fi
    if wait $NGINX_PID 2>/dev/null; then NGINX_OK=1; fi

    if [ $BACKEND_OK -eq 0 ] || [ $FRONTEND_OK -eq 0 ] || [ $NGINX_OK -eq 0 ]; then
        log_error "Some images failed to pull"
        exit 1
    fi

    log_info "All images pulled successfully"

    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f /home/ec2-user/docker-compose.prod.yml down 2>/dev/null || true

    # Start new containers
    log_info "Starting new containers..."
    if docker-compose -f /home/ec2-user/docker-compose.prod.yml up -d; then
        log_info "Containers started successfully"
    else
        log_error "Failed to start containers"
        exit 1
    fi

    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30

    # Health checks
    log_info "Performing health checks..."

    # MySQL health check
    MAX_RETRIES=10
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if docker-compose -f /home/ec2-user/docker-compose.prod.yml exec -T mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
            log_info "MySQL is healthy"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            log_warn "MySQL not ready yet ($RETRY_COUNT/$MAX_RETRIES)"
            sleep 5
        fi
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_error "MySQL health check failed"
    fi

    # Final status
    log_info "Deployment completed successfully"
    log_info "Container status:"
    docker-compose -f /home/ec2-user/docker-compose.prod.yml ps || docker ps

    echo ""
    log_info "🎉 Deployment finished at $(date)"
    echo "==========================================="
}

# Run main function
main "$@"
