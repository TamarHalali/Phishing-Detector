#!/bin/bash
# SSH Setup Script for GitHub Actions
# Sets up SSH connection to EC2

set -e

echo "🔑 Setting up SSH..."
mkdir -p ~/.ssh
echo "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
chmod 600 ~/.ssh/deploy_key
ssh-keyscan -H $EC2_HOST >> ~/.ssh/known_hosts 2>/dev/null

echo "✅ SSH setup completed"
