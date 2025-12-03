# 🐳 Docker Deployment Guide

## Quick Start

### 1. Build and Run with Docker Compose
```bash
cd phishing_detector
docker-compose up --build
```

### 2. Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000

## Configuration

### Environment Variables (Optional)
Create `.env` file in root directory:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### API Keys
- **GEMINI_API_KEY**: Google Gemini API key
- **OPENAI_API_KEY**: OpenAI API key  
- **VIRUSTOTAL_API_KEY**: VirusTotal API key

*Without API keys, the app runs in demo mode with mock data.*

## Docker Commands

### Build Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Run Services
```bash
# Run in background
docker-compose up -d

# Run with logs
docker-compose up

# Stop services
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

### Development Mode
```bash
# Run with volume mounts for development
docker-compose -f docker-compose.yml up
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   NGINX         │    │   Flask API      │
│   (Frontend)    │◄──►│   (Backend)      │
│   Port 80       │    │   Port 5000      │
└─────────────────┘    └──────────────────┘
```

## Troubleshooting

### Port Conflicts
If port 80 is in use:
```bash
# Change frontend port in docker-compose.yml
ports:
  - "8080:80"  # Use port 8080 instead
```

### Backend Connection Issues
Check backend health:
```bash
curl http://localhost:5000/health
```

### View Container Status
```bash
docker-compose ps
```

## Production Deployment

### Security Considerations
1. Change default ports
2. Add SSL/TLS certificates
3. Set proper environment variables
4. Use secrets management
5. Enable firewall rules

### Scaling
```bash
# Scale backend instances
docker-compose up --scale backend=3
```