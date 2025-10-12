# Thales Cyber Shield Container Deployment Script - Windows Version
param(
    [switch]$Force
)

Write-Host "Starting Thales Cyber Shield Containers..." -ForegroundColor Green
Write-Host ""

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check for container runtime
if (Test-Command "podman") {
    $containerCmd = "podman"
    Write-Host "Using Podman" -ForegroundColor Green
} elseif (Test-Command "docker") {
    $containerCmd = "docker" 
    Write-Host "Using Docker" -ForegroundColor Green
} else {
    Write-Host "Neither Podman nor Docker found. Please install one of them." -ForegroundColor Red
    exit 1
}

# Stop and remove existing containers if Force is specified
if ($Force) {
    Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
    $existingContainers = @("postgres-db", "thales-cyber-shield", "thales-frontend")
    foreach ($container in $existingContainers) {
        try {
            & $containerCmd stop $container 2>$null
            & $containerCmd rm $container 2>$null
            Write-Host "   Removed: $container" -ForegroundColor Gray
        } catch {
            # Container doesn't exist, ignore
        }
    }
}

# Build images
Write-Host "Building application images..." -ForegroundColor Yellow

Write-Host "Building main application..." -ForegroundColor Cyan
& $containerCmd build -t thales-cyber-shield .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build main application" -ForegroundColor Red
    exit 1
}

Write-Host "Building frontend..." -ForegroundColor Cyan
& $containerCmd build -f Dockerfile.frontend -t thales-frontend .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build frontend" -ForegroundColor Red
    exit 1
}

# Create network
Write-Host "Setting up network..." -ForegroundColor Yellow
try {
    & $containerCmd network create thales-network 2>$null
} catch {
    # Network might already exist
}

# Start PostgreSQL
Write-Host "Starting PostgreSQL..." -ForegroundColor Yellow
& $containerCmd run -d --name postgres-db --network thales-network -p 5432:5432 -e POSTGRES_DB=thales_db -e POSTGRES_USER=thales -e POSTGRES_PASSWORD=thales123 postgres:13

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start PostgreSQL" -ForegroundColor Red
    exit 1
}

# Wait for database
Write-Host "Waiting for database..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Start main application
Write-Host "Starting main application..." -ForegroundColor Yellow
& $containerCmd run -d --name thales-cyber-shield --network thales-network -p 8000:8000 -e DATABASE_URL=postgresql://thales:thales123@postgres-db:5432/thales_db -e SECRET_KEY=thales-secret-key-for-hackathon-2025 -e DEBUG=true thales-cyber-shield

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start main application" -ForegroundColor Red
    exit 1
}

# Wait for application
Write-Host "Waiting for application..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Start frontend
Write-Host "Starting frontend..." -ForegroundColor Yellow
& $containerCmd run -d --name thales-frontend --network thales-network -p 3000:3000 thales-frontend

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start frontend" -ForegroundColor Red
    exit 1
}

# Show status
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
& $containerCmd ps

Write-Host ""
Write-Host "Thales Cyber Shield is running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Health: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Built for Thales GenTech India Hackathon 2025" -ForegroundColor Green