#!/bin/bash

# CrypTal - Docker Launch Script
# This script starts the entire stack with Docker Compose

set -e

echo ""
echo "========================================"
echo "🚀 CrypTal - Docker Stack Startup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is running"

# Navigate to docker-compose directory
cd .config/iac/dev

echo ""
echo "🐳 Starting Docker containers..."
echo ""

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down

# Start all services
echo ""
echo "Starting services:"
echo "  - Zookeeper"
echo "  - Kafka"
echo "  - Producer (Kafka → CoinGecko)"
echo "  - Consumer (Kafka → Neon DB)"
echo "  - API Backend (FastAPI)"
echo "  - Frontend Dashboard (Next.js)"
echo ""
echo "ℹ️  Using Neon DB (cloud) - no local Postgres needed"
echo ""

docker-compose up -d

echo ""
echo -e "${GREEN}✓${NC} All containers started!"
echo ""

# Wait a few seconds for services to initialize
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "========================================"
echo "✅ CrypTal is ready!"
echo "========================================"
echo ""
echo "📊 Available services:"
echo ""
echo "  🎨 Dashboard:         http://localhost:3000"
echo "  🌐 API Backend:       http://localhost:8000"
echo "  📚 API Docs:          http://localhost:8000/docs"
echo "  ❤️  Health Check:      http://localhost:8000/health"
echo "  🗄️  Database:          Neon DB (cloud)"
echo ""
echo "🔍 View logs:"
echo "  docker-compose logs -f                    # All services"
echo "  docker-compose logs -f frontend           # Frontend only"
echo "  docker-compose logs -f api                # API only"
echo "  docker-compose logs -f kafka-producer     # Producer only"
echo "  docker-compose logs -f kafka-consumer     # Consumer only"
echo ""
echo "🛑 Stop all services:"
echo "  docker-compose down"
echo ""
echo "📋 Check status:"
echo "  docker-compose ps"
echo ""
echo "========================================"
echo ""
echo -e "${YELLOW}💡 Tip:${NC} Wait 1-2 minutes for data to populate"
echo -e "${YELLOW}💡 Tip:${NC} Check logs if you see errors: docker-compose logs"
echo ""
echo "🎉 Happy analyzing!"
echo ""
