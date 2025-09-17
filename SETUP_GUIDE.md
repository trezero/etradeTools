# AI Trading Assistant - Complete Setup Guide

This comprehensive guide walks you through setting up the AI Trading Assistant with all available options and configurations.

## 🚀 Quick Setup (Recommended)

### One-Command Setup
```bash
./setup.sh
```

This interactive script will:
1. Check system requirements
2. Guide you through configuration
3. Set up all required services
4. Start the application

### Quick Start After Setup
```bash
./scripts/quick-start.sh
```

## 📋 Prerequisites

### Required
- **Python 3.10+**
- **Node.js 18+** with npm
- **Google Gemini API Key** - [Get here](https://makersuite.google.com/app/apikey)

### For Docker (Recommended)
- **Docker Desktop** - [Install here](https://docs.docker.com/get-docker/)
- **Docker Compose** (included with Docker Desktop)

### For Manual Setup
- **Redis Server** - [Install here](https://redis.io/download)

### Optional
- **E*TRADE Account** - [Sign up](https://us.etrade.com) (for live trading)
- **SMTP Credentials** - For email notifications
- **Slack Bot Token** - For Slack notifications

## 🛠️ Setup Options

### Option 1: Docker Setup (Easiest)

```bash
# Run interactive setup
./setup.sh

# Or direct Docker setup
./setup.sh --docker

# Quick commands after setup
./scripts/docker-dev.sh     # Development mode
./scripts/docker-prod.sh    # Production mode
```

**Advantages:**
- ✅ No manual dependency installation
- ✅ Isolated environment
- ✅ Consistent across systems
- ✅ Easy to start/stop/restart
- ✅ Includes all services

### Option 2: Manual Setup

```bash
# Run manual setup
./setup.sh --manual

# Or step by step
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cd frontend && npm install && cd ..
```

**Advantages:**
- ✅ Full control over environment
- ✅ Direct access to processes
- ✅ Easier debugging
- ✅ No Docker dependency

## ⚙️ Configuration Guide

### Required Configuration

#### 1. Google Gemini AI API Key
```ini
[AI_SERVICES]
GEMINI_API_KEY = your_actual_api_key_here
```
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Required for**: AI trading decisions and market analysis

#### 2. E*TRADE Configuration (Optional)
```ini
[DEFAULT]
CONSUMER_KEY = your_etrade_consumer_key
CONSUMER_SECRET = your_etrade_consumer_secret
```
- **Get Credentials**: https://developer.etrade.com/getting-started
- **Default**: Comes with sandbox credentials for testing
- **Production**: Replace with your real credentials for live trading

### Optional Configuration

#### Email Notifications
```ini
[NOTIFICATIONS]
smtp_username = your_email@gmail.com
smtp_password = your_app_password
smtp_host = smtp.gmail.com
smtp_port = 587
```
- **Gmail Setup**: Use App Password (not regular password)
- **Get App Password**: https://support.google.com/accounts/answer/185833

#### Slack Notifications
```ini
[NOTIFICATIONS]
slack_bot_token = xoxb-your-slack-bot-token
slack_channel = #trading-alerts
```
- **Setup Guide**: https://api.slack.com/apps

#### Advanced Settings
```ini
[WEB_APP]
HOST = 0.0.0.0
PORT = 8000
DEBUG = false

[DATABASE]
DATABASE_URL = sqlite:///./trading_assistant.db

[CELERY]
BROKER_URL = redis://localhost:6379/0
```

## 🏃‍♂️ Running the Application

### Method 1: Quick Start Script
```bash
./scripts/quick-start.sh
```
Interactive menu with all options.

### Method 2: Direct Commands

#### Docker
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production  
docker-compose -f docker-compose.prod.yml up -d

# Standard
docker-compose up -d
```

#### Manual
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
source venv/bin/activate
celery -A etrade_python_client.services.celery_app worker --loglevel=info

# Terminal 3: Celery Beat
source venv/bin/activate  
celery -A etrade_python_client.services.celery_app beat --loglevel=info

# Terminal 4: Backend
source venv/bin/activate
python run_server.py

# Terminal 5: Frontend
cd frontend && npm start
```

## 🔍 Validation & Troubleshooting

### Validate Configuration
```bash
./scripts/validate-config.sh
```

### Check System Status  
```bash
./scripts/quick-start.sh status
```

### View Logs
```bash
# Docker
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Manual
tail -f logs/trading_assistant.log
```

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using ports
lsof -i :3000,8000,6379

# Change ports in docker-compose.yml or config.ini
```

#### 2. Docker Issues
```bash
# Restart Docker
docker-compose down
docker-compose up -d

# Clean rebuild
docker-compose down
docker system prune -f
docker-compose up --build -d
```

#### 3. Redis Connection
```bash
# Test Redis
redis-cli ping

# Docker Redis
docker-compose exec redis redis-cli ping
```

#### 4. Permission Errors
```bash
# Fix permissions
sudo chown -R $USER:$USER data/ logs/
chmod +x scripts/*.sh
```

## 📊 Access Points

Once running, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main web interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Service health status |

## 🎯 Initial Usage

### First Steps
1. **Open Web Interface**: http://localhost:3000
2. **Connect E*TRADE**: Click "Connect E*TRADE" (optional)
3. **Complete OAuth**: Follow E*TRADE authentication flow
4. **Configure Preferences**: Set risk tolerance and trading preferences
5. **Add Watchlist**: Add symbols to monitor
6. **Start Trading**: Use AI recommendations or manual trading

### Key Features
- **Portfolio Dashboard**: Real-time portfolio performance
- **AI Decisions**: AI-powered trading recommendations  
- **Market Data**: Live quotes and charts
- **Trading Interface**: Execute trades directly
- **Notifications**: Email/Slack alerts
- **Analytics**: Performance tracking and analysis

## 🔧 Development & Customization

### Project Structure
```
├── etrade_python_client/     # Backend Python code
├── frontend/                 # React frontend  
├── scripts/                  # Setup and utility scripts
├── data/                     # Database and data files
├── logs/                     # Application logs
├── docker-compose*.yml       # Docker configurations
└── README*.md               # Documentation
```

### Adding Features
1. **Backend**: Modify `etrade_python_client/web/main.py`
2. **Frontend**: Add components in `frontend/src/components/`
3. **Database**: Update models in `etrade_python_client/database/models.py`
4. **Services**: Add business logic in `etrade_python_client/services/`

### Testing
```bash
# Backend tests
pytest

# Frontend tests  
cd frontend && npm test

# Code quality
flake8 etrade_python_client
black etrade_python_client
```

## 📚 Documentation

- **Main README**: [README.md](README.md) - Complete project overview
- **Docker Guide**: [README.Docker.md](README.Docker.md) - Docker-specific documentation
- **API Documentation**: http://localhost:8000/docs (when running)
- **Setup Guide**: This file - Comprehensive setup instructions

## 🆘 Getting Help

### Scripts Reference
```bash
./setup.sh                    # Main setup wizard
./setup.sh --docker          # Docker setup only  
./setup.sh --manual          # Manual setup only
./scripts/quick-start.sh      # Interactive start menu
./scripts/validate-config.sh  # Validate configuration
./scripts/docker-dev.sh       # Start development environment
./scripts/docker-prod.sh      # Start production environment
```

### Support Resources
- **Issues**: GitHub Issues for bug reports
- **Documentation**: README files in project
- **Logs**: Check application logs for errors
- **Health Check**: http://localhost:8000/health

## ⚠️ Important Notes

### Security
- **Never commit real API keys** to version control
- **Use sandbox mode** for testing before live trading
- **Review all trades** before execution
- **Monitor logs** for security issues

### Trading Safety
- **Start small** with test amounts
- **Understand risks** of automated trading
- **Monitor performance** regularly
- **Have stop-loss strategies** in place

### Data & Privacy
- **Local storage** - All data stays on your machine
- **No data sharing** - Application doesn't send data externally
- **Backup important data** regularly
- **Secure your API keys** appropriately

---

**🎉 You're ready to start trading with AI assistance!**

For additional help, see the main [README.md](README.md) or [README.Docker.md](README.Docker.md).