from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from src.core.database import get_db
from src.models.disruption import DisruptionEvent
from src.core.pipeline.supply_chain_pipeline import SupplyChainPipeline
from src.utils.logger import setup_logger
from config.settings import settings

# Import AI endpoints
from src.api.ai_endpoints import router as ai_router
from src.api.pathway_rag_endpoints import router as pathway_rag_router

logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Supply Chain Disruption Predictor",
    description="Real-time supply chain disruption prediction and monitoring system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global pipeline instance
pipeline = SupplyChainPipeline()

# Include AI router
app.include_router(ai_router)

# Include Pathway RAG router
app.include_router(pathway_rag_router)

# Pydantic models for API responses
from pydantic import BaseModel

class DisruptionResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    title: str
    description: Optional[str]
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    confidence_score: Optional[float]
    impact_score: Optional[float]
    source: str
    alert_level: str
    priority_rank: Optional[int]
    affected_routes: List[str]
    mitigation_strategies: List[str]
    financial_impact: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class DashboardStats(BaseModel):
    total_alerts_24h: int
    critical_alerts_24h: int
    active_disruptions: int
    average_confidence: float
    system_health: str
    affected_routes: List[str]

class AlertSummary(BaseModel):
    id: int
    title: str
    severity: str
    location: str
    impact_score: float
    created_at: datetime

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token - simplified for demo"""
    token = credentials.credentials
    if token != "demo_token":  # In production, use proper JWT validation
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supply Chain Disruption Predictor API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "pipeline_status": pipeline.get_status()
    }

@app.get("/api/v1/alerts", response_model=List[DisruptionResponse])
async def get_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    location: Optional[str] = Query(None, description="Filter by location"),
    active_only: bool = Query(True, description="Show only active alerts"),
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get supply chain disruption alerts"""
    try:
        query = db.query(DisruptionEvent)
        
        # Apply filters
        if active_only:
            query = query.filter(DisruptionEvent.is_active == True)
        
        if severity:
            query = query.filter(DisruptionEvent.severity == severity)
        
        if location:
            query = query.filter(DisruptionEvent.location.ilike(f"%{location}%"))
        
        # Order by priority and creation time
        query = query.order_by(
            DisruptionEvent.priority_rank.asc(),
            DisruptionEvent.created_at.desc()
        )
        
        # Pagination
        offset = (page - 1) * page_size
        alerts = query.offset(offset).limit(page_size).all()
        
        # Convert to response format
        response_alerts = []
        for alert in alerts:
            response_alerts.append(DisruptionResponse(
                id=alert.id,
                event_type=alert.event_type,
                severity=alert.severity,
                title=alert.title,
                description=alert.description,
                location=alert.location,
                latitude=alert.latitude,
                longitude=alert.longitude,
                confidence_score=alert.confidence_score,
                impact_score=alert.impact_score,
                source=alert.source,
                alert_level=alert.alert_level,
                priority_rank=alert.priority_rank,
                affected_routes=json.loads(alert.affected_routes) if alert.affected_routes else [],
                mitigation_strategies=json.loads(alert.mitigation_strategies) if alert.mitigation_strategies else [],
                financial_impact=json.loads(alert.financial_impact) if alert.financial_impact else {},
                is_active=alert.is_active,
                created_at=alert.created_at,
                updated_at=alert.updated_at
            ))
        
        return response_alerts
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/alerts/{alert_id}", response_model=DisruptionResponse)
async def get_alert_by_id(
    alert_id: int,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get specific alert by ID"""
    try:
        alert = db.query(DisruptionEvent).filter(DisruptionEvent.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return DisruptionResponse(
            id=alert.id,
            event_type=alert.event_type,
            severity=alert.severity,
            title=alert.title,
            description=alert.description,
            location=alert.location,
            latitude=alert.latitude,
            longitude=alert.longitude,
            confidence_score=alert.confidence_score,
            impact_score=alert.impact_score,
            source=alert.source,
            alert_level=alert.alert_level,
            priority_rank=alert.priority_rank,
            affected_routes=json.loads(alert.affected_routes) if alert.affected_routes else [],
            mitigation_strategies=json.loads(alert.mitigation_strategies) if alert.mitigation_strategies else [],
            financial_impact=json.loads(alert.financial_impact) if alert.financial_impact else {},
            is_active=alert.is_active,
            created_at=alert.created_at,
            updated_at=alert.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        # Calculate stats for last 24 hours
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Total alerts in last 24 hours
        total_alerts_24h = db.query(DisruptionEvent).filter(
            DisruptionEvent.created_at >= twenty_four_hours_ago
        ).count()
        
        # Critical alerts in last 24 hours
        critical_alerts_24h = db.query(DisruptionEvent).filter(
            DisruptionEvent.created_at >= twenty_four_hours_ago,
            DisruptionEvent.severity == "critical"
        ).count()
        
        # Active disruptions
        active_disruptions = db.query(DisruptionEvent).filter(
            DisruptionEvent.is_active == True
        ).count()
        
        # Average confidence score
        avg_confidence_result = db.query(
            db.func.avg(DisruptionEvent.confidence_score)
        ).filter(
            DisruptionEvent.created_at >= twenty_four_hours_ago
        ).scalar()
        
        average_confidence = float(avg_confidence_result) if avg_confidence_result else 0.0
        
        # Get affected routes from recent alerts
        recent_alerts = db.query(DisruptionEvent).filter(
            DisruptionEvent.created_at >= twenty_four_hours_ago,
            DisruptionEvent.affected_routes.isnot(None)
        ).all()
        
        affected_routes = set()
        for alert in recent_alerts:
            if alert.affected_routes:
                routes = json.loads(alert.affected_routes)
                affected_routes.update(routes)
        
        # Determine system health
        system_health = "healthy"
        if critical_alerts_24h > 5:
            system_health = "critical"
        elif critical_alerts_24h > 2 or total_alerts_24h > 20:
            system_health = "warning"
        
        return DashboardStats(
            total_alerts_24h=total_alerts_24h,
            critical_alerts_24h=critical_alerts_24h,
            active_disruptions=active_disruptions,
            average_confidence=round(average_confidence, 3),
            system_health=system_health,
            affected_routes=list(affected_routes)
        )
        
    except Exception as e:
        logger.error(f"Error calculating dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/alerts/summary", response_model=List[AlertSummary])
async def get_alerts_summary(
    limit: int = Query(10, ge=1, le=50, description="Number of recent alerts"),
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get summary of recent alerts"""
    try:
        alerts = db.query(DisruptionEvent).filter(
            DisruptionEvent.is_active == True
        ).order_by(
            DisruptionEvent.priority_rank.asc(),
            DisruptionEvent.created_at.desc()
        ).limit(limit).all()
        
        return [
            AlertSummary(
                id=alert.id,
                title=alert.title,
                severity=alert.severity,
                location=alert.location or "Unknown",
                impact_score=alert.impact_score or 0.0,
                created_at=alert.created_at
            )
            for alert in alerts
        ]
        
    except Exception as e:
        logger.error(f"Error fetching alerts summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/pipeline/start")
async def start_pipeline(token: str = Depends(verify_token)):
    """Start the data processing pipeline"""
    try:
        if pipeline.is_running:
            return {"message": "Pipeline is already running", "status": "running"}
        
        pipeline.start()
        return {"message": "Pipeline started successfully", "status": "running"}
        
    except Exception as e:
        logger.error(f"Error starting pipeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to start pipeline")

@app.post("/api/v1/pipeline/stop")
async def stop_pipeline(token: str = Depends(verify_token)):
    """Stop the data processing pipeline"""
    try:
        if not pipeline.is_running:
            return {"message": "Pipeline is already stopped", "status": "stopped"}
        
        pipeline.stop()
        return {"message": "Pipeline stopped successfully", "status": "stopped"}
        
    except Exception as e:
        logger.error(f"Error stopping pipeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop pipeline")

@app.get("/api/v1/pipeline/status")
async def get_pipeline_status(token: str = Depends(verify_token)):
    """Get pipeline status"""
    try:
        return pipeline.get_status()
    except Exception as e:
        logger.error(f"Error getting pipeline status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pipeline status")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting Supply Chain Disruption Predictor API")
    
    # Start the pipeline automatically
    try:
        pipeline.start()
        logger.info("Pipeline started automatically on startup")
    except Exception as e:
        logger.error(f"Failed to start pipeline on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down Supply Chain Disruption Predictor API")
    
    # Stop the pipeline
    try:
        pipeline.stop()
        logger.info("Pipeline stopped on shutdown")
    except Exception as e:
        logger.error(f"Error stopping pipeline on shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 