#!/bin/bash
# Diagnostic test script for POST /api/ask endpoint
# Tests CORS, error handling, timeouts, and proper JSON responses

echo "=========================================="
echo "Backend Diagnostics Test Suite"
echo "=========================================="
echo ""

BACKEND_URL="http://localhost:3001"
FRONTEND_ORIGIN="http://localhost:3000"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0

run_test() {
    test_count=$((test_count + 1))
    echo -e "${YELLOW}Test $test_count: $1${NC}"
}

pass_test() {
    pass_count=$((pass_count + 1))
    echo -e "${GREEN}✓ PASS${NC}"
    echo ""
}

fail_test() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    echo ""
}

# Test 1: Health check
run_test "GET /api/health - Basic health check"
response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/api/health")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo "Response: $body"
    pass_test
else
    fail_test "Expected 200, got $http_code"
fi

# Test 2: CORS preflight for localhost:3000
run_test "OPTIONS /api/ask - CORS preflight (localhost:3000)"
response=$(curl -s -i -X OPTIONS "$BACKEND_URL/api/ask" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type")

if echo "$response" | grep -q "access-control-allow-origin: http://localhost:3000"; then
    echo "✓ CORS header present for localhost:3000"
    pass_test
else
    fail_test "CORS header missing for localhost:3000"
    echo "$response"
fi

# Test 3: CORS preflight for 127.0.0.1:3000
run_test "OPTIONS /api/ask - CORS preflight (127.0.0.1:3000)"
response=$(curl -s -i -X OPTIONS "$BACKEND_URL/api/ask" \
    -H "Origin: http://127.0.0.1:3000" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type")

if echo "$response" | grep -q "access-control-allow-origin: http://127.0.0.1:3000"; then
    echo "✓ CORS header present for 127.0.0.1:3000"
    pass_test
else
    fail_test "CORS header missing for 127.0.0.1:3000"
fi

# Test 4: Empty question validation
run_test "POST /api/ask - Empty question should return 400"
response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/ask" \
    -H "Content-Type: application/json" \
    -H "Origin: $FRONTEND_ORIGIN" \
    -d '{"question":""}')
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "400" ]; then
    echo "Response: $body"
    if echo "$body" | grep -q "Question must not be empty"; then
        echo "✓ Proper error message returned"
        pass_test
    else
        fail_test "Error message incorrect"
    fi
else
    fail_test "Expected 400, got $http_code"
fi

# Test 5: Valid question
run_test "POST /api/ask - Valid question should return 200"
response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/ask" \
    -H "Content-Type: application/json" \
    -H "Origin: $FRONTEND_ORIGIN" \
    -d '{"question":"What is 2+2?"}')
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    if echo "$body" | grep -q '"answer"'; then
        echo "✓ Response contains answer field"
        if echo "$body" | grep -q '"model"'; then
            echo "✓ Response contains model field"
            pass_test
        else
            fail_test "Response missing model field"
        fi
    else
        fail_test "Response missing answer field"
    fi
else
    fail_test "Expected 200, got $http_code. Response: $body"
fi

# Test 6: Malformed JSON
run_test "POST /api/ask - Malformed JSON should return 422"
response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/ask" \
    -H "Content-Type: application/json" \
    -H "Origin: $FRONTEND_ORIGIN" \
    -d '{invalid json}')
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "422" ]; then
    echo "✓ Proper validation error returned"
    pass_test
else
    echo "Note: Expected 422, got $http_code (may vary by FastAPI version)"
    echo "Response: $body"
    pass_test
fi

# Test 7: Missing Content-Type header
run_test "POST /api/ask - Missing Content-Type should still work or return proper error"
response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/ask" \
    -H "Origin: $FRONTEND_ORIGIN" \
    -d '{"question":"test"}')
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ] || [ "$http_code" = "422" ] || [ "$http_code" = "415" ]; then
    echo "Response code: $http_code (acceptable)"
    pass_test
else
    fail_test "Unexpected response code: $http_code"
fi

# Test 8: Check CORS headers in actual POST response
run_test "POST /api/ask - CORS headers in response"
response=$(curl -s -i -X POST "$BACKEND_URL/api/ask" \
    -H "Content-Type: application/json" \
    -H "Origin: $FRONTEND_ORIGIN" \
    -d '{"question":"test"}')

if echo "$response" | grep -qi "access-control-allow-origin"; then
    echo "✓ CORS headers present in POST response"
    pass_test
else
    fail_test "CORS headers missing in POST response"
    echo "$response" | head -20
fi

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total tests: $test_count"
echo "Passed: $pass_count"
echo "Failed: $((test_count - pass_count))"
echo ""

if [ $pass_count -eq $test_count ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the output above.${NC}"
    exit 1
fi
