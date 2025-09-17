# AI Trading Assistant with E*TRADE Integration

[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue)](README.Docker.md)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)](https://fastapi.tiangolo.com)

An AI-powered trading assistant that integrates with the E*TRADE API to provide real-time market data, portfolio analytics, and automated trading capabilities powered by Google Gemini AI.

## 🚀 Quick Start

Choose your preferred setup method:

### Option 1: Docker Setup (Recommended)
```bash
# Run the interactive setup script
./setup.sh

# Or start directly with Docker
./scripts/docker-dev.sh
```

### Option 2: Manual Setup
```bash
# Run the comprehensive setup script
./setup.sh --manual
```

## 📑 Table of Contents

* [Features](#-features)
* [Architecture](#-architecture)
* [Requirements](#-requirements)
* [Installation](#-installation)
  * [Docker Setup (Recommended)](#docker-setup-recommended)
  * [Manual Setup](#manual-setup)
* [Configuration](#-configuration)
* [Running the Application](#-running-the-application)
* [Usage](#-usage)
* [E*TRADE Integration](#-etrade-integration)
* [API Documentation](#-api-documentation)
* [Development](#-development)
* [Troubleshooting](#-troubleshooting)

## ✨ Features

### Core Trading Features
- 🤖 **AI-Powered Trading Decisions** - Google Gemini AI analyzes market conditions
- 📈 **Real-time Market Data** - Yahoo Finance integration for live quotes and historical data
- 💰 **E*TRADE API Integration** - Secure account management and trade execution
- 📊 **Portfolio Analytics** - Real-time tracking with advanced performance metrics
- 🎯 **Automated Trading** - AI-driven trade execution with configurable confidence thresholds

### Intelligence & Analysis
- 📰 **Market Sentiment Analysis** - News-based sentiment scoring with AI analysis
- 🔍 **Technical Indicators** - Comprehensive technical analysis tools
- 📱 **Real-time Updates** - WebSocket-based live market data and portfolio changes
- 🎛️ **Risk Management** - Configurable risk tolerance and position sizing

### User Experience
- 🖥️ **Modern Web Interface** - React frontend with Material-UI components
- 🔔 **Multi-channel Notifications** - Email and Slack alerts for trading activities
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- 🎨 **Interactive Dashboards** - Real-time charts and portfolio visualizations

### Infrastructure
- 🐳 **Docker Support** - Complete containerized deployment
- ⚡ **High Performance** - Redis caching and Celery background tasks
- 🔒 **Security** - OAuth authentication and secure API integration
- 📦 **Microservices Architecture** - Scalable and maintainable design

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   E*TRADE API   │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         └──────────────►│   (Cache &      │◄─────────────┘
                        │   Message Broker)│
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  Celery Workers │
                        │  (Background    │
                        │   Tasks)        │
                        └─────────────────┘
```

### Component Overview
1. **React Frontend** - TypeScript-based UI with Material-UI
2. **FastAPI Backend** - Python REST API with WebSocket support
3. **Redis** - Message broker for Celery and caching layer
4. **Celery Workers** - Background processing for portfolio sync and AI analysis
5. **SQLite Database** - Local storage for analytics and trading history
6. **External APIs** - E*TRADE, Yahoo Finance, Google Gemini

## 📋 Requirements

### System Requirements
- **Python 3.10+**
- **Node.js 18+** with npm
- **Redis Server** (or Docker)
- **4GB+ RAM** (8GB+ recommended)
- **10GB+ disk space**

### Account Requirements
1. **E*TRADE Account** - [Sign up here](https://us.etrade.com) (sandbox for testing)
2. **Google Gemini API Key** - [Get API key](https://makersuite.google.com/app/apikey)
3. **Optional**: SMTP credentials for email notifications
4. **Optional**: Slack bot token for Slack notifications

## 🛠️ Installation

### Docker Setup (Recommended)

Docker provides the easiest and most reliable setup experience:

```bash
# Clone the repository
git clone <repository-url>
cd EtradePythonClient

# Run the interactive setup script
./setup.sh

# The script will guide you through:
# 1. Docker installation check
# 2. Configuration file creation
# 3. API key setup
# 4. Service startup
```

**Quick Docker Commands:**
```bash
# Development environment
./scripts/docker-dev.sh

# Production environment  
./scripts/docker-prod.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

For detailed Docker documentation, see [README.Docker.md](README.Docker.md).

### Manual Setup

If you prefer to run services manually:

```bash
# Run the setup script with manual flag
./setup.sh --manual

# Or follow these steps:

# 1. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 2. Install Python dependencies
pip install -r requirements-dev.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure the application
cp etrade_python_client/config.ini.template etrade_python_client/config.ini
# Edit config.ini with your settings

# 5. Start Redis server
redis-server

# 6. Start backend services (in separate terminals)
celery -A etrade_python_client.services.celery_app worker --loglevel=info
celery -A etrade_python_client.services.celery_app beat --loglevel=info
python run_server.py

# 7. Start frontend
cd frontend && npm start
```

## ⚙️ Configuration

The setup script (`./setup.sh`) will guide you through all configuration options, or you can configure manually:

### Required Configuration

#### 1. Google Gemini AI API Key
```ini
[AI_SERVICES]
GEMINI_API_KEY = your_actual_gemini_api_key_here
```

#### 2. E*TRADE API Credentials
For production trading, replace sandbox credentials in `config.ini`:
```ini
[DEFAULT]
ETRADE_CONSUMER_KEY = your_etrade_consumer_key
ETRADE_CONSUMER_SECRET = your_etrade_consumer_secret
BASE_URL = https://api.etrade.com  # Production URL
```

### Optional Configuration

#### Email Notifications
```ini
[NOTIFICATIONS]
smtp_username = your_email@gmail.com
smtp_password = your_app_password
smtp_host = smtp.gmail.com
smtp_port = 587
```

#### Slack Notifications  
```ini
[NOTIFICATIONS]
slack_bot_token = xoxb-your-slack-bot-token
slack_channel = #trading-alerts
```

#### Advanced Settings
```ini
[WEB_APP]
HOST = 0.0.0.0
PORT = 8000
DEBUG = false

[CELERY]
BROKER_URL = redis://localhost:6379/0
RESULT_BACKEND = redis://localhost:6379/0
```

## 🚀 Running the Application

### With Docker (Recommended)
```bash
# Development environment with hot reloading
./scripts/docker-dev.sh

# Production environment
./scripts/docker-prod.sh
```

### Manual Startup
```bash
# 1. Start Redis
redis-server

# 2. Start Celery worker (new terminal)
celery -A etrade_python_client.services.celery_app worker --loglevel=info

# 3. Start Celery beat (new terminal)
celery -A etrade_python_client.services.celery_app beat --loglevel=info

# 4. Start backend (new terminal)
python run_server.py

# 5. Start frontend (new terminal)
cd frontend && npm start
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📱 Usage

### Initial Setup

1. **Open the Web Interface**: Navigate to http://localhost:3000
2. **Connect E*TRADE Account**:
   - Click "Connect E*TRADE" in the account widget
   - Complete OAuth authentication in the popup window
   - Enter the verification code provided by E*TRADE
3. **Configure Trading Preferences**:
   - Set risk tolerance levels
   - Configure notification preferences
   - Add watchlist symbols

### AI Trading Workflow

1. **Market Analysis**: The AI continuously analyzes market conditions
2. **Decision Generation**: Trading recommendations appear in the AI Decisions widget
3. **Review & Feedback**: Evaluate AI decisions and provide feedback to improve performance
4. **Execution**: Configure auto-trading or execute trades manually

### Manual Trading

1. **Order Placement**: Use the E*TRADE Trading widget
2. **Order Preview**: Review estimated costs and market impact
3. **Execution**: Confirm and execute trades
4. **Monitoring**: Track order status and portfolio updates

### Portfolio Management

- **Real-time Monitoring**: Dashboard shows live portfolio performance
- **Analytics**: Historical charts and performance metrics
- **Risk Assessment**: Portfolio risk scores and diversification analysis
- **Notifications**: Alerts for significant portfolio changes

## 🔗 E*TRADE Integration

### Authentication
- **OAuth 1.0a Flow**: Secure authentication with E*TRADE
- **Sandbox Support**: Test with paper trading before live deployment
- **Session Management**: Automatic token refresh and error handling

### Account Management
- **Multi-Account Support**: Manage multiple E*TRADE accounts
- **Balance Tracking**: Real-time account balances and buying power
- **Position Management**: Detailed portfolio positions and performance

### Trading Capabilities
- **Order Types**: Market, limit, stop, and stop-limit orders
- **Order Management**: Preview, place, modify, and cancel orders
- **Trade History**: Complete trade execution history and performance

### Data Synchronization
- **Automatic Updates**: Periodic portfolio data synchronization
- **Real-time Events**: WebSocket updates for order status changes
- **Analytics Integration**: Local storage for advanced analytics

## 📚 API Documentation

Complete interactive API documentation is available at http://localhost:8000/docs when the backend is running.

### Key API Categories

#### Market Data APIs
- `GET /api/market/overview` - Major market indices
- `GET /api/market/quote/{symbol}` - Real-time quotes
- `GET /api/market/historical/{symbol}` - Historical data
- `GET /api/market/news/{symbol}` - News headlines

#### Portfolio APIs
- `GET /api/portfolio/latest` - Latest portfolio analytics
- `GET /api/portfolio/history` - Historical performance
- `POST /api/ai/analyze/{symbol}` - Trigger AI analysis

#### E*TRADE APIs
- `GET /api/etrade/accounts` - Account list
- `GET /api/etrade/accounts/{id}/balance` - Account balance
- `POST /api/etrade/accounts/{id}/orders/preview` - Order preview
- `POST /api/etrade/accounts/{id}/orders/place` - Place order

#### AI & Analytics APIs
- `GET /api/decisions` - AI trading decisions
- `POST /api/decisions/{id}/feedback` - Decision feedback
- `GET /api/sentiment` - Market sentiment analysis

## 🛠️ Development

### Project Structure
```
├── etrade_python_client/          # Backend Python code
│   ├── web/                       # FastAPI application
│   ├── services/                  # Business logic & integrations
│   ├── database/                  # Database models & migrations
│   └── utils/                     # Utilities & configuration
├── frontend/                      # React frontend
│   ├── src/components/            # React components
│   ├── src/services/             # API service layer
│   └── src/types/                # TypeScript definitions
├── scripts/                       # Setup and deployment scripts
├── docs/                         # Documentation
└── docker-compose*.yml          # Docker configurations
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt
cd frontend && npm install && cd ..

# Run tests
pytest                            # Backend tests
cd frontend && npm test && cd ..  # Frontend tests

# Code quality
flake8 etrade_python_client      # Python linting
black etrade_python_client       # Python formatting
cd frontend && npm run lint && cd .. # Frontend linting
```

### Adding New Features

1. **Backend**: Add endpoints in `etrade_python_client/web/main.py`
2. **Frontend**: Create components in `frontend/src/components/`
3. **Database**: Add models in `etrade_python_client/database/models.py`
4. **Services**: Add business logic in `etrade_python_client/services/`

## 🔧 Troubleshooting

### Common Issues

#### E*TRADE Authentication
```bash
# Check authentication status
curl http://localhost:8000/api/etrade/auth/status

# Common solutions:
# 1. Verify consumer key/secret in config.ini
# 2. Ensure sandbox mode for testing
# 3. Check E*TRADE account API permissions
```

#### Docker Issues
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

#### Redis Connection
```bash
# Test Redis connectivity
redis-cli ping

# Check Docker Redis
docker-compose exec redis redis-cli ping
```

#### Port Conflicts
```bash
# Check what's using ports
lsof -i :3000,8000,6379

# Change ports in docker-compose.yml if needed
```

### Performance Optimization

#### Backend Performance
- **Celery Workers**: Scale workers based on CPU cores
- **Redis Configuration**: Tune Redis memory settings
- **Database**: Regular SQLite database optimization

#### Frontend Performance
- **Bundle Size**: Monitor bundle size with `npm run build`
- **Caching**: Configure nginx caching for static assets
- **API Calls**: Implement request debouncing for real-time data

### Monitoring

#### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health (Docker)
curl http://localhost:3000/health

# Service status
docker-compose ps
```

#### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Backend only (manual setup)
tail -f logs/trading_assistant.log
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint for TypeScript
- **Testing**: Add tests for new features
- **Documentation**: Update README and API docs
- **Security**: Never commit API keys or secrets

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **E*TRADE** for providing comprehensive trading APIs
- **Google** for the Gemini AI platform
- **Yahoo Finance** for reliable market data
- **Open Source Community** for the amazing tools and libraries

## 📞 Support

- **Documentation**: [README.Docker.md](README.Docker.md) for Docker setup
- **Issues**: GitHub Issues for bug reports and feature requests
- **API Docs**: http://localhost:8000/docs when running

---

**⭐ Star this repository if it helps with your trading journey!**