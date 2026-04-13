#!/bin/bash

# Test script for fixed metrics endpoints
# Tests Volatility, Sharpe, Drawdown, and Correlation endpoints

BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo "=========================================="
echo "🧪 Testing Fixed Metrics Endpoints"
echo "=========================================="
echo ""

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_fields=$3

    echo -n "Testing ${name}... "

    response=$(curl -s "${BASE_URL}${url}")

    # Check if response is valid JSON
    if ! echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        echo -e "${RED}✗ FAILED${NC} (Invalid JSON)"
        echo "  Response: $response"
        ((TESTS_FAILED++))
        return 1
    fi

    # Check for error
    if echo "$response" | grep -q '"detail"'; then
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Error: $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('detail', 'Unknown error'))")"
        ((TESTS_FAILED++))
        return 1
    fi

    # Check expected fields
    missing_fields=""
    for field in $expected_fields; do
        if ! echo "$response" | grep -q "\"$field\""; then
            missing_fields="$missing_fields $field"
        fi
    done

    if [ -n "$missing_fields" ]; then
        echo -e "${RED}✗ FAILED${NC} (Missing fields:$missing_fields)"
        ((TESTS_FAILED++))
        return 1
    fi

    echo -e "${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))
    return 0
}

# Test Volatility endpoints
echo -e "${BLUE}═══ Volatility Endpoints ═══${NC}"
test_endpoint "Volatility (single)" \
    "/api/metrics/volatility/bitcoin?period=7" \
    "coin_id period_days data_points mean_price std_dev variance coefficient_of_variation var_95 min_price max_price price_range"

test_endpoint "Volatility (all)" \
    "/api/metrics/volatility?period=7" \
    "coin_id period_days data_points"

echo ""

# Test Sharpe endpoints
echo -e "${BLUE}═══ Sharpe Ratio Endpoints ═══${NC}"
test_endpoint "Sharpe (single)" \
    "/api/metrics/sharpe/bitcoin?period=30&risk_free_rate=0.02" \
    "coin_id period_days data_points total_return annualized_return annualized_volatility sharpe_ratio sortino_ratio start_price end_price"

test_endpoint "Sharpe (all)" \
    "/api/metrics/sharpe?period=30&risk_free_rate=0.02" \
    "coin_id sharpe_ratio sortino_ratio"

echo ""

# Test Drawdown endpoints
echo -e "${BLUE}═══ Drawdown Endpoints ═══${NC}"
test_endpoint "Drawdown (single)" \
    "/api/metrics/drawdown/bitcoin?period=30" \
    "coin_id period_days data_points max_drawdown_pct max_drawdown_value current_drawdown_pct underwater_pct peak_price trough_price current_price peak_date trough_date drawdown_periods"

test_endpoint "Drawdown (all)" \
    "/api/metrics/drawdown?period=30" \
    "coin_id max_drawdown_pct peak_price trough_price drawdown_periods"

echo ""

# Test Correlation endpoint
echo -e "${BLUE}═══ Correlation Endpoints ═══${NC}"
test_endpoint "Correlation Matrix" \
    "/api/metrics/correlation?period=30" \
    "period_days correlations diversification_score highest_correlation lowest_correlation"

echo ""
echo "=========================================="
echo "📊 Test Results Summary"
echo "=========================================="
echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
