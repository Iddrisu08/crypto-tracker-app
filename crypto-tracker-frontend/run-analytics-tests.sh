#!/bin/bash

echo "Starting Playwright tests for Analytics Dashboard..."
echo "Working directory: $(pwd)"

# Run the analytics tests specifically
echo "Running analytics.spec.js tests..."
npx playwright test tests/analytics.spec.js --reporter=list

echo "Tests completed!"
