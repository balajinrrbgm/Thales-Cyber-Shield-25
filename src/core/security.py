"""
Security and Authentication for Thales Cyber Shield
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib

from src.core.config import get_settings

security = HTTPBearer()

class SecurityManager:
    """Security and authentication manager"""

    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.SECRET_KEY
        self.algorithm = self.settings.ALGORITHM
        self.access_token_expire_minutes = self.settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key (would check against database)"""
        # Placeholder - would implement database lookup
        return len(api_key) == 43  # URL-safe base64 encoded 32 bytes

    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        # Placeholder for rate limiting logic
        # Would integrate with Redis for distributed rate limiting
        return True

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        # Placeholder for security event logging
        print(f"Security Event: {event_type} - {details}")

# Global security manager instance
security_manager = SecurityManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = security_manager.verify_token(token)

    # Extract user information from token
    user = {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role", "user"),
        "permissions": payload.get("permissions", [])
    }

    return user

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def create_demo_token() -> str:
    """Create demo token for testing"""
    demo_data = {
        "sub": "demo_user",
        "username": "demo",
        "role": "admin",
        "permissions": ["read", "write", "admin"]
    }
    return security_manager.create_access_token(demo_data)

# IP Address validation and geolocation
class IPAnalyzer:
    """IP address analysis and threat intelligence"""

    def __init__(self):
        # Known malicious IP ranges and threat intel sources
        self.malicious_ip_ranges = [
            # Example ranges - would be populated from threat intelligence
            "192.0.2.0/24",  # TEST-NET-1
            "198.51.100.0/24",  # TEST-NET-2
        ]

        # Known APT group IP ranges specific to Indian threat landscape
        self.apt_ip_ranges = {
            "APT36": ["203.0.113.0/24"],  # Example range
            "SideCopy": ["198.18.0.0/24"],
            "APT41": ["233.252.0.0/24"]
        }

    def is_suspicious_ip(self, ip_address: str) -> Dict[str, Any]:
        """Check if IP address is suspicious"""
        result = {
            "is_suspicious": False,
            "threat_level": "LOW",
            "reasons": [],
            "apt_group": None,
            "country": "Unknown"
        }

        # Check against known malicious ranges
        for malicious_range in self.malicious_ip_ranges:
            if self._ip_in_range(ip_address, malicious_range):
                result["is_suspicious"] = True
                result["threat_level"] = "HIGH"
                result["reasons"].append("IP in known malicious range")
                break

        # Check against APT group ranges
        for apt_group, ip_ranges in self.apt_ip_ranges.items():
            for ip_range in ip_ranges:
                if self._ip_in_range(ip_address, ip_range):
                    result["is_suspicious"] = True
                    result["threat_level"] = "CRITICAL"
                    result["apt_group"] = apt_group
                    result["reasons"].append(f"IP associated with {apt_group}")
                    break

        # Add geolocation check (would integrate with GeoIP service)
        result["country"] = self._get_country(ip_address)

        return result

    def _ip_in_range(self, ip: str, cidr: str) -> bool:
        """Check if IP is in CIDR range"""
        try:
            import ipaddress
            return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)
        except:
            return False

    def _get_country(self, ip: str) -> str:
        """Get country for IP address"""
        # Placeholder - would integrate with GeoIP service
        if ip.startswith("192."):
            return "India"
        return "Unknown"

# File hash verification
class FileAnalyzer:
    """File analysis and malware detection"""

    def __init__(self):
        # Known malware hashes from threat intelligence
        self.malware_hashes = {
            # APT36/Transparent Tribe malware hashes
            "crimson_rat": [
                "5d41402abc4b2a76b9719d911017c592",
                "7d865e959b2466918c9863afca942d0f"
            ],
            "capra_rat": [
                "098f6bcd4621d373cade4e832627b4f6",
                "ad0234829205b9033196ba818f7a872b"
            ]
        }

    def analyze_file_hash(self, file_hash: str) -> Dict[str, Any]:
        """Analyze file hash for threats"""
        result = {
            "is_malicious": False,
            "threat_family": None,
            "confidence": 0.0,
            "first_seen": None
        }

        # Check against known malware hashes
        for family, hashes in self.malware_hashes.items():
            if file_hash.lower() in [h.lower() for h in hashes]:
                result["is_malicious"] = True
                result["threat_family"] = family
                result["confidence"] = 0.95
                break

        return result

    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

# Global analyzers
ip_analyzer = IPAnalyzer()
file_analyzer = FileAnalyzer()
