"""
Advanced Anomaly Detection System
Specialized for detecting unusual patterns in Indian digital infrastructure
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    AI-powered anomaly detection system for cybersecurity
    Focuses on behavioral anomalies in user activities and system operations
    """

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.baselines = {}
        self.is_initialized = False

        # Anomaly types
        self.anomaly_types = [
            "USER_BEHAVIOR_ANOMALY",
            "NETWORK_TRAFFIC_ANOMALY", 
            "SYSTEM_RESOURCE_ANOMALY",
            "ACCESS_PATTERN_ANOMALY",
            "TEMPORAL_ANOMALY",
            "GEOGRAPHICAL_ANOMALY",
            "DEVICE_ANOMALY",
            "APPLICATION_USAGE_ANOMALY"
        ]

    async def initialize(self):
        """Initialize anomaly detection models"""
        try:
            await self._load_models()
            self.is_initialized = True
            logger.info("Anomaly detection system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize anomaly detector: {str(e)}")
            await self._create_models()

    async def _load_models(self):
        """Load pre-trained anomaly detection models"""
        try:
            self.models['isolation_forest'] = joblib.load('models/anomaly_isolation_forest.pkl')
            self.scalers['anomaly'] = joblib.load('models/anomaly_scaler.pkl')
            self.baselines = joblib.load('models/behavioral_baselines.pkl')
        except FileNotFoundError:
            logger.warning("Anomaly detection models not found, creating new ones")
            await self._create_models()

    async def _create_models(self):
        """Create and train anomaly detection models"""
        # Generate synthetic baseline data
        baseline_data = self._generate_baseline_data()

        # Train Isolation Forest
        self.scalers['anomaly'] = StandardScaler()
        scaled_data = self.scalers['anomaly'].fit_transform(baseline_data)

        self.models['isolation_forest'] = IsolationForest(
            contamination=0.1,  # 10% outliers expected
            random_state=42,
            n_estimators=100
        )
        self.models['isolation_forest'].fit(scaled_data)

        # Create behavioral baselines
        self.baselines = self._create_behavioral_baselines(baseline_data)

        # Save models
        import os
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.models['isolation_forest'], 'models/anomaly_isolation_forest.pkl')
        joblib.dump(self.scalers['anomaly'], 'models/anomaly_scaler.pkl')
        joblib.dump(self.baselines, 'models/behavioral_baselines.pkl')

        self.is_initialized = True
        logger.info("Anomaly detection models created and saved")

    def _generate_baseline_data(self) -> np.ndarray:
        """Generate synthetic baseline data for normal behavior"""
        np.random.seed(42)
        n_samples = 5000

        # Normal user behavior patterns
        features = []

        for i in range(n_samples):
            # User activity patterns (normal behavior)
            login_hour = np.random.normal(10, 3)  # Most logins around 10 AM
            login_hour = max(0, min(23, login_hour))  # Clamp to valid hours

            session_duration = np.random.lognormal(3, 1)  # Log-normal distribution
            session_duration = min(480, session_duration)  # Max 8 hours

            files_accessed = np.random.poisson(5)  # Average 5 files per session
            data_downloaded = np.random.gamma(2, 50)  # MB downloaded
            data_uploaded = np.random.gamma(1, 20)  # MB uploaded

            applications_used = np.random.poisson(3)  # Number of apps
            failed_login_attempts = np.random.poisson(0.1)  # Very few failed logins

            # Location consistency (0-1 score)
            location_consistency = np.random.beta(8, 2)  # Usually consistent

            # Device consistency (0-1 score) 
            device_consistency = np.random.beta(9, 1)  # Very consistent

            # Network patterns
            bandwidth_usage = np.random.gamma(3, 10)  # MB/hour
            connection_count = np.random.poisson(15)  # Network connections

            feature_vector = [
                login_hour,
                session_duration,
                files_accessed,
                data_downloaded,
                data_uploaded,
                applications_used,
                failed_login_attempts,
                location_consistency,
                device_consistency,
                bandwidth_usage,
                connection_count
            ]

            features.append(feature_vector)

        return np.array(features)

    def _create_behavioral_baselines(self, baseline_data: np.ndarray) -> Dict[str, Any]:
        """Create behavioral baselines for different metrics"""
        baselines = {}

        feature_names = [
            'login_hour', 'session_duration', 'files_accessed',
            'data_downloaded', 'data_uploaded', 'applications_used',
            'failed_login_attempts', 'location_consistency', 
            'device_consistency', 'bandwidth_usage', 'connection_count'
        ]

        for i, feature_name in enumerate(feature_names):
            feature_data = baseline_data[:, i]
            baselines[feature_name] = {
                'mean': np.mean(feature_data),
                'std': np.std(feature_data),
                'median': np.median(feature_data),
                'percentile_25': np.percentile(feature_data, 25),
                'percentile_75': np.percentile(feature_data, 75),
                'min': np.min(feature_data),
                'max': np.max(feature_data)
            }

        return baselines

    async def detect(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main anomaly detection function"""
        if not self.is_initialized:
            await self.initialize()

        results = {
            "timestamp": asyncio.get_event_loop().time(),
            "anomaly_detected": False,
            "anomaly_score": 0.0,
            "anomaly_type": "NORMAL",
            "confidence": 0.0,
            "details": {},
            "recommendations": []
        }

        try:
            # Extract features
            features = self._extract_anomaly_features(data)

            # Run different anomaly detection analyses
            if 'user_activity' in data:
                user_result = await self._detect_user_anomalies(data['user_activity'])
                results["details"]["user_behavior"] = user_result

            if 'network_traffic' in data:
                network_result = await self._detect_network_anomalies(data['network_traffic'])
                results["details"]["network"] = network_result

            if 'system_metrics' in data:
                system_result = await self._detect_system_anomalies(data['system_metrics'])
                results["details"]["system"] = system_result

            # Machine learning based detection
            if features is not None:
                ml_result = await self._ml_anomaly_detection(features)
                results["details"]["ml_detection"] = ml_result

            # Combine results
            results = self._combine_anomaly_results(results)

            return results

        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            results["error"] = str(e)
            return results

    def _extract_anomaly_features(self, data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract features for ML-based anomaly detection"""
        try:
            features = [0.0] * 11  # Match baseline feature count

            if 'user_activity' in data:
                activity = data['user_activity']
                features[0] = activity.get('login_hour', 10)
                features[1] = activity.get('session_duration', 60)
                features[2] = activity.get('files_accessed', 5)
                features[3] = activity.get('data_downloaded', 100)
                features[4] = activity.get('data_uploaded', 20)
                features[5] = activity.get('applications_used', 3)
                features[6] = activity.get('failed_login_attempts', 0)
                features[7] = activity.get('location_consistency', 0.9)
                features[8] = activity.get('device_consistency', 0.95)

            if 'network_traffic' in data:
                network = data['network_traffic']
                features[9] = network.get('bandwidth_usage', 30)
                features[10] = network.get('connection_count', 15)

            return np.array(features).reshape(1, -1)

        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return None

    async def _detect_user_anomalies(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect user behavior anomalies"""
        anomalies = []
        severity_score = 0.0

        # Check unusual login times
        login_hour = user_data.get('login_hour', 10)
        if login_hour < 6 or login_hour > 22:
            anomalies.append("Unusual login time")
            severity_score += 0.3

        # Check excessive failed logins
        failed_logins = user_data.get('failed_login_attempts', 0)
        if failed_logins > 5:
            anomalies.append("Excessive failed login attempts")
            severity_score += 0.4

        # Check location inconsistency
        location_consistency = user_data.get('location_consistency', 0.9)
        if location_consistency < 0.5:
            anomalies.append("Unusual geographic access pattern")
            severity_score += 0.3

        # Check device inconsistency
        device_consistency = user_data.get('device_consistency', 0.95)
        if device_consistency < 0.6:
            anomalies.append("Unusual device usage pattern")
            severity_score += 0.2

        # Check data access patterns
        files_accessed = user_data.get('files_accessed', 5)
        baseline_files = self.baselines.get('files_accessed', {}).get('mean', 5)
        if files_accessed > baseline_files * 3:
            anomalies.append("Excessive file access")
            severity_score += 0.4

        return {
            "anomalies": anomalies,
            "severity_score": min(severity_score, 1.0),
            "anomaly_type": "USER_BEHAVIOR_ANOMALY" if anomalies else "NORMAL",
            "details": user_data
        }

    async def _detect_network_anomalies(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect network traffic anomalies"""
        anomalies = []
        severity_score = 0.0

        # Check bandwidth usage
        bandwidth = network_data.get('bandwidth_usage', 30)
        baseline_bandwidth = self.baselines.get('bandwidth_usage', {}).get('mean', 30)
        if bandwidth > baseline_bandwidth * 5:
            anomalies.append("Excessive bandwidth usage")
            severity_score += 0.5

        # Check connection count
        connections = network_data.get('connection_count', 15)
        baseline_connections = self.baselines.get('connection_count', {}).get('mean', 15)
        if connections > baseline_connections * 4:
            anomalies.append("Unusual number of network connections")
            severity_score += 0.4

        # Check for suspicious ports
        suspicious_ports = network_data.get('suspicious_ports', [])
        if suspicious_ports:
            anomalies.append(f"Suspicious port activity: {suspicious_ports}")
            severity_score += 0.6

        return {
            "anomalies": anomalies,
            "severity_score": min(severity_score, 1.0),
            "anomaly_type": "NETWORK_TRAFFIC_ANOMALY" if anomalies else "NORMAL",
            "details": network_data
        }

    async def _detect_system_anomalies(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect system resource anomalies"""
        anomalies = []
        severity_score = 0.0

        # Check CPU usage
        cpu_usage = system_data.get('cpu_usage', 30)
        if cpu_usage > 90:
            anomalies.append("High CPU usage detected")
            severity_score += 0.4

        # Check memory usage
        memory_usage = system_data.get('memory_usage', 50)
        if memory_usage > 95:
            anomalies.append("High memory usage detected")
            severity_score += 0.4

        # Check disk I/O
        disk_io = system_data.get('disk_io', 100)
        if disk_io > 1000:  # High disk I/O
            anomalies.append("Unusual disk I/O activity")
            severity_score += 0.3

        return {
            "anomalies": anomalies,
            "severity_score": min(severity_score, 1.0),
            "anomaly_type": "SYSTEM_RESOURCE_ANOMALY" if anomalies else "NORMAL",
            "details": system_data
        }

    async def _ml_anomaly_detection(self, features: np.ndarray) -> Dict[str, Any]:
        """Machine learning based anomaly detection"""
        try:
            # Scale features
            features_scaled = self.scalers['anomaly'].transform(features)

            # Isolation Forest prediction
            anomaly_score = self.models['isolation_forest'].decision_function(features_scaled)[0]
            is_outlier = self.models['isolation_forest'].predict(features_scaled)[0] == -1

            # Convert anomaly score to 0-1 scale (higher = more anomalous)
            normalized_score = max(0, (-anomaly_score + 0.5) * 2)
            normalized_score = min(1, normalized_score)

            return {
                "is_anomaly": is_outlier,
                "anomaly_score": float(normalized_score),
                "model": "IsolationForest",
                "confidence": float(abs(anomaly_score))
            }

        except Exception as e:
            logger.error(f"ML anomaly detection failed: {str(e)}")
            return {"error": str(e)}

    def _combine_anomaly_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine anomaly detection results"""
        max_severity = 0.0
        primary_anomaly = "NORMAL"
        all_anomalies = []

        for analysis_type, analysis_result in results["details"].items():
            if isinstance(analysis_result, dict):
                severity = analysis_result.get("severity_score", 0)
                if severity > max_severity:
                    max_severity = severity
                    primary_anomaly = analysis_result.get("anomaly_type", "NORMAL")

                if "anomalies" in analysis_result:
                    all_anomalies.extend(analysis_result["anomalies"])

        # Check ML detection
        if "ml_detection" in results["details"]:
            ml_result = results["details"]["ml_detection"]
            if ml_result.get("is_anomaly", False):
                ml_score = ml_result.get("anomaly_score", 0)
                if ml_score > max_severity:
                    max_severity = ml_score
                    primary_anomaly = "BEHAVIORAL_ANOMALY"

        # Set detection threshold
        ANOMALY_THRESHOLD = 0.5

        results["anomaly_detected"] = max_severity > ANOMALY_THRESHOLD
        results["anomaly_type"] = primary_anomaly if results["anomaly_detected"] else "NORMAL"
        results["anomaly_score"] = max_severity
        results["confidence"] = max_severity

        # Add recommendations
        if results["anomaly_detected"]:
            results["recommendations"] = self._generate_anomaly_recommendations(
                primary_anomaly, all_anomalies
            )

        return results

    def _generate_anomaly_recommendations(self, anomaly_type: str, anomalies: List[str]) -> List[str]:
        """Generate recommendations based on detected anomalies"""
        recommendations = []

        if anomaly_type == "USER_BEHAVIOR_ANOMALY":
            recommendations.extend([
                "Review user access logs for this account",
                "Verify user identity through secondary authentication",
                "Check if account credentials have been compromised",
                "Monitor user activity closely for next 24 hours"
            ])

        elif anomaly_type == "NETWORK_TRAFFIC_ANOMALY":
            recommendations.extend([
                "Investigate network traffic patterns",
                "Check for data exfiltration attempts",
                "Review firewall and network access logs",
                "Consider implementing additional network monitoring"
            ])

        elif anomaly_type == "SYSTEM_RESOURCE_ANOMALY":
            recommendations.extend([
                "Investigate system resource usage patterns",
                "Check for malware or unauthorized processes",
                "Review system performance logs",
                "Consider system resource optimization"
            ])

        # Add specific recommendations based on individual anomalies
        if "failed login attempts" in " ".join(anomalies).lower():
            recommendations.append("Implement account lockout policies")

        if "bandwidth" in " ".join(anomalies).lower():
            recommendations.append("Monitor for data exfiltration")

        return list(set(recommendations))  # Remove duplicates

    def is_ready(self) -> bool:
        """Check if anomaly detector is ready"""
        return self.is_initialized and len(self.models) > 0
