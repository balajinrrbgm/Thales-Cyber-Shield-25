"""
Unit tests for ThreatDetector
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock
import asyncio

from src.ml_models.threat_detector import ThreatDetector

@pytest.fixture
def threat_detector():
    detector = ThreatDetector()
    detector.is_loaded = True
    return detector

@pytest.mark.asyncio
async def test_threat_detector_initialization():
    """Test ThreatDetector initialization"""
    detector = ThreatDetector()
    assert detector.threat_categories is not None
    assert len(detector.threat_categories) > 0
    assert "APT36_TRANSPARENT_TRIBE" in detector.threat_categories

@pytest.mark.asyncio 
async def test_analyze_normal_traffic(threat_detector):
    """Test analysis of normal network traffic"""
    normal_data = {
        "network_traffic": {
            "packet_size": 1024,
            "connection_duration": 30,
            "bytes_sent": 5000,
            "bytes_received": 5000,
            "port_scan_count": 0,
            "suspicious_strings": [],
            "geo_anomaly_score": 0.1
        }
    }

    result = await threat_detector.analyze(normal_data)

    assert result["threat_detected"] is not None
    assert result["confidence_score"] is not None
    assert result["threat_type"] is not None

@pytest.mark.asyncio
async def test_analyze_apt36_indicators(threat_detector):
    """Test detection of APT36 indicators"""
    apt36_data = {
        "network_traffic": {
            "packet_size": 2048,
            "connection_duration": 300,
            "bytes_sent": 1000,
            "bytes_received": 15000,
            "port_scan_count": 5,
            "suspicious_strings": ["crimson_rat", "transparent_tribe"],
            "geo_anomaly_score": 0.8,
            "privilege_escalation": True
        }
    }

    # Mock the model predictions
    threat_detector.models = {"random_forest": Mock()}
    threat_detector.scalers = {"network": Mock()}
    threat_detector.encoders = {"threat": Mock()}

    # Configure mocks
    threat_detector.scalers["network"].transform = Mock(return_value=np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]))
    threat_detector.models["random_forest"].predict = Mock(return_value=[1])  # APT36 class
    threat_detector.models["random_forest"].predict_proba = Mock(return_value=[[0.1, 0.9, 0.0]])
    threat_detector.encoders["threat"].inverse_transform = Mock(return_value=["APT36_TRANSPARENT_TRIBE"])

    result = await threat_detector.analyze(apt36_data)

    assert result is not None
    assert "analysis_details" in result

def test_extract_features(threat_detector):
    """Test feature extraction from input data"""
    data = {
        "network_traffic": {
            "packet_size": 1024,
            "connection_duration": 60,
            "bytes_sent": 2000,
            "bytes_received": 3000
        }
    }

    features = threat_detector._extract_features(data)

    assert features.shape == (1, 10)  # Should have 10 features
    assert features[0][0] == 1024  # packet_size
    assert features[0][1] == 60    # connection_duration

def test_is_ready(threat_detector):
    """Test readiness check"""
    assert threat_detector.is_ready() == True

    threat_detector.is_loaded = False
    assert threat_detector.is_ready() == False
