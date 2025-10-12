# Test Script for Thales Cyber Shield - Windows Version
# For Thales GenTech India Hackathon 2025

Write-Host "🧪 Running Thales Cyber Shield Tests..." -ForegroundColor Green
Write-Host ""

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    $pythonCmd = ".\venv\Scripts\python.exe"
} else {
    Write-Host "⚠️  Virtual environment not found. Using system Python." -ForegroundColor DarkYellow
    $pythonCmd = "python"
}

# Check if pytest is available
try {
    & $pythonCmd -m pytest --version | Out-Null
    Write-Host "✅ pytest found" -ForegroundColor Green
} catch {
    Write-Host "❌ pytest not found. Installing..." -ForegroundColor Red
    & $pythonCmd -m pip install pytest pytest-cov pytest-asyncio
}

# Run unit tests
Write-Host ""
Write-Host "📋 Running unit tests..." -ForegroundColor Yellow
if (Test-Path "tests\unit") {
    try {
        & $pythonCmd -m pytest tests\unit\ -v --cov=src --cov-report=html --cov-report=term
        Write-Host "✅ Unit tests completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Unit tests failed" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Unit tests directory not found" -ForegroundColor DarkYellow
}

# Run integration tests  
Write-Host ""
Write-Host "🔗 Running integration tests..." -ForegroundColor Yellow
if (Test-Path "tests\integration") {
    try {
        & $pythonCmd -m pytest tests\integration\ -v
        Write-Host "✅ Integration tests completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Integration tests failed" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Integration tests directory not found" -ForegroundColor DarkYellow
}

# Check container status
Write-Host ""
Write-Host "🐳 Checking container status..." -ForegroundColor Yellow
if (Test-Command "podman") {
    $containers = & podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    if ($containers.Count -gt 1) {
        Write-Host "Running containers:" -ForegroundColor Cyan
        $containers | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    } else {
        Write-Host "⚠️  No containers running" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "⚠️  Podman not found" -ForegroundColor DarkYellow
}

# API health check
Write-Host ""
Write-Host "🌐 Testing API endpoints..." -ForegroundColor Yellow
try {
    $healthCheck = @"
import requests
import sys
import json

try:
    # Test main API
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.status_code == 200:
        print('✅ Main API health check passed')
        print(f'   Response: {response.json()}')
    else:
        print(f'❌ Main API health check failed: {response.status_code}')
    
    # Test threat detection endpoint
    test_data = {
        'source_ip': '192.0.2.1',
        'destination_ip': '10.0.0.1',
        'port': 80,
        'protocol': 'HTTP'
    }
    
    response = requests.post('http://localhost:8000/api/v1/threats/analyze', 
                           json=test_data, timeout=5)
    if response.status_code in [200, 422]:  # 422 is validation error, which is expected
        print('✅ Threat analysis endpoint accessible')
    else:
        print(f'⚠️  Threat analysis endpoint returned: {response.status_code}')
        
except requests.exceptions.ConnectionError:
    print('⚠️  API not running or unreachable')
    print('   Start the application first:')
    print('   .\venv\Scripts\python.exe src\main.py')
except Exception as e:
    print(f'❌ Error testing API: {str(e)}')
"@
    
    $healthCheck | & $pythonCmd
} catch {
    Write-Host "❌ Failed to run API health check" -ForegroundColor Red
}

# Test frontend availability
Write-Host ""
Write-Host "🌐 Testing frontend availability..." -ForegroundColor Yellow
try {
    $frontendCheck = @"
import requests
import sys

try:
    response = requests.get('http://localhost:3000', timeout=5)
    if response.status_code == 200:
        print('✅ Frontend is accessible')
    else:
        print(f'⚠️  Frontend returned status: {response.status_code}')
except requests.exceptions.ConnectionError:
    print('⚠️  Frontend not running or unreachable')
    print('   Start containers: podman-compose up -d')
except Exception as e:
    print(f'❌ Error testing frontend: {str(e)}')
"@
    
    $frontendCheck | & $pythonCmd
} catch {
    Write-Host "❌ Failed to run frontend check" -ForegroundColor Red
}

# Generate test report
Write-Host ""
Write-Host "📊 Generating test report..." -ForegroundColor Yellow
$testReport = @"
# Thales Cyber Shield Test Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Test Summary
- Unit Tests: $(if (Test-Path "htmlcov\index.html") { "✅ Completed with coverage report" } else { "⚠️ Coverage report not generated" })
- Integration Tests: $(if (Test-Path "tests\integration") { "✅ Available" } else { "⚠️ Not found" })
- API Health: Tested against localhost:8000
- Frontend Health: Tested against localhost:3000

## Coverage Report
$(if (Test-Path "htmlcov\index.html") { "Available at: htmlcov\index.html" } else { "Not generated" })

## Next Steps
1. Review test results above
2. Check coverage report: htmlcov\index.html
3. Ensure all containers are running: podman ps
4. Access dashboard: http://localhost:3000
5. Check API docs: http://localhost:8000/docs

## Thales Cyber Shield Status
🛡️ Protecting India's Digital Infrastructure
🚀 Ready for Hackathon Demo
"@

$testReport | Out-File -FilePath "test-report.md" -Encoding UTF8

Write-Host ""
Write-Host "🎉 Test execution completed!" -ForegroundColor Green
Write-Host "📊 Test report saved: test-report.md" -ForegroundColor Cyan
Write-Host "📊 Coverage report: htmlcov\index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Quick Access URLs:" -ForegroundColor Green
Write-Host "   • Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "🛡️ Thales Cyber Shield - Ready for Demo!" -ForegroundColor Green