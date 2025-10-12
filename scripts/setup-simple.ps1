# Thales Cyber Shield Setup Script for Windows
# For Thales GenTech India Hackathon 2025

Write-Host "Setting up Thales Cyber Shield..." -ForegroundColor Green
Write-Host "AI-Powered Threat Intelligence & Response System" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
$directories = @("models", "data\sample_data", "logs")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   Created: $dir" -ForegroundColor Gray
    }
}

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $version = [version]$matches[1]
        $requiredVersion = [version]"3.9"
        
        if ($version -ge $requiredVersion) {
            Write-Host "Python $pythonVersion found" -ForegroundColor Green
        } else {
            Write-Host "Python 3.9+ required. Found: $pythonVersion" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Create sample configuration
if (!(Test-Path ".env")) {
    Write-Host "Creating environment configuration..." -ForegroundColor Yellow
    @"
# Thales Cyber Shield Configuration
SECRET_KEY=thales-secret-key-for-hackathon-2025
DEBUG=true
DATABASE_URL=postgresql://thales:thales123@localhost:5432/thales_db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO

# API Keys (get from respective providers)
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
SHODAN_API_KEY=your_shodan_api_key_here

# Thales specific configuration
THALES_ENVIRONMENT=development
THALES_REGION=india
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Created .env file" -ForegroundColor Green
} else {
    Write-Host "Environment configuration exists" -ForegroundColor Green
}

# Check container runtime
if (Test-Command "podman") {
    Write-Host "Podman found" -ForegroundColor Green
} elseif (Test-Command "docker") {
    Write-Host "Docker found" -ForegroundColor Green
} else {
    Write-Host "Podman/Docker not found" -ForegroundColor DarkYellow
}

# Create sample data
Write-Host "Creating sample threat data..." -ForegroundColor Yellow
$sampleData = '[
  {
    "timestamp": "2025-10-12T12:00:00Z",
    "threat_type": "APT36_TRANSPARENT_TRIBE",
    "source_ip": "203.0.113.100",
    "target_ip": "10.0.0.50",
    "confidence": 0.85,
    "description": "APT36 credential harvesting attempt detected"
  }
]'
$sampleData | Out-File -FilePath "data\sample_data\indian_threat_indicators.json" -Encoding UTF8

Write-Host ""
Write-Host "Thales Cyber Shield setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "   1. Edit .env file with your API keys" -ForegroundColor White
Write-Host "   2. Run: python src\main.py" -ForegroundColor White
Write-Host "   3. Open browser: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Container deployment:" -ForegroundColor Cyan
Write-Host "   1. Run: .\scripts\run-containers.ps1" -ForegroundColor White
Write-Host "   2. Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Built for Thales GenTech India Hackathon 2025" -ForegroundColor Green