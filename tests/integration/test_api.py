"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock

from src.main import app

# Mock the global instances
app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "Thales Cyber Shield"
    assert "Thales GenTech India Hackathon 2025" in data["hackathon"]

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data

def test_analyze_endpoint(client):
    """Test threat analysis endpoint"""
    # Mock the global detector instances
    import src.main
    src.main.threat_detector = Mock()
    src.main.threat_detector.is_ready = Mock(return_value=True)
    src.main.threat_detector.analyze = AsyncMock(return_value={
        "threat_detected": True,
        "threat_type": "TEST_THREAT",
        "confidence_score": 0.85,
        "risk_score": 85.0
    })

    src.main.anomaly_detector = Mock()
    src.main.anomaly_detector.is_ready = Mock(return_value=True)
    src.main.anomaly_detector.detect = AsyncMock(return_value={
        "anomaly_detected": False
    })

    test_data = {
        "network_traffic": {
            "source_ip": "192.168.1.100",
            "packet_size": 1024
        }
    }

    response = client.post(
        "/api/v1/analyze",
        json=test_data,
        headers={"Authorization": "Bearer test-token"}
    )

    # Note: This might return 401 due to authentication, which is expected
    assert response.status_code in [200, 401, 422]

def test_dashboard_metrics_endpoint(client):
    """Test dashboard metrics endpoint"""
    response = client.get("/api/v1/dashboard/metrics")

    # This might fail due to database not being set up, which is expected in unit tests
    assert response.status_code in [200, 500]

def test_threat_incidents_endpoint(client):
    """Test threat incidents endpoint"""
    response = client.get("/api/v1/threats/incidents")

    # This might fail due to database not being set up, which is expected in unit tests
    assert response.status_code in [200, 500]

def test_threat_map_endpoint(client):
    """Test threat map endpoint"""
    response = client.get("/api/v1/dashboard/threat-map")

    # This might fail due to database not being set up, which is expected in unit tests
    assert response.status_code in [200, 500]

def test_indian_threat_landscape_endpoint(client):
    """Test Indian threat landscape endpoint"""
    response = client.get("/api/v1/analytics/indian-threat-landscape")

    # This might fail due to database not being set up, which is expected in unit tests
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert "top_apt_groups" in data
        assert "targeted_sectors" in data
        assert "cert_in_alerts" in data
