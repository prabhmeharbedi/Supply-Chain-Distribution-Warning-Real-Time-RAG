"""
Pathway-Powered Real-Time RAG Pipeline for Supply Chain Intelligence
"""

import pathway as pw
import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from sentence_transformers import SentenceTransformer
import openai

from src.utils.logger import setup_logger
from src.core.rag.pathway_vector_store import PathwayVectorStore
from src.core.detectors.ai_disruption_detector import AIDisruptionDetector
from src.services.ai_analysis_service import AIAnalysisService
from config.settings import settings

logger = setup_logger(__name__)

class PathwayRAGPipeline:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = PathwayVectorStore()
        self.ai_detector = AIDisruptionDetector()
        self.ai_analysis = AIAnalysisService()
        
        # Initialize OpenAI if available
        self.openai_client = None
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
            logger.info("OpenAI initialized for Pathway RAG pipeline")
        
        logger.info("Pathway RAG Pipeline initialized")
    
    def create_streaming_pipeline(self):
        """Create the main Pathway streaming pipeline"""
        
        # 1. Data Sources - Multiple streaming inputs
        weather_stream = self._create_weather_stream()
        news_stream = self._create_news_stream()
        earthquake_stream = self._create_earthquake_stream()
        file_stream = self._create_file_stream()
        
        # 2. Combine all streams
        combined_stream = pw.Table.concat_reindex(
            weather_stream,
            news_stream, 
            earthquake_stream,
            file_stream
        )
        
        # 3. Real-time processing and enrichment
        enriched_stream = combined_stream.select(
            *pw.this,
            processed_at=pw.apply(lambda: datetime.utcnow().isoformat()),
            embedding=pw.apply_async(self._create_embedding, pw.this.content),
            supply_chain_relevance=pw.apply_async(self._assess_relevance, pw.this),
            ai_analysis=pw.apply_async(self._analyze_with_ai, pw.this)
        )
        
        # 4. Filter for supply chain relevant events
        relevant_stream = enriched_stream.filter(pw.this.supply_chain_relevance > 0.3)
        
        # 5. Real-time vector store updates
        vector_updates = relevant_stream.select(
            *pw.this,
            vector_id=pw.apply_async(self._update_vector_store, pw.this)
        )
        
        # 6. Generate disruption alerts
        disruption_alerts = vector_updates.select(
            *pw.this,
            disruption_score=pw.apply_async(self._calculate_disruption_score, pw.this),
            alert_generated=pw.apply_async(self._generate_alert, pw.this)
        )
        
        # 7. Output streams for different consumers
        self._setup_output_streams(disruption_alerts)
        
        return disruption_alerts
    
    def _create_weather_stream(self):
        """Create weather data stream"""
        # Simulated weather data stream - in production, connect to actual weather APIs
        weather_schema = pw.schema_from_types(
            source=str,
            event_type=str,
            title=str,
            description=str,
            location=str,
            severity=str,
            latitude=float,
            longitude=float,
            content=str,
            timestamp=str
        )
        
        # For demo - create from directory monitoring
        return pw.io.fs.read(
            path="./data/weather/",
            format="json",
            schema=weather_schema,
            mode="streaming"
        )
    
    def _create_news_stream(self):
        """Create news data stream"""
        news_schema = pw.schema_from_types(
            source=str,
            event_type=str,
            title=str,
            description=str,
            location=str,
            content=str,
            url=str,
            published_at=str,
            timestamp=str
        )
        
        return pw.io.fs.read(
            path="./data/news/",
            format="json", 
            schema=news_schema,
            mode="streaming"
        )
    
    def _create_earthquake_stream(self):
        """Create earthquake data stream"""
        earthquake_schema = pw.schema_from_types(
            source=str,
            event_type=str,
            title=str,
            description=str,
            location=str,
            magnitude=float,
            depth=float,
            latitude=float,
            longitude=float,
            content=str,
            timestamp=str
        )
        
        return pw.io.fs.read(
            path="./data/earthquakes/",
            format="json",
            schema=earthquake_schema,
            mode="streaming"
        )
    
    def _create_file_stream(self):
        """Create file-based data stream for manual updates"""
        file_schema = pw.schema_from_types(
            source=str,
            event_type=str,
            title=str,
            description=str,
            location=str,
            content=str,
            metadata=str,
            timestamp=str
        )
        
        return pw.io.fs.read(
            path="./data/manual_updates/",
            format="json",
            schema=file_schema,
            mode="streaming"
        )
    
    async def _create_embedding(self, content: str) -> List[float]:
        """Create embedding for content"""
        try:
            if not content:
                return [0.0] * 384  # Default embedding size
            
            embedding = self.embedding_model.encode([content])[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return [0.0] * 384
    
    async def _assess_relevance(self, row: Dict[str, Any]) -> float:
        """Assess supply chain relevance using AI"""
        try:
            content = row.get('content', '') or f"{row.get('title', '')} {row.get('description', '')}"
            
            # Use AI detector for relevance assessment
            relevance = await self.ai_detector._is_supply_chain_relevant_ai({
                'title': row.get('title', ''),
                'description': row.get('description', ''),
                'location': row.get('location', ''),
                'event_type': row.get('event_type', '')
            })
            
            return 0.8 if relevance else 0.2
            
        except Exception as e:
            logger.error(f"Error assessing relevance: {e}")
            return 0.0
    
    async def _analyze_with_ai(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI analysis on the event"""
        try:
            # Get context from vector store
            context = self.vector_store.get_context_for_event(row)
            
            # Use AI detector for analysis
            analysis = await self.ai_detector._analyze_with_ai(row, context)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                "disruption_type": "unknown",
                "confidence_level": 0.5,
                "impact_severity": "moderate"
            }
    
    async def _update_vector_store(self, row: Dict[str, Any]) -> str:
        """Update vector store with new data in real-time"""
        try:
            content = row.get('content', '') or f"{row.get('title', '')} {row.get('description', '')}"
            
            metadata = {
                "source": row.get('source', 'unknown'),
                "event_type": row.get('event_type', 'unknown'),
                "location": row.get('location', ''),
                "timestamp": row.get('timestamp', datetime.utcnow().isoformat()),
                "processed_at": row.get('processed_at', datetime.utcnow().isoformat()),
                "ai_analysis": row.get('ai_analysis', {})
            }
            
            # Add to vector store - this happens in real-time!
            vector_id = self.vector_store.add_document_streaming(content, metadata)
            
            logger.info(f"Real-time vector store update: {vector_id} for {row.get('title', 'Unknown')}")
            
            return f"vector_{vector_id}_{datetime.utcnow().timestamp()}"
            
        except Exception as e:
            logger.error(f"Error updating vector store: {e}")
            return "error"
    
    async def _calculate_disruption_score(self, row: Dict[str, Any]) -> float:
        """Calculate disruption score"""
        try:
            ai_analysis = row.get('ai_analysis', {})
            
            # Use AI detector scoring
            score = await self.ai_detector._calculate_ai_disruption_score(
                row, ai_analysis, {}
            )
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating disruption score: {e}")
            return 0.0
    
    async def _generate_alert(self, row: Dict[str, Any]) -> bool:
        """Generate alert if disruption score is high enough"""
        try:
            disruption_score = row.get('disruption_score', 0.0)
            
            if disruption_score >= 0.5:  # Alert threshold
                alert_data = {
                    "id": f"alert_{datetime.utcnow().timestamp()}",
                    "title": row.get('title', 'Supply Chain Alert'),
                    "description": row.get('description', ''),
                    "location": row.get('location', ''),
                    "disruption_score": disruption_score,
                    "ai_analysis": row.get('ai_analysis', {}),
                    "vector_id": row.get('vector_id', ''),
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                # Store alert (in production, this would go to database/queue)
                logger.info(f"🚨 REAL-TIME ALERT GENERATED: {alert_data['title']} (Score: {disruption_score:.2f})")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            return False
    
    def _setup_output_streams(self, processed_stream):
        """Setup output streams for different consumers"""
        
        # 1. High-priority alerts stream
        alerts_stream = processed_stream.filter(pw.this.disruption_score >= 0.7)
        
        # 2. All processed events stream  
        events_stream = processed_stream.filter(pw.this.supply_chain_relevance > 0.3)
        
        # 3. Vector store updates stream
        vector_stream = processed_stream.select(
            pw.this.vector_id,
            pw.this.title,
            pw.this.processed_at
        )
        
        # Output to different sinks
        pw.io.fs.write(
            alerts_stream,
            pw.io.fs.write.ParquetSink("./output/alerts/"),
            format="parquet"
        )
        
        pw.io.fs.write(
            events_stream,
            pw.io.fs.write.JsonSink("./output/events/"),
            format="json"
        )
        
        # Real-time API updates (webhook/callback)
        alerts_stream.output_to(self._send_real_time_alert)
    
    async def _send_real_time_alert(self, alert_data):
        """Send real-time alert to API consumers"""
        try:
            # In production, this would send to webhooks, WebSocket connections, etc.
            logger.info(f"📡 REAL-TIME API UPDATE: {alert_data}")
            
            # Update global state for API queries
            self.vector_store.latest_alerts.append(alert_data)
            
        except Exception as e:
            logger.error(f"Error sending real-time alert: {e}")
    
    def start_streaming(self):
        """Start the Pathway streaming pipeline"""
        try:
            logger.info("🚀 Starting Pathway Real-Time RAG Pipeline...")
            
            # Create the pipeline
            pipeline = self.create_streaming_pipeline()
            
            # Run the pipeline
            pw.run(
                monitoring_level=pw.MonitoringLevel.ALL,
                with_http_server=True,
                http_server_port=8080
            )
            
        except Exception as e:
            logger.error(f"Error starting Pathway pipeline: {e}")
            raise
    
    def get_real_time_query_interface(self):
        """Get interface for real-time queries"""
        return PathwayQueryInterface(self.vector_store, self.ai_analysis)


class PathwayQueryInterface:
    """Real-time query interface that reflects latest data immediately"""
    
    def __init__(self, vector_store, ai_analysis):
        self.vector_store = vector_store
        self.ai_analysis = ai_analysis
        logger.info("Pathway Query Interface initialized")
    
    async def query_supply_chain_intelligence(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Query the real-time updated knowledge base"""
        try:
            # This query will IMMEDIATELY reflect any updates that happened at T+0
            results = self.vector_store.search_real_time(query, k=k)
            
            # Generate AI insights based on latest data
            insights = await self._generate_real_time_insights(query, results)
            
            return {
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "results": results,
                "ai_insights": insights,
                "data_freshness": "real_time",
                "vector_store_size": self.vector_store.get_current_size()
            }
            
        except Exception as e:
            logger.error(f"Error in real-time query: {e}")
            return {"error": str(e)}
    
    async def _generate_real_time_insights(self, query: str, results: List[Dict]) -> Dict[str, Any]:
        """Generate AI insights from real-time data"""
        try:
            if not results:
                return {"message": "No relevant data found"}
            
            # Combine results for AI analysis
            context = "\n".join([r.get("document", "") for r in results[:3]])
            
            prompt = f"""
            Based on the latest real-time supply chain data, provide insights for this query: "{query}"
            
            Latest Data Context:
            {context}
            
            Provide insights in JSON format:
            {{
                "key_findings": ["list of key findings"],
                "risk_assessment": "low|medium|high|critical",
                "recommendations": ["list of recommendations"],
                "affected_regions": ["list of regions"],
                "confidence": 0.0-1.0
            }}
            """
            
            # This would use OpenAI API if available
            insights = {
                "key_findings": ["Real-time analysis based on latest data"],
                "risk_assessment": "medium",
                "recommendations": ["Monitor situation closely"],
                "affected_regions": [],
                "confidence": 0.8
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating real-time insights: {e}")
            return {"error": str(e)}

# Global pipeline instance
pathway_rag_pipeline = PathwayRAGPipeline() 