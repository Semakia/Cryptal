#!/bin/bash
# Startup script for Crypto Viz API
# Usage: ./scripts/start_api.sh

set -e

echo "=========================================="
echo "🚀 Starting Crypto Viz API"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
API_DIR="$PROJECT_ROOT/src/api"

# Check if .env exists
if [ ! -f "$PROJECT_ROOT/src/.env" ]; then
    echo -e "${RED}❌ Error: .env file not found at $PROJECT_ROOT/src/.env${NC}"
    echo "Please create the .env file with database credentials."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found .env file"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 is installed"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠${NC} Not in a virtual environment"

    # Check if venv exists
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        echo -e "${YELLOW}→${NC} Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    else
        echo -e "${YELLOW}→${NC} Creating virtual environment..."
        python3 -m venv "$PROJECT_ROOT/.venv"
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
else
    echo -e "${GREEN}✓${NC} Virtual environment is active"
fi

# Install/upgrade dependencies
echo ""
echo "=========================================="
echo "📦 Installing dependencies..."
echo "=========================================="

cd "$API_DIR"

if pip install -r requirements.txt --quiet; then
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Export environment variables
echo ""
echo "=========================================="
echo "🔧 Loading environment variables..."
echo "=========================================="

export $(grep -v '^#' "$PROJECT_ROOT/src/.env" | xargs)
echo -e "${GREEN}✓${NC} Environment variables loaded"

# Check database connection
echo ""
echo "=========================================="
echo "🔍 Testing database connection..."
echo "=========================================="

python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('BRONZE_DB_HOST'),
        dbname=os.getenv('BRONZE_DB_NAME'),
        user=os.getenv('BRONZE_DB_USER'),
        password=os.getenv('BRONZE_DB_PASSWORD'),
        port=os.getenv('BRONZE_DB_PORT', '5432'),
        sslmode='require'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    cursor.close()
    conn.close()
    print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database connection test failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Database connection successful"

# Start the API
echo ""
echo "=========================================="
echo "🚀 Starting API server..."
echo "=========================================="
echo ""
echo -e "${GREEN}API will be available at:${NC}"
echo -e "  ${YELLOW}→${NC} http://localhost:8000"
echo -e "  ${YELLOW}→${NC} Docs: http://localhost:8000/docs"
echo -e "  ${YELLOW}→${NC} ReDoc: http://localhost:8000/redoc"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run uvicorn
cd "$API_DIR"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
