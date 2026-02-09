#!/bin/bash
# EC2 Initial Setup Script for Phishing Detector
# Run this script once when setting up a new EC2 instance

set -e

echo "🚀 Starting EC2 Setup for Phishing Detector..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
echo "✅ Verifying installations..."
docker --version
docker-compose --version

# Create project directory
echo "📁 Creating project directory..."
mkdir -p ~/phishing-detector
cd ~/phishing-detector

# Create .env file template
echo "📝 Creating .env file template..."
cat > .env << 'EOF'
# MySQL Configuration
MYSQL_ROOT_PASSWORD=your_root_password_here
MYSQL_PASSWORD=your_password_here

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
EOF

echo ""
echo "✅ EC2 Setup Complete!"
echo ""
echo "⚠️  IMPORTANT: Next steps:"
echo "1. Edit ~/phishing-detector/.env with your actual credentials"
echo "2. Log out and log back in for Docker group changes to take effect"
echo "3. Run the deploy.sh script to start the application"
echo ""
echo "Commands:"
echo "  nano ~/phishing-detector/.env    # Edit environment variables"
echo "  exit                              # Log out"
echo "  ssh back in                       # Log back in"
echo "  cd ~/phishing-detector && ./deploy.sh  # Deploy application"
