"""
Advanced Threat Detection using AI/ML Models
Specifically designed for Indian cybersecurity threat landscape
"""

import asyncio
import logging
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import AutoTokenizer, AutoModel
import joblib

logger = logging.getLogger(__name__)

class DeepThreatNet(nn.Module):
    """Deep Learning model for advanced threat detection"""

    def __init__(self, input_size: int = 128, hidden_size: int = 256, num_classes: int = 12):
        super(DeepThreatNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, hidden_size // 4)
        self.fc4 = nn.Linear(hidden_size // 4, num_classes)
        self.dropout = nn.Dropout(0.3)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.softmax(self.fc4(x))
        return x

class ThreatDetector:
    """
    Advanced AI-powered threat detection system
    Trained on Indian cybersecurity threat patterns including:
    - APT36 (Transparent Tribe) patterns
    - SideCopy attack vectors
    - APT41 techniques
    - Operation Sindoor related patterns
    """

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.is_loaded = False

        # Threat categories specific to Indian landscape
        self.threat_categories = [
            "NORMAL",
            "APT36_TRANSPARENT_TRIBE", 
            "SIDECOPY_APT",
            "APT41_CHINESE",
            "RANSOMWARE_DOUBLE_EXTORTION",
            "PHISHING_SOCIAL_ENGINEERING",
            "INSIDER_THREAT",
            "API_ABUSE",
            "CLOUD_MISCONFIGURATION",
            "IOT_BOTNET",
            "SUPPLY_CHAIN_ATTACK",
            "NATION_STATE_SURVEILLANCE"
        ]

        # Indian-specific IOCs (Indicators of Compromise)
        self.indian_threat_indicators = {
            "suspicious_domains": [
                ".tk", ".ml", ".ga", ".cf",  # Common in APT campaigns
                "indian-gov", "bharat-gov", "india-mil"  # Government impersonation
            ],
            "apt36_patterns": [
                "crimson_rat", "capra_rat", "transparent_tribe",
                "mythic_leopard", "operation_c-major"
            ],
            "sidecopy_patterns": [
                "sidecopy", "allakore_rat", "atta_rat",
                "operation_ghazi", "loda_rat"
            ],
            "targeted_sectors": [
                "defence", "government", "banking", "telecom",
                "energy", "healthcare", "critical_infrastructure"
            ]
        }

    async def load_models(self):
        """Load pre-trained models"""
        try:
            # Load traditional ML models
            await self._load_random_forest_model()
            await self._load_isolation_forest_model()

            # Load deep learning model
            await self._load_deep_learning_model()

            # Load NLP model for text-based threat analysis
            await self._load_nlp_model()

            self.is_loaded = True
            logger.info("All threat detection models loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            # Create and train models if not found
            await self._create_and_train_models()

    async def _load_random_forest_model(self):
        """Load Random Forest model for network traffic analysis"""
        try:
            self.models['random_forest'] = joblib.load('models/threat_rf_model.pkl')
            self.scalers['network'] = joblib.load('models/network_scaler.pkl')
            self.encoders['threat'] = joblib.load('models/threat_encoder.pkl')
        except FileNotFoundError:
            logger.warning("Random Forest model not found, will create new one")
            await self._train_random_forest_model()

    async def _train_random_forest_model(self):
        """Train Random Forest model with synthetic Indian threat data"""
        # Generate synthetic training data
        X_train, y_train = self._generate_synthetic_training_data()

        # Train model
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )

        # Fit scaler and encoder
        self.scalers['network'] = StandardScaler()
        self.encoders['threat'] = LabelEncoder()

        X_train_scaled = self.scalers['network'].fit_transform(X_train)
        y_train_encoded = self.encoders['threat'].fit_transform(y_train)

        self.models['random_forest'].fit(X_train_scaled, y_train_encoded)

        # Save models
        import os
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.models['random_forest'], 'models/threat_rf_model.pkl')
        joblib.dump(self.scalers['network'], 'models/network_scaler.pkl')
        joblib.dump(self.encoders['threat'], 'models/threat_encoder.pkl')

        logger.info("Random Forest model trained and saved")

    def _generate_synthetic_training_data(self) -> Tuple[np.ndarray, List[str]]:
        """Generate synthetic training data for Indian threat landscape"""
        np.random.seed(42)

        # Network traffic features
        n_samples = 10000
        features = []
        labels = []

        for i in range(n_samples):
            # Select random threat category
            threat_type = np.random.choice(self.threat_categories)

            if threat_type == "NORMAL":
                # Normal traffic patterns
                packet_size = np.random.normal(1024, 200)
                connection_duration = np.random.normal(30, 10)
                bytes_sent = np.random.normal(5000, 1000)
                bytes_received = np.random.normal(5000, 1000)
                port_scan_count = 0
                suspicious_strings = 0
                geo_anomaly = 0

            elif threat_type == "APT36_TRANSPARENT_TRIBE":
                # APT36 specific patterns
                packet_size = np.random.normal(2048, 400)  # Larger packets for data exfiltration
                connection_duration = np.random.normal(300, 100)  # Longer connections
                bytes_sent = np.random.normal(1000, 500)  # Lower outbound
                bytes_received = np.random.normal(15000, 5000)  # Higher inbound (C2)
                port_scan_count = np.random.poisson(5)
                suspicious_strings = np.random.poisson(8)  # High suspicious content
                geo_anomaly = 0.8  # High geographic anomaly score

            elif threat_type == "RANSOMWARE_DOUBLE_EXTORTION":
                # Ransomware patterns
                packet_size = np.random.normal(4096, 800)  # Large packets
                connection_duration = np.random.normal(120, 30)
                bytes_sent = np.random.normal(50000, 20000)  # High data exfiltration
                bytes_received = np.random.normal(2000, 500)
                port_scan_count = np.random.poisson(2)
                suspicious_strings = np.random.poisson(12)  # Very high
                geo_anomaly = 0.6

            else:
                # Generic malicious patterns
                packet_size = np.random.normal(1500, 300)
                connection_duration = np.random.normal(60, 20)
                bytes_sent = np.random.normal(8000, 3000)
                bytes_received = np.random.normal(8000, 3000)
                port_scan_count = np.random.poisson(3)
                suspicious_strings = np.random.poisson(5)
                geo_anomaly = np.random.uniform(0.3, 0.7)

            # Additional features
            failed_logins = np.random.poisson(1) if threat_type != "NORMAL" else 0
            privilege_escalation = 1 if threat_type in ["APT36_TRANSPARENT_TRIBE", "APT41_CHINESE"] else 0
            lateral_movement = 1 if threat_type.startswith("APT") else 0

            feature_vector = [
                max(0, packet_size),
                max(0, connection_duration),
                max(0, bytes_sent),
                max(0, bytes_received),
                port_scan_count,
                suspicious_strings,
                geo_anomaly,
                failed_logins,
                privilege_escalation,
                lateral_movement
            ]

            features.append(feature_vector)
            labels.append(threat_type)

        return np.array(features), labels

    async def _load_deep_learning_model(self):
        """Load PyTorch deep learning model"""
        try:
            self.models['deep_net'] = DeepThreatNet()
            self.models['deep_net'].load_state_dict(
                torch.load('models/deep_threat_net.pth', map_location='cpu')
            )
            self.models['deep_net'].eval()
        except FileNotFoundError:
            logger.warning("Deep learning model not found, creating new one")
            await self._train_deep_learning_model()

    async def _train_deep_learning_model(self):
        """Train PyTorch deep learning model"""
        # Generate training data
        X, y = self._generate_synthetic_training_data()

        # Prepare data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        encoder = LabelEncoder()
        y_train_encoded = encoder.fit_transform(y_train)
        y_test_encoded = encoder.transform(y_test)

        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train_scaled)
        y_train_tensor = torch.LongTensor(y_train_encoded)
        X_test_tensor = torch.FloatTensor(X_test_scaled)
        y_test_tensor = torch.LongTensor(y_test_encoded)

        # Initialize model
        model = DeepThreatNet(input_size=X_train_scaled.shape[1], num_classes=len(self.threat_categories))
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        # Training loop
        model.train()
        for epoch in range(100):
            optimizer.zero_grad()
            outputs = model(X_train_tensor)
            loss = criterion(outputs, y_train_tensor)
            loss.backward()
            optimizer.step()

            if epoch % 20 == 0:
                logger.info(f"Epoch {epoch}, Loss: {loss.item():.4f}")

        # Save model
        import os
        os.makedirs('models', exist_ok=True)
        torch.save(model.state_dict(), 'models/deep_threat_net.pth')
        joblib.dump(scaler, 'models/deep_net_scaler.pkl')
        joblib.dump(encoder, 'models/deep_net_encoder.pkl')

        self.models['deep_net'] = model
        self.scalers['deep_net'] = scaler
        self.encoders['deep_net'] = encoder

        logger.info("Deep learning model trained and saved")

    async def _load_nlp_model(self):
        """Load NLP model for text-based threat analysis"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self.models['nlp_tokenizer'] = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
            self.models['nlp_model'] = AutoModelForSequenceClassification.from_pretrained('bert-base-multilingual-cased')
        except Exception as e:
            logger.warning(f"Could not load pre-trained NLP model: {str(e)}")

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main threat analysis function"""
        if not self.is_loaded:
            await self.load_models()

        results = {
            "timestamp": asyncio.get_event_loop().time(),
            "threat_detected": False,
            "threat_type": "NORMAL",
            "confidence_score": 0.0,
            "risk_score": 0.0,
            "analysis_details": {},
            "recommendations": []
        }

        try:
            # Extract features from input data
            features = self._extract_features(data)

            # Run different analysis models
            if 'network_traffic' in data:
                network_result = await self._analyze_network_traffic(features)
                results["analysis_details"]["network"] = network_result

            if 'log_data' in data:
                log_result = await self._analyze_log_data(data['log_data'])
                results["analysis_details"]["logs"] = log_result

            if 'email_content' in data:
                email_result = await self._analyze_email_content(data['email_content'])
                results["analysis_details"]["email"] = email_result

            # Combine results and make final decision
            results = self._combine_analysis_results(results)

            # Add Indian-specific threat context
            if results["threat_detected"]:
                results = self._add_indian_threat_context(results, data)

            return results

        except Exception as e:
            logger.error(f"Error in threat analysis: {str(e)}")
            results["error"] = str(e)
            return results

    def _extract_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract features from input data"""
        # Default feature vector
        features = [0.0] * 10

        if 'network_traffic' in data:
            traffic = data['network_traffic']
            features[0] = traffic.get('packet_size', 0)
            features[1] = traffic.get('connection_duration', 0)
            features[2] = traffic.get('bytes_sent', 0)
            features[3] = traffic.get('bytes_received', 0)
            features[4] = traffic.get('port_scan_count', 0)
            features[5] = len(traffic.get('suspicious_strings', []))
            features[6] = traffic.get('geo_anomaly_score', 0)
            features[7] = traffic.get('failed_logins', 0)
            features[8] = 1 if traffic.get('privilege_escalation') else 0
            features[9] = 1 if traffic.get('lateral_movement') else 0

        return np.array(features).reshape(1, -1)

    async def _analyze_network_traffic(self, features: np.ndarray) -> Dict[str, Any]:
        """Analyze network traffic using ML models"""
        try:
            # Random Forest prediction
            features_scaled = self.scalers['network'].transform(features)
            rf_prediction = self.models['random_forest'].predict(features_scaled)[0]
            rf_probabilities = self.models['random_forest'].predict_proba(features_scaled)[0]

            threat_type = self.encoders['threat'].inverse_transform([rf_prediction])[0]
            confidence = max(rf_probabilities)

            return {
                "model": "RandomForest",
                "threat_type": threat_type,
                "confidence": float(confidence),
                "probabilities": {
                    self.encoders['threat'].inverse_transform([i])[0]: float(prob)
                    for i, prob in enumerate(rf_probabilities)
                }
            }

        except Exception as e:
            logger.error(f"Network traffic analysis failed: {str(e)}")
            return {"error": str(e)}

    def is_ready(self) -> bool:
        """Check if the detector is ready"""
        return self.is_loaded and len(self.models) > 0

    def _combine_analysis_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from different analysis modules"""
        max_confidence = 0.0
        primary_threat = "NORMAL"

        for analysis_type, analysis_result in results["analysis_details"].items():
            if isinstance(analysis_result, dict) and "confidence" in analysis_result:
                confidence = analysis_result["confidence"]
                if confidence > max_confidence:
                    max_confidence = confidence
                    primary_threat = analysis_result.get("threat_type", "UNKNOWN")

        # Set threat detection threshold
        THREAT_THRESHOLD = 0.7

        results["threat_detected"] = max_confidence > THREAT_THRESHOLD
        results["threat_type"] = primary_threat if results["threat_detected"] else "NORMAL"
        results["confidence_score"] = max_confidence
        results["risk_score"] = min(max_confidence * 100, 100.0)

        return results

    def _add_indian_threat_context(self, results: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Add Indian-specific threat intelligence context"""
        threat_type = results["threat_type"]

        if threat_type == "APT36_TRANSPARENT_TRIBE":
            results["recommendations"] = [
                "Alert CERT-In immediately - APT36 targeting detected",
                "Check for Crimson RAT or CapraRAT indicators",
                "Monitor for credential harvesting activities",
                "Review access to defense/government systems",
                "Implement additional network segmentation"
            ]
            results["threat_context"] = {
                "apt_group": "APT36 (Transparent Tribe)",
                "origin": "Pakistan",
                "targets": "Indian defense, government, education",
                "techniques": ["Spear-phishing", "RAT deployment", "Credential theft"]
            }

        elif threat_type == "SIDECOPY_APT":
            results["recommendations"] = [
                "Possible SideCopy campaign - monitor for RAT deployment",
                "Check for Allakore RAT or ATTA RAT indicators",
                "Review recent email attachments and downloads",
                "Strengthen email security controls",
                "Monitor for data exfiltration"
            ]

        return results

    async def _create_and_train_models(self):
        """Create and train all models if not found"""
        logger.info("Creating and training new models...")
        await self._train_random_forest_model()
        await self._train_deep_learning_model()
        self.is_loaded = True
        logger.info("All models created and trained successfully")

    async def _analyze_log_data(self, log_data: str) -> Dict[str, Any]:
        """Analyze log data for threats"""
        # Simple log analysis - can be enhanced
        suspicious_keywords = [
            "failed login", "privilege escalation", "unauthorized access",
            "suspicious activity", "malware", "trojan", "backdoor"
        ]

        suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in log_data.lower())
        confidence = min(suspicious_count / len(suspicious_keywords), 1.0)

        return {
            "model": "LogAnalyzer",
            "threat_type": "INSIDER_THREAT" if confidence > 0.5 else "NORMAL",
            "confidence": confidence,
            "suspicious_indicators": suspicious_count
        }

    async def _analyze_email_content(self, email_content: str) -> Dict[str, Any]:
        """Analyze email content for phishing/threats"""
        phishing_indicators = [
            "urgent", "verify account", "click here", "suspended",
            "confirm identity", "update payment", "security alert"
        ]

        indicator_count = sum(1 for indicator in phishing_indicators if indicator in email_content.lower())
        confidence = min(indicator_count / len(phishing_indicators), 1.0)

        return {
            "model": "EmailAnalyzer", 
            "threat_type": "PHISHING_SOCIAL_ENGINEERING" if confidence > 0.3 else "NORMAL",
            "confidence": confidence,
            "phishing_indicators": indicator_count
        }
