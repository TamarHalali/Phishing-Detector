#!/bin/bash
# Deployment Script for Phishing Detector on EC2
# Run this script to deploy or update the application

set -e

echo "🚀 Starting Phishing Detector Deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with required variables"
    exit 1
fi

# Verify required environment variables
REQUIRED_VARS=("MYSQL_ROOT_PASSWORD" "MYSQL_PASSWORD" "GEMINI_API_KEY" "VIRUSTOTAL_API_KEY")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set in .env file"
        exit 1
    fi
done

echo "✅ All required environment variables are set"

# Set Docker Hub username (change if needed)
DOCKER_USERNAME="tamarhalali"

# Get latest version or use 'latest' tag
VERSION="${1:-latest}"

echo "📥 Pulling Docker images (version: $VERSION)..."
docker pull mysql:8.0.35
docker pull ${DOCKER_USERNAME}/phishing-detector-backend:${VERSION}
docker pull ${DOCKER_USERNAME}/phishing-detector-frontend:${VERSION}
docker pull ${DOCKER_USERNAME}/phishing-detector-nginx:${VERSION}

echo "🧹 Stopping existing containers..."
docker-compose down 2>/dev/null || true

echo "🗑️  Cleaning up old containers and images..."
docker container prune -f
docker image prune -f

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🌐 Application should be available at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "📝 Useful commands:"
echo "   docker-compose logs -f           # View logs"
echo "   docker-compose ps                # Check status"
echo "   docker-compose restart           # Restart services"
echo "   docker-compose down              # Stop services"
