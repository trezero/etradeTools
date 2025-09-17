#!/bin/bash
# Development Docker setup script

set -e

echo "🐳 Setting up AI Trading Assistant for Development..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if config file exists
if [ ! -f "etrade_python_client/config.ini" ]; then
    echo "📝 Creating config.ini from template..."
    cp etrade_python_client/config.ini.template etrade_python_client/config.ini
    echo "⚠️  Please edit etrade_python_client/config.ini with your settings before continuing."
    echo "Press Enter when ready..."
    read
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs

# Build and start development environment
echo "🔨 Building and starting development environment..."
docker-compose -f docker-compose.dev.yml down --remove-orphans
docker-compose -f docker-compose.dev.yml up --build

echo "✅ Development environment started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"