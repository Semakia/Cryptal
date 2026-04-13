#!/bin/bash
# Full Stack Startup Script for Crypto Viz
# Launches both backend API and frontend dashboard

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
API_DIR="$PROJECT_ROOT/src/api"
FRONTEND_DIR="$PROJECT_ROOT/crypto-dashboard"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Starting Crypto Viz Full Stack${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if API directory exists
if [ ! -d "$API_DIR" ]; then
    echo -e "${RED}❌ Error: API directory not found at $API_DIR${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Error: Frontend directory not found at $FRONTEND_DIR${NC}"
    exit 1
fi

# Check if .env exists for API
if [ ! -f "$PROJECT_ROOT/src/.env" ]; then
    echo -e "${RED}❌ Error: .env file not found at $PROJECT_ROOT/src/.env${NC}"
    echo "Please create the .env file with database credentials."
    exit 1
fi

# Check if .env.local exists for frontend
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    echo -e "${YELLOW}⚠ Warning: .env.local not found in frontend directory${NC}"
    echo -e "${YELLOW}Creating .env.local with default values...${NC}"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > "$FRONTEND_DIR/.env.local"
    echo -e "${GREEN}✓ Created .env.local${NC}"
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
echo -e "${BLUE}🔍 Checking ports...${NC}"

if check_port 8000; then
    echo -e "${YELLOW}⚠ Port 8000 is already in use (API)${NC}"
    echo -e "${YELLOW}The API might already be running, or you need to kill the process.${NC}"
    read -p "Kill the process on port 8000? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Killing process on port 8000...${NC}"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓ Port 8000 freed${NC}"
    else
        echo -e "${RED}Cannot start API on port 8000${NC}"
        exit 1
    fi
fi

if check_port 3000; then
    echo -e "${YELLOW}⚠ Port 3000 is already in use (Frontend)${NC}"
    read -p "Kill the process on port 3000? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Killing process on port 3000...${NC}"
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓ Port 3000 freed${NC}"
    else
        echo -e "${RED}Cannot start frontend on port 3000${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Ports are available${NC}"
echo ""

# Start API in background
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔧 Starting Backend API...${NC}"
echo -e "${BLUE}========================================${NC}"

cd "$API_DIR"

# Check if venv exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate"

# Install dependencies
echo -e "${YELLOW}Installing API dependencies...${NC}"
pip install -r requirements.txt --quiet

# Start API in background
echo -e "${GREEN}Starting API on http://localhost:8000${NC}"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/crypto-viz-api.log 2>&1 &
API_PID=$!

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ API failed to start${NC}"
        echo -e "${YELLOW}Check logs: tail -f /tmp/crypto-viz-api.log${NC}"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""

# Start Frontend
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🎨 Starting Frontend Dashboard...${NC}"
echo -e "${BLUE}========================================${NC}"

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    if command -v pnpm &> /dev/null; then
        pnpm install
    else
        npm install
    fi
fi

# Start frontend in background
echo -e "${GREEN}Starting frontend on http://localhost:3000${NC}"
if command -v pnpm &> /dev/null; then
    nohup pnpm dev > /tmp/crypto-viz-frontend.log 2>&1 &
else
    nohup npm run dev > /tmp/crypto-viz-frontend.log 2>&1 &
fi
FRONTEND_PID=$!

# Wait for frontend to be ready
echo -e "${YELLOW}Waiting for frontend to be ready...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready!${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ Frontend failed to start${NC}"
        echo -e "${YELLOW}Check logs: tail -f /tmp/crypto-viz-frontend.log${NC}"
        kill $API_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 Full Stack Started Successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Services Running:${NC}"
echo -e "  ${YELLOW}→${NC} Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "  ${YELLOW}→${NC} API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  ${YELLOW}→${NC} Frontend:     ${BLUE}http://localhost:3000${NC}"
echo ""
echo -e "${GREEN}Process IDs:${NC}"
echo -e "  API PID:      ${API_PID}"
echo -e "  Frontend PID: ${FRONTEND_PID}"
echo ""
echo -e "${GREEN}Logs:${NC}"
echo -e "  ${YELLOW}→${NC} API:      tail -f /tmp/crypto-viz-api.log"
echo -e "  ${YELLOW}→${NC} Frontend: tail -f /tmp/crypto-viz-frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create stop function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"

    # Kill API
    if kill -0 $API_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping API (PID: $API_PID)...${NC}"
        kill $API_PID 2>/dev/null || true
    fi

    # Kill Frontend
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping Frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    # Kill any remaining processes on ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Keep script running and tail logs
tail -f /tmp/crypto-viz-api.log /tmp/crypto-viz-frontend.log
