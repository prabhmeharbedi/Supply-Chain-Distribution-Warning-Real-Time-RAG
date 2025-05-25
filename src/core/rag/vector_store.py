"""
Vector Store for Supply Chain RAG System
"""

import numpy as np
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import faiss
from sentence_transformers import SentenceTransformer
from src.utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

class SupplyChainVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.documents = []  # Store original documents
        self.metadata = []   # Store metadata for each document
        
        # Initialize with supply chain knowledge base
        self._initialize_knowledge_base()
        
    def _initialize_knowledge_base(self):
        """Initialize vector store with supply chain knowledge"""
        logger.info("Initializing supply chain knowledge base...")
        
        # Supply chain knowledge documents
        knowledge_docs = [
            {
                "content": "Shanghai Port is the world's busiest container port, handling over 47 million TEU annually. Disruptions here affect global electronics, automotive, and consumer goods supply chains.",
                "type": "port_info",
                "location": "Shanghai, China",
                "importance": 10
            },
            {
                "content": "Suez Canal handles 12% of global trade and 30% of container traffic. Blockages cause massive delays in Asia-Europe trade routes affecting oil, consumer goods, and manufacturing.",
                "type": "waterway_info", 
                "location": "Suez Canal, Egypt",
                "importance": 10
            },
            {
                "content": "Taiwan produces 63% of global semiconductors. Any disruption in Taiwan affects global electronics, automotive, and technology supply chains with 3-6 month recovery times.",
                "type": "sector_info",
                "location": "Taiwan",
                "importance": 9
            },
            {
                "content": "Los Angeles and Long Beach ports handle 40% of US container imports. Labor strikes, congestion, or closures impact retail, automotive, and consumer electronics nationwide.",
                "type": "port_info",
                "location": "Los Angeles, USA", 
                "importance": 8
            },
            {
                "content": "Typhoons in the Pacific typically disrupt shipping for 3-7 days, affecting trans-Pacific trade routes. Peak season is June-November with highest impact in August-October.",
                "type": "weather_pattern",
                "location": "Pacific Ocean",
                "importance": 7
            },
            {
                "content": "Just-in-time manufacturing makes automotive supply chains vulnerable to disruptions. A single component shortage can halt production lines within 2-3 days.",
                "type": "sector_vulnerability",
                "location": "Global",
                "importance": 8
            },
            {
                "content": "Pharmaceutical supply chains are highly regulated and concentrated. 80% of active pharmaceutical ingredients come from China and India, creating single points of failure.",
                "type": "sector_info",
                "location": "China, India",
                "importance": 9
            },
            {
                "content": "Rotterdam Port is Europe's largest port, handling 14.8 million TEU. Disruptions affect European manufacturing, energy imports, and consumer goods distribution.",
                "type": "port_info",
                "location": "Rotterdam, Netherlands",
                "importance": 8
            },
            {
                "content": "Cyber attacks on supply chain systems can cause weeks of disruption. Colonial Pipeline attack in 2021 disrupted fuel supplies across US East Coast for 6 days.",
                "type": "cyber_threat",
                "location": "Global",
                "importance": 7
            },
            {
                "content": "Ukraine and Russia supply 30% of global wheat exports. Conflicts or trade restrictions cause food price volatility and supply shortages globally.",
                "type": "agriculture_info",
                "location": "Ukraine, Russia",
                "importance": 8
            }
        ]
        
        # Add documents to vector store
        for doc in knowledge_docs:
            self.add_document(doc["content"], doc)
            
        logger.info(f"Initialized knowledge base with {len(knowledge_docs)} documents")
    
    def add_document(self, text: str, metadata: Dict[str, Any] = None) -> int:
        """Add a document to the vector store"""
        try:
            # Create embedding
            embedding = self.embedding_model.encode([text])[0]
            
            # Normalize for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            
            # Add to FAISS index
            self.index.add(np.array([embedding]).astype('float32'))
            
            # Store document and metadata
            self.documents.append(text)
            self.metadata.append(metadata or {})
            
            doc_id = len(self.documents) - 1
            logger.debug(f"Added document {doc_id} to vector store")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            return -1
    
    def search(self, query: str, k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search FAISS index
            scores, indices = self.index.search(
                np.array([query_embedding]).astype('float32'), k
            )
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= threshold and idx < len(self.documents):
                    results.append({
                        "document": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "score": float(score),
                        "rank": i + 1
                    })
            
            logger.debug(f"Found {len(results)} relevant documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_context_for_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant context for a supply chain event"""
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
        
        # Search for relevant documents
        relevant_docs = self.search(query, k=3, threshold=0.3)
        
        # Organize context
        context = {
            "relevant_knowledge": relevant_docs,
            "location_insights": [],
            "sector_insights": [],
            "historical_patterns": []
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
    
    def add_disruption_event(self, disruption: Dict[str, Any]):
        """Add a disruption event to the knowledge base for future reference"""
        try:
            # Create document text from disruption
            source_data = disruption.get("source_data", {})
            ai_analysis = disruption.get("ai_analysis", {})
            
            doc_text = f"""
            Disruption Event: {source_data.get('title', 'Unknown')}
            Location: {source_data.get('location', 'Unknown')}
            Type: {ai_analysis.get('disruption_type', 'unknown')}
            Severity: {ai_analysis.get('impact_severity', 'unknown')}
            Affected Sectors: {', '.join(ai_analysis.get('affected_sectors', []))}
            Duration: {ai_analysis.get('predicted_duration_days', 0)} days
            Description: {source_data.get('description', '')}
            """
            
            metadata = {
                "type": "historical_disruption",
                "location": source_data.get('location', ''),
                "disruption_type": ai_analysis.get('disruption_type', ''),
                "severity": ai_analysis.get('impact_severity', ''),
                "date": disruption.get('detected_at', ''),
                "score": disruption.get('disruption_score', 0)
            }
            
            self.add_document(doc_text.strip(), metadata)
            logger.info(f"Added disruption event to knowledge base: {source_data.get('title', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error adding disruption event to knowledge base: {e}")
    
    def get_similar_historical_events(self, current_event: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
        """Find similar historical disruption events"""
        try:
            # Create query from current event
            source_data = current_event.get("source_data", {})
            query = f"""
            {source_data.get('title', '')} 
            {source_data.get('description', '')} 
            {source_data.get('location', '')}
            {source_data.get('event_type', '')}
            """
            
            # Search for similar events
            results = self.search(query.strip(), k=k * 2)  # Get more results to filter
            
            # Filter for historical disruptions only
            historical_events = [
                result for result in results 
                if result["metadata"].get("type") == "historical_disruption"
            ]
            
            return historical_events[:k]
            
        except Exception as e:
            logger.error(f"Error finding similar historical events: {e}")
            return []
    
    def save_index(self, filepath: str):
        """Save FAISS index to disk"""
        try:
            faiss.write_index(self.index, filepath)
            
            # Save documents and metadata separately
            data = {
                "documents": self.documents,
                "metadata": self.metadata,
                "dimension": self.dimension
            }
            
            with open(f"{filepath}.json", 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved vector store to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def load_index(self, filepath: str):
        """Load FAISS index from disk"""
        try:
            self.index = faiss.read_index(filepath)
            
            # Load documents and metadata
            with open(f"{filepath}.json", 'r') as f:
                data = json.load(f)
                
            self.documents = data["documents"]
            self.metadata = data["metadata"]
            self.dimension = data["dimension"]
            
            logger.info(f"Loaded vector store from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal,
            "dimension": self.dimension,
            "document_types": self._get_document_type_counts()
        }
    
    def _get_document_type_counts(self) -> Dict[str, int]:
        """Get count of documents by type"""
        type_counts = {}
        for metadata in self.metadata:
            doc_type = metadata.get("type", "unknown")
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        return type_counts

# Global vector store instance
vector_store = SupplyChainVectorStore() 