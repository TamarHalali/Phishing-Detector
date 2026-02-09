#!/bin/bash
# EC2 Deployment Script for GitHub Actions
# This script runs on EC2 via SSH to deploy the application

set -e

echo "📋 Updating .env file..."
cat > ~/phishing-detector/.env << EOF
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_PASSWORD=${MYSQL_PASSWORD}
GEMINI_API_KEY=${GEMINI_API_KEY}
VIRUSTOTAL_API_KEY=${VIRUSTOTAL_API_KEY}
EOF

echo "🐳 Pulling latest images..."
cd ~/phishing-detector
docker pull mysql:8.0.35 &
docker pull ${DOCKERHUB_USERNAME}/phishing-detector-backend:latest &
docker pull ${DOCKERHUB_USERNAME}/phishing-detector-frontend:latest &
docker pull ${DOCKERHUB_USERNAME}/phishing-detector-nginx:latest &
wait

echo "🔄 Restarting services..."
docker-compose down || true
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 20

echo "🔍 Checking status..."
docker-compose ps

echo "✅ Deployment completed!"
