from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.sql import func
from src.core.database import Base

class DisruptionEvent(Base):
    __tablename__ = "disruption_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    confidence_score = Column(Float)
    impact_score = Column(Float)
    source = Column(String(50))
    alert_level = Column(String(20))
    priority_rank = Column(Integer)
    affected_routes = Column(Text)  # JSON string of affected routes
    mitigation_strategies = Column(Text)  # JSON string of strategies
    financial_impact = Column(Text)  # JSON string of financial estimates
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DisruptionEvent(id={self.id}, type={self.event_type}, severity={self.severity})>" 