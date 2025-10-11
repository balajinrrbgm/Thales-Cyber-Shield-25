"""
Database models and initialization for Thales Cyber Shield
"""

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

from src.core.config import get_settings

Base = declarative_base()

class ThreatIncident(Base):
    """Threat incident model"""
    __tablename__ = "threat_incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    threat_type = Column(String, index=True)
    severity = Column(String, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    source_ip = Column(String, index=True)
    target_ip = Column(String, index=True)
    description = Column(Text)
    raw_data = Column(JSON)
    analysis_result = Column(JSON)
    status = Column(String, default="OPEN")  # OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    assigned_to = Column(String)
    tags = Column(JSON)
    confidence_score = Column(Float)
    false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnomalyEvent(Base):
    """Anomaly event model"""
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    anomaly_type = Column(String, index=True)
    anomaly_score = Column(Float, index=True)
    entity_id = Column(String, index=True)  # user_id, device_id, etc.
    entity_type = Column(String, index=True)  # USER, DEVICE, NETWORK, etc.
    baseline_data = Column(JSON)
    current_data = Column(JSON)
    deviation_metrics = Column(JSON)
    is_confirmed = Column(Boolean, default=None)
    investigation_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ThreatIntelligence(Base):
    """Threat intelligence indicators"""
    __tablename__ = "threat_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String, unique=True, index=True)
    indicator_type = Column(String, index=True)  # IP, DOMAIN, HASH, URL, etc.
    indicator_value = Column(String, index=True)
    threat_type = Column(String, index=True)
    confidence_level = Column(String, index=True)  # LOW, MEDIUM, HIGH
    source = Column(String, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON)
    context = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserActivity(Base):
    """User activity tracking for behavioral analysis"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    activity_type = Column(String, index=True)
    resource_accessed = Column(String)
    ip_address = Column(String, index=True)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    risk_score = Column(Float, default=0.0)
    geolocation = Column(JSON)
    device_fingerprint = Column(JSON)
    additional_data = Column(JSON)

# Database engine and session
engine = None
AsyncSessionLocal = None
redis_client = None

async def init_db():
    """Initialize database connection and create tables"""
    global engine, AsyncSessionLocal, redis_client

    settings = get_settings()

    # PostgreSQL connection
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Redis connection for caching and real-time data
    redis_client = redis.from_url(settings.REDIS_URL)

    print("Database and Redis connections initialized")

async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis():
    """Get Redis client"""
    return redis_client

class DatabaseManager:
    """Database operations manager"""

    @staticmethod
    async def save_threat_incident(incident_data: Dict[str, Any]) -> ThreatIncident:
        """Save threat incident to database"""
        async with AsyncSessionLocal() as session:
            incident = ThreatIncident(**incident_data)
            session.add(incident)
            await session.commit()
            await session.refresh(incident)
            return incident

    @staticmethod
    async def save_anomaly_event(anomaly_data: Dict[str, Any]) -> AnomalyEvent:
        """Save anomaly event to database"""
        async with AsyncSessionLocal() as session:
            event = AnomalyEvent(**anomaly_data)
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event

    @staticmethod
    async def get_recent_threats(limit: int = 100) -> List[ThreatIncident]:
        """Get recent threat incidents"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ThreatIncident)
                .order_by(ThreatIncident.timestamp.desc())
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def update_threat_intelligence(indicators: List[Dict[str, Any]]):
        """Update threat intelligence indicators"""
        async with AsyncSessionLocal() as session:
            for indicator_data in indicators:
                # Check if indicator exists
                from sqlalchemy import select
                result = await session.execute(
                    select(ThreatIntelligence)
                    .where(ThreatIntelligence.indicator_value == indicator_data["indicator_value"])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing
                    for key, value in indicator_data.items():
                        setattr(existing, key, value)
                    existing.last_seen = datetime.utcnow()
                else:
                    # Create new
                    indicator = ThreatIntelligence(**indicator_data)
                    session.add(indicator)

            await session.commit()

# Cache operations
class CacheManager:
    """Redis cache operations"""

    @staticmethod
    async def set(key: str, value: Any, expire: int = 3600):
        """Set cache value"""
        import json
        await redis_client.set(key, json.dumps(value), ex=expire)

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get cache value"""
        import json
        value = await redis_client.get(key)
        return json.loads(value) if value else None

    @staticmethod
    async def delete(key: str):
        """Delete cache key"""
        await redis_client.delete(key)

    @staticmethod
    async def publish(channel: str, message: Any):
        """Publish message to Redis channel"""
        import json
        await redis_client.publish(channel, json.dumps(message))
