# Docker Setup for AI Trading Assistant

This guide explains how to run the AI Trading Assistant using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- 4GB+ available RAM
- 10GB+ available disk space

## Quick Start

### Development Environment

```bash
# Clone and navigate to project
cd EtradePythonClient

# Copy configuration template
cp etrade_python_client/config.ini.template etrade_python_client/config.ini

# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Redis: localhost:6379
```

### Production Environment

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d --build

# Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:8000 (internal)
```

## Architecture Overview

The application consists of 5 main services:

1. **Redis** - Message broker for Celery tasks
2. **Backend** - FastAPI Python application
3. **Celery Worker** - Background task processing
4. **Celery Beat** - Scheduled task scheduler
5. **Frontend** - React web application with nginx

## Environment Configurations

### Development (docker-compose.dev.yml)
- Hot reloading enabled
- Debug logging
- Direct port exposure
- Volume mounting for live code changes

### Production (docker-compose.prod.yml)
- Optimized builds
- Resource limits
- Nginx reverse proxy
- Health checks and logging
- No debug information

### Standard (docker-compose.yml)
- Balanced configuration
- Suitable for staging/testing
- Health checks enabled
- Persistent data volumes

## Configuration

### Required Configuration Files

1. **etrade_python_client/config.ini** - Main application config
   ```ini
   [GENERAL]
   DEBUG = false
   LOG_LEVEL = INFO
   
   [WEB_APP]
   HOST = 0.0.0.0
   PORT = 8000
   
   [REDIS]
   URL = redis://redis:6379/0
   
   [DATABASE]
   URL = sqlite:///data/trading_assistant.db
   ```

2. **Environment Variables** (optional .env file)
   ```env
   REDIS_URL=redis://redis:6379/0
   DATABASE_URL=sqlite:///data/trading_assistant.db
   ENVIRONMENT=production
   ```

### Optional: SSL Configuration (Production)

Create SSL certificates in `nginx/ssl/`:
```bash
mkdir -p nginx/ssl
# Add your SSL certificates
# nginx/ssl/cert.pem
# nginx/ssl/key.pem
```

## Service Details

### Backend Service
- **Image**: Custom Python 3.10 with FastAPI
- **Ports**: 8000 (API)
- **Health Check**: GET /health
- **Dependencies**: redis
- **Volumes**: 
  - `./data:/app/data` (SQLite database)
  - `./logs:/app/logs` (Application logs)
  - `./etrade_python_client/config.ini:/app/etrade_python_client/config.ini:ro`

### Frontend Service
- **Image**: Multi-stage Node.js + nginx
- **Ports**: 3000 (dev), 80 (prod)
- **Health Check**: GET /health
- **Features**: 
  - API proxy to backend
  - WebSocket proxy support
  - Static asset optimization
  - React Router support

### Redis Service
- **Image**: redis:7-alpine
- **Ports**: 6379
- **Health Check**: redis-cli ping
- **Persistence**: AOF + RDB snapshots
- **Volume**: `redis_data:/data`

### Celery Services
- **Worker**: Processes background tasks
- **Beat**: Scheduled task execution
- **Dependencies**: redis, backend
- **Command Examples**:
  ```bash
  # Worker
  celery -A etrade_python_client.services.celery_app worker --loglevel=info
  
  # Beat Scheduler
  celery -A etrade_python_client.services.celery_app beat --loglevel=info
  ```

## Docker Commands

### Basic Operations
```bash
# Build all services
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Stop all services
docker-compose down

# Remove volumes (CAUTION: deletes data)
docker-compose down -v
```

### Development Commands
```bash
# Development with hot reloading
docker-compose -f docker-compose.dev.yml up

# Frontend development only
docker-compose -f docker-compose.dev.yml up frontend_dev

# Backend development only
docker-compose -f docker-compose.dev.yml up backend redis celery_worker
```

### Production Commands
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d --build

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3

# Update specific service
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
```

### Debugging Commands
```bash
# Execute commands in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# View container resource usage
docker stats

# Inspect container details
docker-compose ps
docker inspect etrade_backend

# View health check status
docker-compose exec backend curl -f http://localhost:8000/health
```

## Data Persistence

### Volumes
- **redis_data**: Redis data persistence
- **./data**: SQLite database and application data
- **./logs**: Application logs

### Backup Strategy
```bash
# Backup database
docker-compose exec backend cp /app/data/trading_assistant.db /app/data/backup_$(date +%Y%m%d_%H%M%S).db

# Backup entire data directory
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/
```

## Monitoring and Health Checks

### Health Endpoints
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000/health` (dev), `http://localhost:80/health` (prod)
- Redis: Built-in redis-cli ping

### Log Monitoring
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# With timestamps
docker-compose logs -f -t backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Resource Monitoring
```bash
# Container stats
docker stats

# Service resource usage
docker-compose top
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using the port
   lsof -i :8000
   netstat -tulpn | grep :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # host:container
   ```

2. **Permission Errors**
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER data/
   sudo chown -R $USER:$USER logs/
   ```

3. **Database Errors**
   ```bash
   # Reset database
   docker-compose down
   rm -rf data/trading_assistant.db*
   docker-compose up
   ```

4. **Redis Connection Issues**
   ```bash
   # Check Redis connectivity
   docker-compose exec backend python -c "import redis; r=redis.Redis(host='redis', port=6379); print(r.ping())"
   ```

5. **Build Failures**
   ```bash
   # Clean build
   docker-compose down
   docker system prune -f
   docker-compose build --no-cache
   ```

### Service Dependencies

```
Redis (start first)
  ↓
Backend API (depends on Redis)
  ↓
Celery Worker & Beat (depend on Backend + Redis)
  ↓
Frontend (depends on Backend)
```

### Performance Tuning

1. **Production Resources** (docker-compose.prod.yml)
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 512M
       reservations:
         cpus: '0.25'
         memory: 256M
   ```

2. **Celery Workers**
   ```bash
   # Scale workers based on CPU cores
   docker-compose up -d --scale celery_worker=4
   ```

3. **Redis Optimization**
   ```bash
   # Monitor Redis performance
   docker-compose exec redis redis-cli info memory
   docker-compose exec redis redis-cli info stats
   ```

## Security Considerations

1. **Production Secrets**
   - Use environment variables for sensitive data
   - Don't commit config.ini with real API keys
   - Use Docker secrets for production

2. **Network Security**
   - Services communicate via internal Docker network
   - Only necessary ports exposed to host
   - Consider using nginx for SSL termination

3. **File Permissions**
   - Non-root user in containers
   - Proper volume permissions
   - Read-only configuration mounts

## Next Steps

1. Set up SSL certificates for production
2. Configure monitoring (Prometheus/Grafana)
3. Set up automated backups
4. Configure log aggregation
5. Implement CI/CD pipeline

For more information, see the main project README.md.