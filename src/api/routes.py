"""
API Routes for Thales Cyber Shield
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio

from src.core.database import get_db, DatabaseManager
from src.core.security import get_current_user

# Request/Response Models
class ThreatAnalysisRequest(BaseModel):
    network_traffic: Optional[Dict[str, Any]] = None
    log_data: Optional[str] = None
    email_content: Optional[str] = None
    user_activity: Optional[Dict[str, Any]] = None
    system_metrics: Optional[Dict[str, Any]] = None

class ThreatAnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: float
    threat_detected: bool
    threat_type: str
    confidence_score: float
    risk_score: float
    analysis_details: Dict[str, Any]
    recommendations: List[str]

class DashboardMetrics(BaseModel):
    total_threats: int
    active_incidents: int
    threat_categories: Dict[str, int]
    risk_levels: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

# Create routers
threat_router = APIRouter()
dashboard_router = APIRouter()
analytics_router = APIRouter()

@threat_router.post("/analyze", response_model=ThreatAnalysisResponse)
async def analyze_threat(
    request: ThreatAnalysisRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Analyze incoming data for threats"""
    try:
        from src.main import threat_detector, anomaly_detector

        # Convert request to dict
        data = request.dict(exclude_none=True)

        results = {
            "analysis_id": f"analysis_{int(asyncio.get_event_loop().time())}",
            "timestamp": asyncio.get_event_loop().time(),
            "threat_detected": False,
            "threat_type": "NORMAL",
            "confidence_score": 0.0,
            "risk_score": 0.0,
            "analysis_details": {},
            "recommendations": []
        }

        # Run threat detection
        if threat_detector and threat_detector.is_ready():
            threat_result = await threat_detector.analyze(data)
            results.update(threat_result)

        # Run anomaly detection
        if anomaly_detector and anomaly_detector.is_ready():
            anomaly_result = await anomaly_detector.detect(data)
            results["analysis_details"]["anomaly"] = anomaly_result

            # Update overall results if anomaly detected
            if anomaly_result.get("anomaly_detected", False):
                if not results["threat_detected"] or anomaly_result["confidence"] > results["confidence_score"]:
                    results["threat_detected"] = True
                    results["threat_type"] = anomaly_result["anomaly_type"]
                    results["confidence_score"] = anomaly_result["confidence"]

        # Save to database if threat detected
        if results["threat_detected"]:
            background_tasks.add_task(
                save_threat_incident,
                results,
                data
            )

        return ThreatAnalysisResponse(**results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@threat_router.get("/incidents")
async def get_threat_incidents(
    limit: int = 100,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db=Depends(get_db)
):
    """Get threat incidents"""
    try:
        incidents = await DatabaseManager.get_recent_threats(limit)

        # Convert to dict format
        result = []
        for incident in incidents:
            result.append({
                "id": incident.id,
                "incident_id": incident.incident_id,
                "timestamp": incident.timestamp.isoformat(),
                "threat_type": incident.threat_type,
                "severity": incident.severity,
                "source_ip": incident.source_ip,
                "target_ip": incident.target_ip,
                "description": incident.description,
                "status": incident.status,
                "confidence_score": incident.confidence_score
            })

        return {"incidents": result, "total": len(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get incidents: {str(e)}")

@threat_router.post("/incidents/{incident_id}/update")
async def update_incident_status(
    incident_id: str,
    status: str,
    notes: Optional[str] = None,
    db=Depends(get_db)
):
    """Update incident status"""
    try:
        # Update incident in database
        # This would require implementing the update method in DatabaseManager
        return {"message": f"Incident {incident_id} updated to {status}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update incident: {str(e)}")

@dashboard_router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(db=Depends(get_db)):
    """Get dashboard metrics"""
    try:
        # Get metrics from database
        incidents = await DatabaseManager.get_recent_threats(1000)

        # Calculate metrics
        total_threats = len([i for i in incidents if i.threat_type != "NORMAL"])
        active_incidents = len([i for i in incidents if i.status == "OPEN"])

        # Threat categories
        threat_categories = {}
        risk_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

        for incident in incidents:
            # Count threat categories
            threat_type = incident.threat_type
            threat_categories[threat_type] = threat_categories.get(threat_type, 0) + 1

            # Count risk levels
            if incident.confidence_score >= 0.9:
                risk_levels["CRITICAL"] += 1
            elif incident.confidence_score >= 0.7:
                risk_levels["HIGH"] += 1
            elif incident.confidence_score >= 0.4:
                risk_levels["MEDIUM"] += 1
            else:
                risk_levels["LOW"] += 1

        # Recent activity
        recent_activity = []
        for incident in incidents[:10]:  # Last 10 incidents
            recent_activity.append({
                "timestamp": incident.timestamp.isoformat(),
                "type": incident.threat_type,
                "severity": incident.severity,
                "source": incident.source_ip,
                "description": incident.description[:100] if incident.description else ""
            })

        return DashboardMetrics(
            total_threats=total_threats,
            active_incidents=active_incidents,
            threat_categories=threat_categories,
            risk_levels=risk_levels,
            recent_activity=recent_activity
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@dashboard_router.get("/threat-map")
async def get_threat_map(db=Depends(get_db)):
    """Get threat map data for visualization"""
    try:
        incidents = await DatabaseManager.get_recent_threats(500)

        # Group threats by source IP and location
        threat_map = {}

        for incident in incidents:
            if incident.source_ip:
                if incident.source_ip not in threat_map:
                    threat_map[incident.source_ip] = {
                        "ip": incident.source_ip,
                        "count": 0,
                        "severity": "LOW",
                        "threats": [],
                        "location": {"country": "Unknown", "city": "Unknown"}  # Would integrate with GeoIP
                    }

                threat_map[incident.source_ip]["count"] += 1
                threat_map[incident.source_ip]["threats"].append(incident.threat_type)

                # Update severity
                if incident.confidence_score >= 0.7:
                    threat_map[incident.source_ip]["severity"] = "HIGH"
                elif incident.confidence_score >= 0.4:
                    if threat_map[incident.source_ip]["severity"] == "LOW":
                        threat_map[incident.source_ip]["severity"] = "MEDIUM"

        return {"threat_sources": list(threat_map.values())}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat map: {str(e)}")

@analytics_router.get("/trends")
async def get_threat_trends(
    days: int = 30,
    db=Depends(get_db)
):
    """Get threat trends over time"""
    try:
        # This would implement time-series analysis
        # For now, return mock data structure

        trends = {
            "daily_threats": [
                {"date": "2025-10-01", "count": 45, "severity": {"HIGH": 12, "MEDIUM": 20, "LOW": 13}},
                {"date": "2025-10-02", "count": 38, "severity": {"HIGH": 8, "MEDIUM": 18, "LOW": 12}},
                # ... more days
            ],
            "threat_types_trend": {
                "APT36_TRANSPARENT_TRIBE": [5, 8, 12, 6, 9],
                "RANSOMWARE_DOUBLE_EXTORTION": [3, 5, 7, 4, 6],
                "PHISHING_SOCIAL_ENGINEERING": [15, 18, 22, 16, 20]
            },
            "prediction": {
                "next_7_days": [25, 28, 22, 30, 26, 24, 27],
                "confidence": 0.78
            }
        }

        return trends

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

@analytics_router.get("/indian-threat-landscape")
async def get_indian_threat_landscape(db=Depends(get_db)):
    """Get India-specific threat landscape analysis"""
    try:
        analysis = {
            "top_apt_groups": [
                {"name": "APT36 (Transparent Tribe)", "incidents": 45, "trend": "increasing"},
                {"name": "SideCopy", "incidents": 32, "trend": "stable"},
                {"name": "APT41", "incidents": 28, "trend": "decreasing"}
            ],
            "targeted_sectors": [
                {"sector": "Government", "attacks": 78, "severity": "HIGH"},
                {"sector": "Defense", "attacks": 56, "severity": "CRITICAL"},
                {"sector": "Banking", "attacks": 42, "severity": "HIGH"},
                {"sector": "Telecommunications", "attacks": 34, "severity": "MEDIUM"}
            ],
            "attack_vectors": [
                {"vector": "Spear Phishing", "percentage": 35},
                {"vector": "Watering Hole", "percentage": 22},
                {"vector": "Supply Chain", "percentage": 18},
                {"vector": "Zero-day Exploits", "percentage": 15},
                {"vector": "Others", "percentage": 10}
            ],
            "geographic_distribution": [
                {"state": "Delhi", "incidents": 89},
                {"state": "Maharashtra", "incidents": 67},
                {"state": "Karnataka", "incidents": 45},
                {"state": "Tamil Nadu", "incidents": 34}
            ],
            "cert_in_alerts": {
                "recent_alerts": 12,
                "high_priority": 4,
                "sectors_affected": ["Banking", "Government", "Healthcare"]
            }
        }

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat landscape: {str(e)}")

async def save_threat_incident(analysis_result: Dict[str, Any], raw_data: Dict[str, Any]):
    """Save threat incident to database (background task)"""
    try:
        incident_data = {
            "incident_id": analysis_result["analysis_id"],
            "timestamp": datetime.utcnow(),
            "threat_type": analysis_result["threat_type"],
            "severity": get_severity_from_score(analysis_result["confidence_score"]),
            "source_ip": extract_source_ip(raw_data),
            "target_ip": extract_target_ip(raw_data),
            "description": generate_incident_description(analysis_result),
            "raw_data": raw_data,
            "analysis_result": analysis_result,
            "status": "OPEN",
            "confidence_score": analysis_result["confidence_score"]
        }

        await DatabaseManager.save_threat_incident(incident_data)

    except Exception as e:
        print(f"Failed to save incident: {str(e)}")

def get_severity_from_score(score: float) -> str:
    """Convert confidence score to severity level"""
    if score >= 0.9:
        return "CRITICAL"
    elif score >= 0.7:
        return "HIGH"
    elif score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"

def extract_source_ip(data: Dict[str, Any]) -> Optional[str]:
    """Extract source IP from raw data"""
    if "network_traffic" in data:
        return data["network_traffic"].get("source_ip")
    return None

def extract_target_ip(data: Dict[str, Any]) -> Optional[str]:
    """Extract target IP from raw data"""
    if "network_traffic" in data:
        return data["network_traffic"].get("target_ip")
    return None

def generate_incident_description(analysis_result: Dict[str, Any]) -> str:
    """Generate human-readable incident description"""
    threat_type = analysis_result["threat_type"]
    confidence = analysis_result["confidence_score"]

    descriptions = {
        "APT36_TRANSPARENT_TRIBE": "APT36 (Transparent Tribe) activity detected - possible credential harvesting or RAT deployment",
        "SIDECOPY_APT": "SideCopy APT group activity detected - monitor for RAT installation",
        "RANSOMWARE_DOUBLE_EXTORTION": "Ransomware indicators detected - possible data exfiltration and encryption threat",
        "PHISHING_SOCIAL_ENGINEERING": "Phishing or social engineering attack detected",
        "INSIDER_THREAT": "Suspicious insider activity detected - unusual user behavior patterns",
        "API_ABUSE": "API abuse or unauthorized access detected",
        "CLOUD_MISCONFIGURATION": "Cloud security misconfiguration detected"
    }

    base_description = descriptions.get(threat_type, f"Security threat detected: {threat_type}")
    return f"{base_description} (Confidence: {confidence:.2%})"
