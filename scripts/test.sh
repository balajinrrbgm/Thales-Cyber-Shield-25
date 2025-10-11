#!/bin/bash

# Test Script for Thales Cyber Shield

echo "🧪 Running Thales Cyber Shield Tests..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run unit tests
echo "📋 Running unit tests..."
python -m pytest tests/unit/ -v --cov=src --cov-report=html

# Run integration tests  
echo "🔗 Running integration tests..."
python -m pytest tests/integration/ -v

# Run security tests
echo "🔒 Running security tests..."
python -m pytest tests/security/ -v

# API health check
echo "🌐 Testing API endpoints..."
python -c "
import requests
import sys

try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.status_code == 200:
        print('✅ API health check passed')
    else:
        print(f'❌ API health check failed: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'⚠️  API not running or unreachable: {str(e)}')
    print('   Start the application first: python src/main.py')
    sys.exit(1)
"

# Performance test
echo "⚡ Running performance tests..."
python -m pytest tests/performance/ -v

echo ""
echo "🎉 All tests completed!"
echo "📊 Coverage report: htmlcov/index.html"
