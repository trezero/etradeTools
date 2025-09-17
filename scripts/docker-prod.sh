#!/bin/bash
# Production Docker deployment script

set -e

echo "🚀 Deploying AI Trading Assistant to Production..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Validate production requirements
echo "🔍 Validating production requirements..."

# Check if config file exists
if [ ! -f "etrade_python_client/config.ini" ]; then
    echo "❌ config.ini not found. Please copy from template and configure."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs nginx/ssl

# Backup existing data if it exists
if [ -f "data/trading_assistant.db" ]; then
    echo "💾 Backing up existing database..."
    cp data/trading_assistant.db data/trading_assistant.db.backup.$(date +%Y%m%d_%H%M%S)
fi

# Build and deploy production environment
echo "🔨 Building and deploying production environment..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
if docker-compose -f docker-compose.prod.yml exec backend curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service health check failed"
    exit 1
fi

if docker-compose -f docker-compose.prod.yml exec frontend curl -f http://localhost:80/health > /dev/null 2>&1; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service health check failed"
    exit 1
fi

echo "🎉 Production deployment complete!"
echo "Frontend: http://localhost:80"
echo "Backend API: http://localhost:8000 (internal)"
echo ""
echo "📊 Monitor with:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo "  docker-compose -f docker-compose.prod.yml ps"