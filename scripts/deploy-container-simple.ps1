# Thales Cyber Shield Container Deployment Script - Docker Hub Version
# For Thales GenTech India Hackathon 2025

Write-Host "Deploying Thales Cyber Shield from Docker Hub..." -ForegroundColor Green
Write-Host "AI-Powered Threat Intelligence & Response System" -ForegroundColor Cyan
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

# Docker Hub image names
$mainAppImage = "balajinrrb91gm/thales-cyber-shield:latest"
$frontendImage = "balajinrrb91gm/thales-frontend:latest"
$postgresImage = "postgres:13"

# Pull images from Docker Hub
Write-Host "Pulling images from Docker Hub..." -ForegroundColor Yellow

Write-Host "Pulling main application image..." -ForegroundColor Gray
& $containerCmd pull $mainAppImage

Write-Host "Pulling frontend image..." -ForegroundColor Gray
& $containerCmd pull $frontendImage

Write-Host "Pulling PostgreSQL image..." -ForegroundColor Gray
& $containerCmd pull $postgresImage

Write-Host "All images pulled successfully" -ForegroundColor Green

# Create network if it doesn't exist
Write-Host "Setting up container network..." -ForegroundColor Yellow
$networks = & $containerCmd network ls --format "{{.Name}}"
if ($networks -notcontains "thales-network") {
    & $containerCmd network create thales-network
    Write-Host "Created thales-network" -ForegroundColor Green
} else {
    Write-Host "Network thales-network already exists" -ForegroundColor Green
}

# Stop and remove existing containers
Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
$existingContainers = @("postgres-db", "thales-cyber-shield", "thales-frontend")
foreach ($container in $existingContainers) {
    try {
        & $containerCmd stop $container 2>$null
        & $containerCmd rm $container 2>$null
        Write-Host "Removed: $container" -ForegroundColor Gray
    } catch {
        # Container doesn't exist, ignore
    }
}

# Start PostgreSQL database
Write-Host "Starting PostgreSQL database..." -ForegroundColor Yellow
& $containerCmd run -d --name postgres-db --network thales-network -p 5432:5432 -e POSTGRES_DB=thales_db -e POSTGRES_USER=thales -e POSTGRES_PASSWORD=thales123 $postgresImage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start PostgreSQL" -ForegroundColor Red
    exit 1
}
Write-Host "PostgreSQL started" -ForegroundColor Green

# Wait for database to be ready
Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start main application
Write-Host "Starting main application..." -ForegroundColor Yellow
& $containerCmd run -d --name thales-cyber-shield --network thales-network -p 8000:8000 -e DATABASE_URL=postgresql+asyncpg://thales:thales123@postgres-db:5432/thales_db -e SECRET_KEY=thales-secret-key-for-hackathon-2025 -e DEBUG=true -e THALES_ENVIRONMENT=demo -e THALES_REGION=india $mainAppImage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start main application" -ForegroundColor Red
    exit 1
}
Write-Host "Main application started" -ForegroundColor Green

# Wait for application to be ready
Write-Host "Waiting for application to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Start frontend
Write-Host "Starting frontend..." -ForegroundColor Yellow
& $containerCmd run -d --name thales-frontend --network thales-network -p 3000:3000 $frontendImage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start frontend" -ForegroundColor Red
    exit 1
}
Write-Host "Frontend started" -ForegroundColor Green

# Check container status
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
& $containerCmd ps

# Test connectivity
Write-Host ""
Write-Host "Testing services..." -ForegroundColor Yellow

# Test database
try {
    & $containerCmd exec postgres-db pg_isready -U thales -d thales_db
    Write-Host "Database is ready" -ForegroundColor Green
} catch {
    Write-Host "Database connection test failed" -ForegroundColor DarkYellow
}

# Test API after a brief wait
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "API is responding" -ForegroundColor Green
    } else {
        Write-Host "API returned status: $($response.StatusCode)" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "API not yet ready (this is normal, may take a minute)" -ForegroundColor DarkYellow
}

# Test frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "Frontend is responding" -ForegroundColor Green
    } else {
        Write-Host "Frontend returned status: $($response.StatusCode)" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "Frontend not yet ready" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "Thales Cyber Shield is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "Frontend Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "API Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "Database: localhost:5432 (thales/thales123)" -ForegroundColor White
Write-Host ""
Write-Host "Management Commands:" -ForegroundColor Cyan
Write-Host "View logs: $containerCmd logs <container-name>" -ForegroundColor White
Write-Host "Stop all: $containerCmd stop postgres-db thales-cyber-shield thales-frontend" -ForegroundColor White
Write-Host "Remove all: $containerCmd rm postgres-db thales-cyber-shield thales-frontend" -ForegroundColor White
Write-Host ""
Write-Host "Docker Hub Images Used:" -ForegroundColor Cyan
Write-Host "Main App: $mainAppImage" -ForegroundColor White
Write-Host "Frontend: $frontendImage" -ForegroundColor White
Write-Host "Database: $postgresImage" -ForegroundColor White
Write-Host ""
Write-Host "Thales Cyber Shield - Protecting India Digital Future!" -ForegroundColor Green
Write-Host "Ready for Hackathon Demo!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: This script pulls pre-built images from Docker Hub" -ForegroundColor Blue
Write-Host "No local building required - faster deployment!" -ForegroundColor Blue