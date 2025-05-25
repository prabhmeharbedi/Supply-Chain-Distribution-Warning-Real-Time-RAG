"""
Pathway-Powered Vector Store with Real-Time Streaming Updates
"""

import pathway as pw
import numpy as np
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import faiss
from sentence_transformers import SentenceTransformer
import threading
import asyncio
from collections import deque

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PathwayVectorStore:
    """Real-time vector store powered by Pathway streaming"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Thread-safe FAISS index for real-time updates
        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []
        self.metadata = []
        self.latest_alerts = deque(maxlen=100)  # Keep latest 100 alerts
        
        # Real-time update tracking
        self.update_counter = 0
        self.last_update_time = datetime.utcnow()
        self.lock = threading.RLock()
        
        # Initialize with base knowledge
        self._initialize_base_knowledge()
        
        logger.info(f"Pathway Vector Store initialized with dimension {dimension}")
    
    def _initialize_base_knowledge(self):
        """Initialize with base supply chain knowledge"""
        base_knowledge = [
            {
                "content": "Shanghai Port is the world's busiest container port, handling over 47 million TEU annually. Real-time disruptions here immediately affect global electronics, automotive, and consumer goods supply chains.",
                "metadata": {"type": "port_info", "location": "Shanghai, China", "importance": 10, "real_time": True}
            },
            {
                "content": "Suez Canal handles 12% of global trade. Any blockage or disruption is immediately reflected in Asia-Europe trade route delays affecting oil, consumer goods, and manufacturing.",
                "metadata": {"type": "waterway_info", "location": "Suez Canal, Egypt", "importance": 10, "real_time": True}
            },
            {
                "content": "Taiwan semiconductor production disruptions have immediate global impact. Real-time monitoring shows 63% of global chip production concentrated here.",
                "metadata": {"type": "sector_info", "location": "Taiwan", "importance": 9, "real_time": True}
            }
        ]
        
        for doc in base_knowledge:
            self.add_document_streaming(doc["content"], doc["metadata"])
    
    def add_document_streaming(self, text: str, metadata: Dict[str, Any] = None) -> int:
        """Add document with real-time streaming capability"""
        with self.lock:
            try:
                # Create embedding
                embedding = self.embedding_model.encode([text])[0]
                embedding = embedding / np.linalg.norm(embedding)
                
                # Add to FAISS index atomically
                self.index.add(np.array([embedding]).astype('float32'))
                
                # Store document and metadata
                self.documents.append(text)
                self.metadata.append({
                    **(metadata or {}),
                    "added_at": datetime.utcnow().isoformat(),
                    "update_id": self.update_counter,
                    "real_time": True
                })
                
                doc_id = len(self.documents) - 1
                self.update_counter += 1
                self.last_update_time = datetime.utcnow()
                
                logger.info(f"🔄 REAL-TIME UPDATE: Added document {doc_id} to vector store")
                
                return doc_id
                
            except Exception as e:
                logger.error(f"Error in streaming document add: {e}")
                return -1
    
    def search_real_time(self, query: str, k: int = 5, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Real-time search that immediately reflects latest updates"""
        with self.lock:
            try:
                if self.index.ntotal == 0:
                    return []
                
                # Create query embedding
                query_embedding = self.embedding_model.encode([query])[0]
                query_embedding = query_embedding / np.linalg.norm(query_embedding)
                
                # Search FAISS index - this includes ALL real-time updates
                scores, indices = self.index.search(
                    np.array([query_embedding]).astype('float32'), 
                    min(k, self.index.ntotal)
                )
                
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if score >= threshold and idx < len(self.documents):
                        results.append({
                            "document": self.documents[idx],
                            "metadata": self.metadata[idx],
                            "score": float(score),
                            "rank": i + 1,
                            "real_time_freshness": self._calculate_freshness(self.metadata[idx])
                        })
                
                logger.debug(f"Real-time search returned {len(results)} results for: {query}")
                return results
                
            except Exception as e:
                logger.error(f"Error in real-time search: {e}")
                return []
    
    def _calculate_freshness(self, metadata: Dict[str, Any]) -> str:
        """Calculate data freshness indicator"""
        try:
            added_at = datetime.fromisoformat(metadata.get("added_at", datetime.utcnow().isoformat()))
            age_seconds = (datetime.utcnow() - added_at).total_seconds()
            
            if age_seconds < 60:
                return "live"  # Less than 1 minute
            elif age_seconds < 3600:
                return "recent"  # Less than 1 hour
            elif age_seconds < 86400:
                return "today"  # Less than 1 day
            else:
                return "historical"
                
        except Exception:
            return "unknown"
    
    def get_context_for_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Get real-time context for an event"""
        # Create search query from event
        query_parts = []
        
        if event.get('title'):
            query_parts.append(event['title'])
        if event.get('description'):
            query_parts.append(event['description'])
        if event.get('location'):
            query_parts.append(f"location: {event['location']}")
        if event.get('event_type'):
            query_parts.append(f"type: {event['event_type']}")
        
        query = " ".join(query_parts)
        
        # Real-time search for relevant context
        relevant_docs = self.search_real_time(query, k=5, threshold=0.2)
        
        # Organize context with real-time indicators
        context = {
            "relevant_knowledge": relevant_docs,
            "location_insights": [],
            "sector_insights": [],
            "historical_patterns": [],
            "real_time_updates": self.get_recent_updates(minutes=30)
        }
        
        # Categorize results
        for doc in relevant_docs:
            metadata = doc["metadata"]
            doc_type = metadata.get("type", "")
            
            if "port" in doc_type or "waterway" in doc_type:
                context["location_insights"].append(doc)
            elif "sector" in doc_type or "agriculture" in doc_type:
                context["sector_insights"].append(doc)
            elif "pattern" in doc_type or "weather" in doc_type:
                context["historical_patterns"].append(doc)
        
        return context
    
    def get_recent_updates(self, minutes: int = 30) -> List[Dict[str, Any]]:
        """Get updates from the last N minutes"""
        with self.lock:
            cutoff_time = datetime.utcnow().timestamp() - (minutes * 60)
            
            recent_updates = []
            for i, metadata in enumerate(self.metadata):
                try:
                    added_at = datetime.fromisoformat(metadata.get("added_at", ""))
                    if added_at.timestamp() > cutoff_time:
                        recent_updates.append({
                            "document_id": i,
                            "content": self.documents[i][:100] + "...",
                            "metadata": metadata,
                            "added_at": metadata.get("added_at")
                        })
                except Exception:
                    continue
            
            return sorted(recent_updates, key=lambda x: x["added_at"], reverse=True)
    
    def get_current_size(self) -> int:
        """Get current vector store size"""
        with self.lock:
            return len(self.documents)
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics"""
        with self.lock:
            recent_updates = self.get_recent_updates(60)  # Last hour
            
            return {
                "total_documents": len(self.documents),
                "index_size": self.index.ntotal,
                "dimension": self.dimension,
                "last_update": self.last_update_time.isoformat(),
                "update_counter": self.update_counter,
                "recent_updates_count": len(recent_updates),
                "latest_alerts_count": len(self.latest_alerts),
                "data_freshness": "real_time"
            }
    
    def create_pathway_connector(self):
        """Create Pathway connector for streaming updates"""
        
        # Define schema for incoming documents
        document_schema = pw.schema_from_types(
            content=str,
            metadata=str,
            timestamp=str
        )
        
        # Create input connector
        input_table = pw.io.fs.read(
            path="./data/vector_updates/",
            format="json",
            schema=document_schema,
            mode="streaming"
        )
        
        # Process and add to vector store
        processed_table = input_table.select(
            *pw.this,
            vector_id=pw.apply_async(self._pathway_add_document, pw.this.content, pw.this.metadata)
        )
        
        return processed_table
    
    async def _pathway_add_document(self, content: str, metadata_str: str) -> str:
        """Pathway-compatible document addition"""
        try:
            metadata = json.loads(metadata_str) if metadata_str else {}
            doc_id = self.add_document_streaming(content, metadata)
            return f"doc_{doc_id}"
        except Exception as e:
            logger.error(f"Error in Pathway document addition: {e}")
            return "error"
    
    def start_real_time_monitoring(self):
        """Start real-time monitoring and updates"""
        logger.info("🔄 Starting real-time vector store monitoring...")
        
        # Create Pathway connector
        pathway_table = self.create_pathway_connector()
        
        # Output real-time updates
        pw.io.fs.write(
            pathway_table,
            pw.io.fs.write.JsonSink("./output/vector_updates/"),
            format="json"
        )
        
        logger.info("Real-time vector store monitoring active")


