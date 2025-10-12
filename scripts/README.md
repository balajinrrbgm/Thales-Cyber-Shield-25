# Thales Cyber Shield - Container Deployment Scripts

This directory contains two PowerShell scripts for deploying the Thales Cyber Shield application:

## 1. run-containers.ps1
**Purpose**: Build and run containers locally
- Builds Docker images from source code
- Suitable for development and local testing
- Requires source code and build dependencies

**Usage**:
```powershell
.\scripts\run-containers.ps1
```

## 2. deploy-container-simple.ps1 
**Purpose**: Deploy using pre-built images from Docker Hub
- Pulls pre-built images from Docker Hub
- Faster deployment (no build time)
- Perfect for production or quick demos
- No local building required

**Usage**:
```powershell
.\scripts\deploy-container-simple.ps1
```

## Docker Hub Images Used

### Main Application
- **Image**: `balajinrrb91gm/thales-cyber-shield:latest`
- **Size**: ~6.04 GB
- **Contains**: Python 3.11, ML libraries, FastAPI, threat detection models

### Frontend Dashboard  
- **Image**: `balajinrrb91gm/thales-frontend:latest`
- **Size**: ~54.2 MB
- **Contains**: Nginx, static dashboard files

### Database
- **Image**: `postgres:13`
- **Size**: ~445 MB
- **Contains**: PostgreSQL database server

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Main Application│    │   PostgreSQL    │
│   Dashboard     │    │   (FastAPI)      │    │   Database      │
│   Port: 3000    │    │   Port: 8000     │    │   Port: 5432    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        thales-network
```

## Access URLs

After successful deployment:

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs  
- **API Health Check**: http://localhost:8000/health
- **Database**: localhost:5432 (thales/thales123)

## Management Commands

```powershell
# View container logs
podman logs <container-name>

# Stop all containers
podman stop postgres-db thales-cyber-shield thales-frontend

# Remove all containers  
podman rm postgres-db thales-cyber-shield thales-frontend

# View running containers
podman ps
```

## Environment Variables

The application uses these key environment variables:

- `DATABASE_URL`: `postgresql+asyncpg://thales:thales123@postgres-db:5432/thales_db`
- `SECRET_KEY`: `thales-secret-key-for-hackathon-2025`
- `DEBUG`: `true`
- `THALES_ENVIRONMENT`: `demo`
- `THALES_REGION`: `india`

## Prerequisites

- Windows PowerShell 5.1+
- Podman or Docker installed and running
- Internet connection (for pulling images)

## Troubleshooting

1. **Container name already in use**: Stop and remove existing containers first
2. **Port already in use**: Check if other services are using ports 3000, 5432, or 8000
3. **Network issues**: Ensure Docker/Podman daemon is running
4. **Image pull failures**: Check internet connection and Docker Hub access

## For Thales GenTech India Hackathon 2025

🛡️ **Thales Cyber Shield - Protecting India's Digital Future!**

Ready for Hackathon Demo 🚀