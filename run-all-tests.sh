#!/bin/bash

# Comprehensive Test Runner for Crypto Tracker
# Run all Playwright tests systematically

echo "🚀 Starting Comprehensive Test Suite for Crypto Tracker"
echo "======================================================="

# Change to frontend directory
cd /Users/iddrisuabdulrazakiddrisu/crypto-tracker-project/crypto-tracker-frontend

# Check if servers are running
echo "🔍 Checking server status..."
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend server is running on port 5173"
else
    echo "❌ Frontend server is not running. Please start with: npm run dev"
    exit 1
fi

if curl -s http://127.0.0.1:5001/portfolio > /dev/null; then
    echo "✅ Backend server is running on port 5001"
else
    echo "❌ Backend server is not running. Please start with: python3 app.py"
    exit 1
fi

echo ""
echo "🧪 TEST 1: Portfolio Features"
echo "=============================="
npx playwright test tests/portfolio.spec.js --reporter=line
PORTFOLIO_EXIT_CODE=$?

echo ""
echo "📊 TEST 2: Analytics Dashboard"
echo "=============================="
npx playwright test tests/analytics.spec.js --reporter=line
ANALYTICS_EXIT_CODE=$?

echo ""
echo "💰 TEST 3: Transaction Management"
echo "================================="
npx playwright test tests/transactions.spec.js --reporter=line
TRANSACTIONS_EXIT_CODE=$?

echo ""
echo "🎯 TEST 4: Full Integration Test"
echo "==============================="
npx playwright test --reporter=line
FULL_EXIT_CODE=$?

echo ""
echo "📋 TEST SUMMARY"
echo "==============="

if [ $PORTFOLIO_EXIT_CODE -eq 0 ]; then
    echo "✅ Portfolio Tests: PASSED"
else
    echo "❌ Portfolio Tests: FAILED"
fi

if [ $ANALYTICS_EXIT_CODE -eq 0 ]; then
    echo "✅ Analytics Tests: PASSED"
else
    echo "❌ Analytics Tests: FAILED"
fi

if [ $TRANSACTIONS_EXIT_CODE -eq 0 ]; then
    echo "✅ Transaction Tests: PASSED"
else
    echo "❌ Transaction Tests: FAILED"
fi

if [ $FULL_EXIT_CODE -eq 0 ]; then
    echo "✅ Full Integration: PASSED"
else
    echo "❌ Full Integration: FAILED"
fi

echo ""
echo "📊 Generating HTML Report..."
npx playwright show-report --host=127.0.0.1 --port=9323 &
REPORT_PID=$!

echo "🎉 Test Suite Complete!"
echo "======================="
echo "📊 View detailed report at: http://127.0.0.1:9323"
echo "📁 Test artifacts saved in: playwright-report/"
echo "🎥 Screenshots and videos available for failed tests"

# Calculate overall success
TOTAL_FAILURES=$((PORTFOLIO_EXIT_CODE + ANALYTICS_EXIT_CODE + TRANSACTIONS_EXIT_CODE + FULL_EXIT_CODE))

if [ $TOTAL_FAILURES -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED! Your crypto tracker is working perfectly! 🚀"
    exit 0
else
    echo "⚠️  Some tests failed. Check the report for details."
    exit 1
fi