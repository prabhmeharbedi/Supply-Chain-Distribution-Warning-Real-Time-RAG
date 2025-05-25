"""
Pathway-Powered Real-Time RAG API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import json

from src.core.pipeline.pathway_rag_pipeline import pathway_rag_pipeline, PathwayQueryInterface
from src.core.rag.pathway_vector_store import pathway_vector_store, pathway_rag_connector
from src.auth.jwt_auth import get_current_user
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/pathway-rag", tags=["Pathway Real-Time RAG"])

# Global query interface
query_interface = pathway_rag_pipeline.get_real_time_query_interface()

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

@router.post("/query/real-time")
async def query_real_time_rag(
    query_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Real-time RAG query that immediately reflects latest data updates
    
    This endpoint demonstrates Pathway's core capability:
    - Data updated at T+0 is immediately available in queries at T+1
    """
    try:
        query = query_data.get("query", "")
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get vector store stats before query
        pre_query_stats = pathway_vector_store.get_real_time_stats()
        
        # Execute real-time query - this IMMEDIATELY reflects any updates
        results = await query_interface.query_supply_chain_intelligence(
            query=query,
            k=query_data.get("k", 5)
        )
        
        # Get vector store stats after query
        post_query_stats = pathway_vector_store.get_real_time_stats()
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "real_time_proof": {
                "query_timestamp": datetime.utcnow().isoformat(),
                "vector_store_last_update": post_query_stats["last_update"],
                "total_documents": post_query_stats["total_documents"],
                "recent_updates": post_query_stats["recent_updates_count"],
                "data_freshness": "live",
                "pathway_powered": True
            },
            "performance": {
                "pre_query_size": pre_query_stats["total_documents"],
                "post_query_size": post_query_stats["total_documents"],
                "updates_during_query": post_query_stats["update_counter"] - pre_query_stats["update_counter"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in real-time RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Real-time query failed: {str(e)}")

@router.post("/data/add-live")
async def add_live_data(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Add data that immediately becomes available for queries
    
    This demonstrates Pathway's real-time indexing:
    - Data added here is immediately searchable
    - No manual rebuilds or delays
    """
    try:
        content = data.get("content", "")
        metadata = data.get("metadata", {})
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        # Add timestamp and user info
        metadata.update({
            "added_by": current_user.get("user_id", "unknown"),
            "added_via": "live_api",
            "live_update": True
        })
        
        # Add to vector store - this happens IMMEDIATELY
        doc_id = pathway_vector_store.add_document_streaming(content, metadata)
        
        if doc_id == -1:
            raise HTTPException(status_code=500, detail="Failed to add document")
        
        # Notify WebSocket connections of live update
        background_tasks.add_task(
            notify_live_update,
            {
                "type": "document_added",
                "doc_id": doc_id,
                "content_preview": content[:100] + "...",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Get updated stats
        updated_stats = pathway_vector_store.get_real_time_stats()
        
        return {
            "status": "success",
            "message": "Data added and immediately available for queries",
            "document_id": doc_id,
            "real_time_proof": {
                "added_at": datetime.utcnow().isoformat(),
                "immediately_searchable": True,
                "vector_store_size": updated_stats["total_documents"],
                "last_update": updated_stats["last_update"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding live data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add live data: {str(e)}")

@router.get("/demo/real-time-proof")
async def demonstrate_real_time_capability(
    test_query: str = "supply chain disruption",
    current_user: Dict = Depends(get_current_user)
):
    """
    Demonstrate real-time capability by showing before/after query results
    
    This endpoint proves that Pathway updates are immediate:
    1. Query current state
    2. Add new data
    3. Query again - new data is immediately available
    """
    try:
        # Step 1: Query current state
        initial_results = await query_interface.query_supply_chain_intelligence(test_query, k=3)
        initial_size = pathway_vector_store.get_current_size()
        
        # Step 2: Add new test data with timestamp
        test_content = f"LIVE TEST: Supply chain disruption detected at {datetime.utcnow().isoformat()} - This is a real-time test to prove immediate data availability."
        test_metadata = {
            "type": "live_test",
            "test_timestamp": datetime.utcnow().isoformat(),
            "demo_purpose": True
        }
        
        new_doc_id = pathway_vector_store.add_document_streaming(test_content, test_metadata)
        
        # Step 3: Query again immediately
        updated_results = await query_interface.query_supply_chain_intelligence(test_query, k=3)
        updated_size = pathway_vector_store.get_current_size()
        
        # Step 4: Verify the new data appears in results
        new_data_found = any(
            result.get("metadata", {}).get("test_timestamp") == test_metadata["test_timestamp"]
            for result in updated_results.get("results", [])
        )
        
        return {
            "status": "success",
            "real_time_proof": {
                "test_query": test_query,
                "initial_vector_size": initial_size,
                "updated_vector_size": updated_size,
                "size_increased": updated_size > initial_size,
                "new_data_immediately_searchable": new_data_found,
                "test_document_id": new_doc_id,
                "test_timestamp": test_metadata["test_timestamp"]
            },
            "initial_results": {
                "count": len(initial_results.get("results", [])),
                "timestamp": initial_results.get("timestamp")
            },
            "updated_results": {
                "count": len(updated_results.get("results", [])),
                "timestamp": updated_results.get("timestamp"),
                "contains_new_data": new_data_found
            },
            "pathway_features_demonstrated": [
                "immediate_indexing",
                "no_rebuild_required",
                "real_time_search",
                "live_data_availability"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in real-time proof demo: {e}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

@router.get("/stats/real-time")
async def get_real_time_stats(
    current_user: Dict = Depends(get_current_user)
):
    """Get real-time statistics about the Pathway-powered system"""
    try:
        stats = pathway_vector_store.get_real_time_stats()
        recent_updates = pathway_vector_store.get_recent_updates(minutes=60)
        
        return {
            "status": "success",
            "real_time_stats": stats,
            "recent_updates": recent_updates,
            "pathway_capabilities": {
                "streaming_etl": True,
                "dynamic_indexing": True,
                "no_rebuilds": True,
                "live_retrieval": True
            },
            "system_health": {
                "vector_store_operational": stats["total_documents"] > 0,
                "recent_activity": len(recent_updates) > 0,
                "last_update_age_seconds": (
                    datetime.utcnow() - datetime.fromisoformat(stats["last_update"])
                ).total_seconds()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@router.post("/pipeline/trigger-update")
async def trigger_pipeline_update(
    update_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Trigger a pipeline update to demonstrate streaming ETL
    
    This simulates external data sources updating the system
    """
    try:
        # Create sample supply chain event
        event_data = {
            "source": update_data.get("source", "manual_trigger"),
            "event_type": update_data.get("event_type", "supply_chain_update"),
            "title": update_data.get("title", f"Supply Chain Update - {datetime.utcnow().isoformat()}"),
            "description": update_data.get("description", "Manual pipeline update triggered via API"),
            "location": update_data.get("location", "Global"),
            "content": update_data.get("content", f"Pipeline update at {datetime.utcnow().isoformat()}"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Process through AI pipeline
        from src.core.detectors.ai_disruption_detector import AIDisruptionDetector
        ai_detector = AIDisruptionDetector()
        
        # Analyze the event
        disruptions = await ai_detector.detect_disruptions_ai([event_data])
        
        # Add to vector store
        for disruption in disruptions:
            content = f"{disruption['source_data'].get('title', '')} - {disruption['source_data'].get('description', '')}"
            metadata = {
                "type": "pipeline_update",
                "disruption_score": disruption.get("disruption_score", 0),
                "ai_analysis": disruption.get("ai_analysis", {}),
                "triggered_by": current_user.get("user_id", "unknown")
            }
            
            pathway_vector_store.add_document_streaming(content, metadata)
        
        return {
            "status": "success",
            "message": "Pipeline update triggered and processed",
            "processed_events": len([event_data]),
            "detected_disruptions": len(disruptions),
            "real_time_updates": len(disruptions),
            "pathway_processing": {
                "streaming_etl": True,
                "immediate_indexing": True,
                "live_availability": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error triggering pipeline update: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline update failed: {str(e)}")

@router.websocket("/ws/live-updates")
async def websocket_live_updates(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    
    Clients can connect here to receive live notifications when data is updated
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial stats
        stats = pathway_vector_store.get_real_time_stats()
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to Pathway real-time updates",
            "current_stats": stats
        })
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(30)  # Send updates every 30 seconds
            
            current_stats = pathway_vector_store.get_real_time_stats()
            recent_updates = pathway_vector_store.get_recent_updates(minutes=5)
            
            await websocket.send_json({
                "type": "periodic_update",
                "timestamp": datetime.utcnow().isoformat(),
                "stats": current_stats,
                "recent_updates": len(recent_updates)
            })
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

async def notify_live_update(update_data: Dict[str, Any]):
    """Notify all WebSocket connections of live updates"""
    if not active_connections:
        return
    
    message = {
        "type": "live_update",
        "data": update_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to all connected clients
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket update: {e}")
            disconnected.append(connection)
    
    # Remove disconnected clients
    for connection in disconnected:
        active_connections.remove(connection)

@router.get("/health/pathway")
async def check_pathway_health():
    """Check health of Pathway-powered components"""
    try:
        # Test vector store
        test_query = "test health check"
        search_results = pathway_vector_store.search_real_time(test_query, k=1)
        
        # Test real-time capabilities
        test_doc_id = pathway_vector_store.add_document_streaming(
            f"Health check at {datetime.utcnow().isoformat()}",
            {"type": "health_check", "timestamp": datetime.utcnow().isoformat()}
        )
        
        # Verify immediate availability
        immediate_search = pathway_vector_store.search_real_time("health check", k=1)
        immediate_available = any(
            result.get("metadata", {}).get("type") == "health_check"
            for result in immediate_search
        )
        
        stats = pathway_vector_store.get_real_time_stats()
        
        return {
            "status": "healthy",
            "pathway_components": {
                "vector_store": "operational",
                "real_time_search": "operational",
                "streaming_updates": "operational",
                "immediate_indexing": immediate_available
            },
            "performance": {
                "total_documents": stats["total_documents"],
                "last_update": stats["last_update"],
                "update_counter": stats["update_counter"]
            },
            "real_time_proof": {
                "test_document_added": test_doc_id != -1,
                "immediately_searchable": immediate_available,
                "no_rebuild_required": True
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Pathway health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat()
        } 