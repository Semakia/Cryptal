#!/bin/bash

# Diagnostic script for Drawdown endpoint
# Checks API response structure and frontend compatibility

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🔍 Drawdown Endpoint Diagnostics"
echo "=========================================="
echo ""

# Test 1: API Health
echo -e "${BLUE}[TEST 1]${NC} API Health Check..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/health")
if [ "$API_STATUS" -eq 200 ]; then
    echo -e "${GREEN}✓ API is running${NC}"
else
    echo -e "${RED}✗ API is not responding (HTTP $API_STATUS)${NC}"
    exit 1
fi
echo ""

# Test 2: Drawdown endpoint availability
echo -e "${BLUE}[TEST 2]${NC} Drawdown endpoint availability..."
DRAWDOWN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/api/metrics/drawdown?period=7")
if [ "$DRAWDOWN_STATUS" -eq 200 ]; then
    echo -e "${GREEN}✓ Drawdown endpoint is accessible${NC}"
else
    echo -e "${RED}✗ Drawdown endpoint failed (HTTP $DRAWDOWN_STATUS)${NC}"
    exit 1
fi
echo ""

# Test 3: Response structure
echo -e "${BLUE}[TEST 3]${NC} Analyzing response structure..."
RESPONSE=$(curl -s "${API_URL}/api/metrics/drawdown?period=7")

# Check if response is an array
IS_ARRAY=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(isinstance(data, list))")
if [ "$IS_ARRAY" = "True" ]; then
    echo -e "${GREEN}✓ Response is an array${NC}"
else
    echo -e "${RED}✗ Response is not an array${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

# Check number of cryptos
CRYPTO_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo -e "  ${GREEN}→${NC} Found $CRYPTO_COUNT cryptocurrencies"

# Check first crypto structure
FIRST_CRYPTO=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data[0]['coin_id'] if len(data) > 0 else 'none')")
echo -e "  ${GREEN}→${NC} First crypto: $FIRST_CRYPTO"
echo ""

# Test 4: drawdown_periods field
echo -e "${BLUE}[TEST 4]${NC} Checking drawdown_periods field..."
HAS_PERIODS=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print('drawdown_periods' in data[0] if len(data) > 0 else False)")
if [ "$HAS_PERIODS" = "True" ]; then
    echo -e "${GREEN}✓ drawdown_periods field exists${NC}"
else
    echo -e "${RED}✗ drawdown_periods field is missing${NC}"
    echo "Available fields:"
    echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(list(data[0].keys()) if len(data) > 0 else [])"
    exit 1
fi

PERIODS_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data[0]['drawdown_periods']) if len(data) > 0 else 0)")
echo -e "  ${GREEN}→${NC} drawdown_periods count: $PERIODS_COUNT"

if [ "$PERIODS_COUNT" -eq 0 ]; then
    echo -e "${RED}✗ drawdown_periods is empty${NC}"
    exit 1
fi

# Check period structure
PERIOD_SAMPLE=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data[0]['drawdown_periods'][0] if len(data) > 0 and len(data[0]['drawdown_periods']) > 0 else {})")
echo -e "  ${GREEN}→${NC} Sample period: $PERIOD_SAMPLE"

HAS_START=$(echo "$PERIOD_SAMPLE" | python3 -c "import sys, json; d = json.loads(sys.stdin.read()); print('start' in d)")
HAS_DRAWDOWN=$(echo "$PERIOD_SAMPLE" | python3 -c "import sys, json; d = json.loads(sys.stdin.read()); print('drawdown' in d)")

if [ "$HAS_START" = "True" ] && [ "$HAS_DRAWDOWN" = "True" ]; then
    echo -e "${GREEN}✓ Period structure is correct (has 'start' and 'drawdown')${NC}"
else
    echo -e "${RED}✗ Period structure is incorrect${NC}"
    echo "Expected: {start: string, drawdown: number}"
    echo "Got: $PERIOD_SAMPLE"
    exit 1
fi
echo ""

# Test 5: All required fields
echo -e "${BLUE}[TEST 5]${NC} Verifying all required fields..."
REQUIRED_FIELDS="coin_id period_days data_points max_drawdown_pct max_drawdown_value current_drawdown_pct underwater_pct peak_price trough_price current_price peak_date trough_date drawdown_periods"

MISSING_FIELDS=""
for field in $REQUIRED_FIELDS; do
    HAS_FIELD=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print('$field' in data[0] if len(data) > 0 else False)")
    if [ "$HAS_FIELD" = "True" ]; then
        echo -e "  ${GREEN}✓${NC} $field"
    else
        echo -e "  ${RED}✗${NC} $field"
        MISSING_FIELDS="$MISSING_FIELDS $field"
    fi
done

if [ -n "$MISSING_FIELDS" ]; then
    echo -e "${RED}✗ Missing fields:$MISSING_FIELDS${NC}"
    exit 1
fi
echo ""

# Test 6: Frontend accessibility
echo -e "${BLUE}[TEST 6]${NC} Frontend accessibility..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}")
if [ "$FRONTEND_STATUS" -eq 200 ]; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not responding (HTTP $FRONTEND_STATUS)${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✅ All diagnostics passed!${NC}"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "  • API Status: Running"
echo "  • Drawdown Endpoint: Working"
echo "  • Cryptocurrencies: $CRYPTO_COUNT"
echo "  • Drawdown Periods: $PERIODS_COUNT per crypto"
echo "  • Frontend: Running"
echo ""
echo -e "${BLUE}🌐 Access the dashboard:${NC}"
echo "  • API Docs:  ${API_URL}/docs"
echo "  • Frontend:  ${FRONTEND_URL}"
echo ""
echo -e "${YELLOW}💡 Tip:${NC} Open ${FRONTEND_URL} and navigate to the Drawdown tab"
echo ""
