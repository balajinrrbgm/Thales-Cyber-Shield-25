# Simple test script for Thales Cyber Shield
Write-Host "Testing Thales Cyber Shield Services..." -ForegroundColor Green
Write-Host ""

# Test API Health
Write-Host "Testing API Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API is responding on port 8000" -ForegroundColor Green
    } else {
        Write-Host "⚠️  API returned status: $($response.StatusCode)" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "❌ API not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Frontend
Write-Host "Testing Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is responding on port 3000" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Frontend returned status: $($response.StatusCode)" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "❌ Frontend not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Database Connection
Write-Host "Testing Database..." -ForegroundColor Yellow
try {
    $result = & podman exec postgres-db pg_isready -U thales -d thales_db
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database is ready" -ForegroundColor Green
    } else {
        Write-Host "❌ Database connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Database test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Container Status
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
& podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "🎉 Thales Cyber Shield Test Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   • Frontend Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "   • API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • API Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "🛡️ Thales Cyber Shield - Ready for Demo!" -ForegroundColor Green