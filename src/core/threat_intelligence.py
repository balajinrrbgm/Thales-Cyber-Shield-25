"""
Threat Intelligence Engine for Thales Cyber Shield
Integrates with CERT-In and other threat intelligence sources
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ThreatIndicator:
    """Threat intelligence indicator"""
    indicator_type: str  # IP, DOMAIN, HASH, URL
    indicator_value: str
    threat_type: str
    confidence: str  # LOW, MEDIUM, HIGH
    source: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str]
    context: Dict[str, Any]

class ThreatIntelligenceEngine:
    """
    Advanced threat intelligence engine
    Integrates with multiple sources for comprehensive threat awareness
    """

    def __init__(self):
        self.sources = {
            "cert_in": CERTInFeed(),
            "abuse_ch": AbuseCHFeed(),
            "virustotal": VirusTotalFeed(),
            "internal": InternalThreatFeed()
        }
        self.indicators = {}
        self.running = False
        self.update_interval = 300  # 5 minutes

    async def start(self):
        """Start threat intelligence collection"""
        self.running = True
        asyncio.create_task(self._update_loop())
        logger.info("Threat intelligence engine started")

    async def stop(self):
        """Stop threat intelligence collection"""
        self.running = False
        logger.info("Threat intelligence engine stopped")

    async def _update_loop(self):
        """Main update loop for threat intelligence"""
        while self.running:
            try:
                await self._update_all_feeds()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in threat intelligence update: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _update_all_feeds(self):
        """Update all threat intelligence feeds"""
        tasks = []
        for source_name, source in self.sources.items():
            tasks.append(self._update_source(source_name, source))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _update_source(self, source_name: str, source):
        """Update single threat intelligence source"""
        try:
            indicators = await source.get_indicators()
            for indicator in indicators:
                key = f"{indicator.indicator_type}:{indicator.indicator_value}"
                self.indicators[key] = indicator

            logger.info(f"Updated {len(indicators)} indicators from {source_name}")

        except Exception as e:
            logger.error(f"Failed to update {source_name}: {str(e)}")

    async def lookup_indicator(self, indicator_type: str, indicator_value: str) -> Optional[ThreatIndicator]:
        """Lookup threat indicator"""
        key = f"{indicator_type}:{indicator_value}"
        return self.indicators.get(key)

    async def enrich_threat_data(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich threat data with intelligence"""
        enriched = threat_data.copy()
        enriched["threat_intelligence"] = {}

        # Look up IP addresses
        if "source_ip" in threat_data:
            ip_intel = await self.lookup_indicator("IP", threat_data["source_ip"])
            if ip_intel:
                enriched["threat_intelligence"]["source_ip"] = {
                    "threat_type": ip_intel.threat_type,
                    "confidence": ip_intel.confidence,
                    "source": ip_intel.source,
                    "tags": ip_intel.tags
                }

        # Look up domains
        if "domain" in threat_data:
            domain_intel = await self.lookup_indicator("DOMAIN", threat_data["domain"])
            if domain_intel:
                enriched["threat_intelligence"]["domain"] = {
                    "threat_type": domain_intel.threat_type,
                    "confidence": domain_intel.confidence,
                    "source": domain_intel.source,
                    "tags": domain_intel.tags
                }

        # Look up file hashes
        if "file_hash" in threat_data:
            hash_intel = await self.lookup_indicator("HASH", threat_data["file_hash"])
            if hash_intel:
                enriched["threat_intelligence"]["file_hash"] = {
                    "threat_type": hash_intel.threat_type,
                    "confidence": hash_intel.confidence,
                    "source": hash_intel.source,
                    "tags": hash_intel.tags
                }

        return enriched

    async def process_incident(self, raw_data: Dict[str, Any], analysis_result: Dict[str, Any]):
        """Process incident and update threat intelligence"""
        try:
            # Extract indicators from incident
            indicators = self._extract_indicators(raw_data)

            # Add to internal threat feed
            for indicator in indicators:
                await self.sources["internal"].add_indicator(indicator)

            # Update threat intelligence database
            from src.core.database import DatabaseManager
            await DatabaseManager.update_threat_intelligence(
                [indicator.__dict__ for indicator in indicators]
            )

        except Exception as e:
            logger.error(f"Failed to process incident: {str(e)}")

    def _extract_indicators(self, raw_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Extract threat indicators from raw data"""
        indicators = []

        if "network_traffic" in raw_data:
            traffic = raw_data["network_traffic"]

            # Extract IP indicators
            if "source_ip" in traffic:
                indicators.append(ThreatIndicator(
                    indicator_type="IP",
                    indicator_value=traffic["source_ip"],
                    threat_type="SUSPICIOUS_IP",
                    confidence="MEDIUM",
                    source="internal",
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    tags=["network_traffic"],
                    context={"traffic_data": traffic}
                ))

        return indicators

    def is_running(self) -> bool:
        """Check if engine is running"""
        return self.running

class CERTInFeed:
    """CERT-In threat intelligence feed"""

    def __init__(self):
        self.base_url = "https://www.cert-in.org.in"
        self.api_key = None  # Would be configured

    async def get_indicators(self) -> List[ThreatIndicator]:
        """Get indicators from CERT-In"""
        # Mock data - would integrate with actual CERT-In API
        return [
            ThreatIndicator(
                indicator_type="IP",
                indicator_value="203.0.113.100",
                threat_type="APT36_C2",
                confidence="HIGH",
                source="cert_in",
                first_seen=datetime.utcnow() - timedelta(days=1),
                last_seen=datetime.utcnow(),
                tags=["apt36", "c2", "india_targeted"],
                context={"cert_in_id": "CERT-IN-2025-001"}
            )
        ]

class AbuseCHFeed:
    """Abuse.ch threat intelligence feed"""

    async def get_indicators(self) -> List[ThreatIndicator]:
        """Get indicators from Abuse.ch"""
        indicators = []

        try:
            # Feodo Tracker - Banking Trojans C&C
            async with aiohttp.ClientSession() as session:
                # Mock implementation - would use real API
                indicators.append(ThreatIndicator(
                    indicator_type="IP",
                    indicator_value="198.51.100.100",
                    threat_type="BANKING_TROJAN_C2",
                    confidence="HIGH",
                    source="abuse_ch_feodo",
                    first_seen=datetime.utcnow() - timedelta(hours=6),
                    last_seen=datetime.utcnow(),
                    tags=["banking_trojan", "c2"],
                    context={"malware_family": "Emotet"}
                ))

        except Exception as e:
            logger.error(f"Failed to fetch Abuse.ch indicators: {str(e)}")

        return indicators

class VirusTotalFeed:
    """VirusTotal threat intelligence feed"""

    def __init__(self):
        self.api_key = None  # Would be configured

    async def get_indicators(self) -> List[ThreatIndicator]:
        """Get indicators from VirusTotal"""
        # Mock implementation - would integrate with VT API
        return [
            ThreatIndicator(
                indicator_type="HASH",
                indicator_value="d41d8cd98f00b204e9800998ecf8427e",
                threat_type="MALWARE",
                confidence="HIGH",
                source="virustotal",
                first_seen=datetime.utcnow() - timedelta(days=2),
                last_seen=datetime.utcnow(),
                tags=["malware", "trojan"],
                context={"detection_ratio": "45/70"}
            )
        ]

class InternalThreatFeed:
    """Internal threat intelligence feed"""

    def __init__(self):
        self.internal_indicators = []

    async def get_indicators(self) -> List[ThreatIndicator]:
        """Get internal indicators"""
        return self.internal_indicators

    async def add_indicator(self, indicator: ThreatIndicator):
        """Add indicator to internal feed"""
        self.internal_indicators.append(indicator)

        # Keep only recent indicators (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        self.internal_indicators = [
            ind for ind in self.internal_indicators 
            if ind.last_seen > cutoff_date
        ]

# Regional threat intelligence specific to India
class IndianThreatLandscape:
    """Indian-specific threat landscape analysis"""

    @staticmethod
    def get_apt_groups() -> Dict[str, Dict[str, Any]]:
        """Get APT groups targeting India"""
        return {
            "APT36": {
                "name": "APT36 (Transparent Tribe)",
                "origin": "Pakistan", 
                "targets": ["Indian government", "military", "education"],
                "techniques": ["Spear-phishing", "RAT deployment", "Credential harvesting"],
                "malware": ["Crimson RAT", "CapraRAT"],
                "active": True,
                "threat_level": "HIGH"
            },
            "SideCopy": {
                "name": "SideCopy",
                "origin": "Pakistan",
                "targets": ["Indian government", "military"],
                "techniques": ["Spear-phishing", "RAT deployment"],
                "malware": ["Allakore RAT", "ATTA RAT"],
                "active": True,
                "threat_level": "HIGH"
            },
            "APT41": {
                "name": "APT41",
                "origin": "China",
                "targets": ["Healthcare", "Telecom", "Government"],
                "techniques": ["Supply chain attacks", "Zero-day exploits"],
                "malware": ["Custom backdoors", "MESSAGETAP"],
                "active": True,
                "threat_level": "CRITICAL"
            }
        }

    @staticmethod
    def get_targeted_sectors() -> List[Dict[str, Any]]:
        """Get sectors commonly targeted in India"""
        return [
            {"sector": "Government", "risk_level": "CRITICAL", "common_attacks": ["APT", "Espionage"]},
            {"sector": "Defense", "risk_level": "CRITICAL", "common_attacks": ["APT", "Data theft"]},
            {"sector": "Banking", "risk_level": "HIGH", "common_attacks": ["Ransomware", "Financial fraud"]},
            {"sector": "Healthcare", "risk_level": "HIGH", "common_attacks": ["Ransomware", "Data breach"]},
            {"sector": "Energy", "risk_level": "HIGH", "common_attacks": ["Sabotage", "Espionage"]},
            {"sector": "Telecommunications", "risk_level": "MEDIUM", "common_attacks": ["Espionage", "Service disruption"]}
        ]
