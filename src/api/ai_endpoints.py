"""
AI-Powered API Endpoints for Supply Chain Intelligence
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from src.services.ai_analysis_service import AIAnalysisService
from src.core.detectors.ai_disruption_detector import AIDisruptionDetector
from src.core.rag.vector_store import vector_store
from src.auth.jwt_auth import get_current_user
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Intelligence"])

# Initialize AI services
ai_analysis_service = AIAnalysisService()
ai_detector = AIDisruptionDetector()

@router.post("/analyze/disruptions")
async def analyze_disruptions_ai(
    data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    AI-powered disruption analysis with RAG capabilities
    """
    try:
        events = data.get("events", [])
        if not events:
            raise HTTPException(status_code=400, detail="No events provided for analysis")
        
        # Run AI disruption detection
        disruptions = await ai_detector.detect_disruptions_ai(events)
        
        # Generate comprehensive AI report
        report = await ai_analysis_service.generate_supply_chain_report(disruptions)
        
        # Add disruptions to vector store for future RAG
        for disruption in disruptions:
            vector_store.add_disruption_event(disruption)
        
        return {
            "status": "success",
            "analysis_type": "ai_powered",
            "processed_events": len(events),
            "detected_disruptions": len(disruptions),
            "report": report,
            "ai_features_used": [
                "semantic_analysis",
                "rag_context_retrieval", 
                "llm_insights",
                "predictive_modeling"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in AI disruption analysis: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/predict/event-impact")
async def predict_event_impact(
    event_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Get AI prediction for specific event impact
    """
    try:
        # Validate input
        required_fields = ["title", "description", "location"]
        missing_fields = [field for field in required_fields if not event_data.get(field)]
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {missing_fields}"
            )
        
        # Get AI prediction
        prediction = await ai_analysis_service.get_event_prediction(event_data)
        
        # Get supply chain insights
        insights = ai_detector.get_supply_chain_insights(
            event_data.get("location", ""),
            event_data.get("event_type", "")
        )
        
        return {
            "status": "success",
            "event": event_data,
            "ai_prediction": prediction,
            "supply_chain_insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in event impact prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/insights/supply-chain")
async def get_supply_chain_insights(
    location: Optional[str] = None,
    sector: Optional[str] = None,
    timeframe: Optional[str] = "7d",
    current_user: Dict = Depends(get_current_user)
):
    """
    Get AI-powered supply chain insights for specific location/sector
    """
    try:
        # Build search query
        query_parts = []
        if location:
            query_parts.append(f"location: {location}")
        if sector:
            query_parts.append(f"sector: {sector}")
        
        query = " ".join(query_parts) if query_parts else "supply chain disruption"
        
        # Search vector store for relevant insights
        relevant_docs = vector_store.search(query, k=5, threshold=0.3)
        
        # Get historical patterns
        historical_events = []
        if location:
            # Search for historical events in this location
            location_query = f"location: {location} disruption"
            historical_events = vector_store.search(location_query, k=3, threshold=0.4)
        
        # Organize insights
        insights = {
            "location": location,
            "sector": sector,
            "timeframe": timeframe,
            "relevant_knowledge": relevant_docs,
            "historical_patterns": historical_events,
            "risk_factors": [],
            "recommendations": []
        }
        
        # Extract risk factors from relevant documents
        for doc in relevant_docs:
            metadata = doc["metadata"]
            if metadata.get("type") in ["port_info", "sector_info", "waterway_info"]:
                insights["risk_factors"].append({
                    "factor": metadata.get("type", "unknown"),
                    "importance": metadata.get("importance", 0),
                    "description": doc["document"][:200] + "..."
                })
        
        return {
            "status": "success",
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting supply chain insights: {e}")
        raise HTTPException(status_code=500, detail=f"Insights retrieval failed: {str(e)}")

@router.get("/knowledge-base/search")
async def search_knowledge_base(
    query: str,
    limit: int = 5,
    threshold: float = 0.3,
    current_user: Dict = Depends(get_current_user)
):
    """
    Search the supply chain knowledge base using semantic search
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        # Perform semantic search
        results = vector_store.search(query, k=limit, threshold=threshold)
        
        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "results": results,
            "search_metadata": {
                "threshold": threshold,
                "limit": limit,
                "search_type": "semantic_similarity"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/knowledge-base/add")
async def add_to_knowledge_base(
    document_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Add new document to the supply chain knowledge base
    """
    try:
        # Validate input
        if not document_data.get("content"):
            raise HTTPException(status_code=400, detail="Document content is required")
        
        content = document_data["content"]
        metadata = document_data.get("metadata", {})
        
        # Add to vector store
        doc_id = vector_store.add_document(content, metadata)
        
        if doc_id == -1:
            raise HTTPException(status_code=500, detail="Failed to add document to knowledge base")
        
        return {
            "status": "success",
            "document_id": doc_id,
            "message": "Document added to knowledge base successfully",
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

@router.get("/knowledge-base/stats")
async def get_knowledge_base_stats(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get statistics about the knowledge base
    """
    try:
        stats = vector_store.get_stats()
        
        return {
            "status": "success",
            "knowledge_base_stats": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@router.post("/analyze/similar-events")
async def find_similar_events(
    event_data: Dict[str, Any],
    limit: int = 5,
    current_user: Dict = Depends(get_current_user)
):
    """
    Find similar historical events using AI similarity matching
    """
    try:
        # Get similar historical events
        similar_events = vector_store.get_similar_historical_events(
            {"source_data": event_data}, 
            k=limit
        )
        
        # If no historical events found, search general knowledge
        if not similar_events:
            query = f"{event_data.get('title', '')} {event_data.get('description', '')} {event_data.get('location', '')}"
            similar_events = vector_store.search(query.strip(), k=limit, threshold=0.3)
        
        return {
            "status": "success",
            "query_event": event_data,
            "similar_events_count": len(similar_events),
            "similar_events": similar_events,
            "analysis_type": "semantic_similarity"
        }
        
    except Exception as e:
        logger.error(f"Error finding similar events: {e}")
        raise HTTPException(status_code=500, detail=f"Similar events search failed: {str(e)}")

@router.post("/generate/report")
async def generate_ai_report(
    report_config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate comprehensive AI-powered supply chain report
    """
    try:
        # Get disruptions from request or recent data
        disruptions = report_config.get("disruptions", [])
        
        if not disruptions:
            # If no disruptions provided, this would typically fetch recent ones from database
            # For now, return empty report
            report = await ai_analysis_service.generate_supply_chain_report([])
        else:
            report = await ai_analysis_service.generate_supply_chain_report(disruptions)
        
        # Add background task to save report if needed
        background_tasks.add_task(
            _save_report_background,
            report,
            current_user.get("user_id", "unknown")
        )
        
        return {
            "status": "success",
            "report": report,
            "ai_features": [
                "pattern_analysis",
                "risk_assessment", 
                "predictive_insights",
                "actionable_recommendations"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating AI report: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/health/ai-services")
async def check_ai_services_health():
    """
    Check health status of AI services
    """
    try:
        health_status = {
            "ai_analysis_service": "operational",
            "ai_disruption_detector": "operational", 
            "vector_store": "operational",
            "openai_integration": "unknown",
            "embedding_model": "unknown"
        }
        
        # Check OpenAI integration
        if ai_analysis_service.openai_client:
            health_status["openai_integration"] = "operational"
        else:
            health_status["openai_integration"] = "disabled"
        
        # Check embedding model
        try:
            test_embedding = ai_detector.embedding_model.encode(["test"])
            health_status["embedding_model"] = "operational"
        except:
            health_status["embedding_model"] = "error"
        
        # Check vector store
        try:
            stats = vector_store.get_stats()
            health_status["vector_store"] = f"operational ({stats['total_documents']} docs)"
        except:
            health_status["vector_store"] = "error"
        
        overall_status = "healthy" if all(
            status in ["operational", "disabled"] or "operational" in status
            for status in health_status.values()
        ) else "degraded"
        
        return {
            "status": overall_status,
            "ai_services": health_status,
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking AI services health: {e}")
        return {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat()
        }

async def _save_report_background(report: Dict[str, Any], user_id: str):
    """Background task to save generated report"""
    try:
        # This would typically save to database
        logger.info(f"Report generated for user {user_id} at {report.get('generated_at')}")
    except Exception as e:
        logger.error(f"Error saving report in background: {e}") 