class PathwayRAGConnector:
    """Connector between Pathway pipeline and vector store"""
    
    def __init__(self, vector_store: PathwayVectorStore):
        self.vector_store = vector_store
        logger.info("Pathway RAG Connector initialized")
    
    def create_real_time_rag_pipeline(self):
        """Create real-time RAG pipeline with Pathway"""
        
        # 1. Query input stream
        query_schema = pw.schema_from_types(
            query=str,
            user_id=str,
            timestamp=str,
            context=str
        )
        
        query_stream = pw.io.fs.read(
            path="./data/queries/",
            format="json",
            schema=query_schema,
            mode="streaming"
        )
        
        # 2. Real-time RAG processing
        rag_results = query_stream.select(
            *pw.this,
            search_results=pw.apply_async(self._real_time_search, pw.this.query),
            response_generated=pw.apply_async(self._generate_rag_response, pw.this.query, pw.this.context),
            processed_at=pw.apply(lambda: datetime.utcnow().isoformat())
        )
        
        # 3. Output real-time responses
        pw.io.fs.write(
            rag_results,
            pw.io.fs.write.JsonSink("./output/rag_responses/"),
            format="json"
        )
        
        return rag_results
    
    async def _real_time_search(self, query: str) -> str:
        """Perform real-time search"""
        try:
            results = self.vector_store.search_real_time(query, k=5)
            return json.dumps(results)
        except Exception as e:
            logger.error(f"Error in real-time search: {e}")
            return json.dumps([])
    
    async def _generate_rag_response(self, query: str, context: str) -> str:
        """Generate RAG response with real-time data"""
        try:
            # Get latest search results
            search_results = self.vector_store.search_real_time(query, k=3)
            
            if not search_results:
                return "No relevant real-time data found for your query."
            
            # Combine results for response
            context_text = "\n".join([r["document"][:200] for r in search_results])
            
            response = f"""
            Based on real-time supply chain data (last updated: {datetime.utcnow().isoformat()}):
            
            Query: {query}
            
            Key Findings:
            {context_text}
            
            Data Freshness: {search_results[0].get('real_time_freshness', 'live')}
            Vector Store Size: {self.vector_store.get_current_size()} documents
            """
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return f"Error processing query: {str(e)}"

# Global instances
pathway_vector_store = PathwayVectorStore()
pathway_rag_connector = PathwayRAGConnector(pathway_vector_store) 