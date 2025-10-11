#!/usr/bin/env python3
"""
Thales Cyber Shield - Main Application Entry Point
AI-Powered Threat Intelligence & Response System

This is the main entry point for the Thales Cyber Shield application.
Designed for the Thales GenTech India Hackathon 2025 - Cybersecurity Theme.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn

from src.core.config import get_settings
from src.core.database import init_db
from src.core.security import SecurityManager
from src.api.routes import threat_router, dashboard_router, analytics_router
from src.ml_models.threat_detector import ThreatDetector
from src.ml_models.anomaly_detector import AnomalyDetector
from src.core.threat_intelligence import ThreatIntelligenceEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
threat_detector: ThreatDetector = None
anomaly_detector: AnomalyDetector = None
threat_intelligence: ThreatIntelligenceEngine = None
security_manager: SecurityManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting Thales Cyber Shield Application...")

    global threat_detector, anomaly_detector, threat_intelligence, security_manager
    settings = get_settings()

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        # Initialize AI models
        threat_detector = ThreatDetector()
        await threat_detector.load_models()
        logger.info("Threat detection models loaded")

        anomaly_detector = AnomalyDetector()
        await anomaly_detector.initialize()
        logger.info("Anomaly detection models initialized")

        # Initialize threat intelligence engine
        threat_intelligence = ThreatIntelligenceEngine()
        await threat_intelligence.start()
        logger.info("Threat intelligence engine started")

        # Initialize security manager
        security_manager = SecurityManager()
        logger.info("Security manager initialized")

        logger.info("Thales Cyber Shield Application started successfully!")

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Thales Cyber Shield Application...")
    if threat_intelligence:
        await threat_intelligence.stop()
    logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Thales Cyber Shield",
    description="AI-Powered Threat Intelligence & Response System for Indian Digital Infrastructure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(threat_router, prefix="/api/v1/threats", tags=["Threat Detection"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Root endpoint with application information"""
    return {
        "application": "Thales Cyber Shield",
        "description": "AI-Powered Threat Intelligence & Response System",
        "version": "1.0.0",
        "hackathon": "Thales GenTech India Hackathon 2025",
        "theme": "Cybersecurity",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "threats": "/api/v1/threats",
            "dashboard": "/api/v1/dashboard",
            "analytics": "/api/v1/analytics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    global threat_detector, anomaly_detector, threat_intelligence

    health_status = {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "threat_detector": threat_detector is not None and threat_detector.is_ready(),
            "anomaly_detector": anomaly_detector is not None and anomaly_detector.is_ready(),
            "threat_intelligence": threat_intelligence is not None and threat_intelligence.is_running(),
            "database": True  # Add actual DB health check
        }
    }

    # Check if all services are healthy
    all_healthy = all(health_status["services"].values())
    if not all_healthy:
        health_status["status"] = "degraded"

    return health_status

@app.post("/api/v1/analyze")
async def analyze_threat(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    token: str = Depends(security)
):
    """Main threat analysis endpoint"""
    try:
        # Validate input
        if not data:
            raise HTTPException(status_code=400, detail="No data provided")

        # Perform threat analysis
        results = {}

        if threat_detector and threat_detector.is_ready():
            threat_result = await threat_detector.analyze(data)
            results["threat_analysis"] = threat_result

        if anomaly_detector and anomaly_detector.is_ready():
            anomaly_result = await anomaly_detector.detect(data)
            results["anomaly_analysis"] = anomaly_result

        # Add to threat intelligence
        if threat_intelligence and threat_intelligence.is_running():
            background_tasks.add_task(
                threat_intelligence.process_incident,
                data,
                results
            )

        return {
            "status": "success",
            "analysis_id": f"analysis_{asyncio.get_event_loop().time()}",
            "results": results,
            "timestamp": asyncio.get_event_loop().time()
        }

    except Exception as e:
        logger.error(f"Error in threat analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
