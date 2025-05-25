"""
AI-Powered Supply Chain Disruption Detection Engine with RAG Capabilities
"""

import json
import openai
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
import asyncio
from src.utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

class AIDisruptionDetector:
    def __init__(self):
        # Initialize AI models
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.openai_client = None
        
        # Initialize OpenAI if API key is available
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
            logger.info("OpenAI client initialized for advanced AI analysis")
        else:
            logger.warning("OpenAI API key not found. Using basic analysis only.")
        
        # Supply chain knowledge base for RAG
        self.supply_chain_knowledge = {
            "critical_routes": {
                "trans_pacific": {
                    "description": "Major trade route between Asia and North America",
                    "key_ports": ["Shanghai", "Shenzhen", "Los Angeles", "Long Beach", "Seattle"],
                    "typical_disruptions": ["typhoons", "port congestion", "labor strikes"],
                    "impact_multiplier": 2.5,
                    "daily_volume_teu": 50000
                },
                "asia_europe": {
                    "description": "Primary trade corridor via Suez Canal",
                    "key_ports": ["Shanghai", "Singapore", "Dubai", "Rotterdam", "Hamburg"],
                    "typical_disruptions": ["suez canal blockage", "red sea tensions", "monsoons"],
                    "impact_multiplier": 2.0,
                    "daily_volume_teu": 35000
                },
                "intra_asia": {
                    "description": "Regional Asian trade networks",
                    "key_ports": ["Singapore", "Hong Kong", "Busan", "Tokyo", "Manila"],
                    "typical_disruptions": ["typhoons", "political tensions", "port strikes"],
                    "impact_multiplier": 1.5,
                    "daily_volume_teu": 25000
                }
            },
            "sector_vulnerabilities": {
                "electronics": {
                    "key_regions": ["Taiwan", "South Korea", "China", "Japan"],
                    "disruption_sensitivity": "critical",
                    "recovery_time_days": 30,
                    "dependency_score": 0.9
                },
                "automotive": {
                    "key_regions": ["Germany", "Japan", "Mexico", "China"],
                    "disruption_sensitivity": "high",
                    "recovery_time_days": 21,
                    "dependency_score": 0.8
                },
                "pharmaceuticals": {
                    "key_regions": ["India", "China", "Ireland", "Puerto Rico"],
                    "disruption_sensitivity": "critical",
                    "recovery_time_days": 45,
                    "dependency_score": 0.95
                },
                "agriculture": {
                    "key_regions": ["Ukraine", "Brazil", "Argentina", "Australia"],
                    "disruption_sensitivity": "seasonal",
                    "recovery_time_days": 90,
                    "dependency_score": 0.7
                }
            },
            "disruption_patterns": {
                "weather_events": {
                    "hurricane": {"severity_multiplier": 2.0, "duration_days": 7},
                    "typhoon": {"severity_multiplier": 1.8, "duration_days": 5},
                    "flood": {"severity_multiplier": 1.5, "duration_days": 14},
                    "drought": {"severity_multiplier": 1.2, "duration_days": 60}
                },
                "geopolitical_events": {
                    "trade_war": {"severity_multiplier": 1.3, "duration_days": 180},
                    "sanctions": {"severity_multiplier": 1.7, "duration_days": 365},
                    "border_closure": {"severity_multiplier": 2.5, "duration_days": 30}
                }
            }
        }
        
        # Enhanced supply chain keywords with semantic categories
        self.supply_chain_keywords = {
            "logistics": ["supply chain", "logistics", "shipping", "transport", "cargo", "freight"],
            "infrastructure": ["port", "airport", "highway", "rail", "truck", "vessel", "container"],
            "operations": ["warehouse", "distribution", "manufacturing", "production", "assembly"],
            "disruptions": ["delay", "disruption", "shortage", "bottleneck", "congestion", "closure"],
            "events": ["strike", "accident", "weather", "storm", "flood", "earthquake", "fire"],
            "geopolitical": ["sanctions", "trade war", "border", "customs", "tariff", "embargo"]
        }
        
        # Critical supply chain locations with coordinates and importance scores
        self.critical_locations = {
            "shanghai": {"lat": 31.2304, "lon": 121.4737, "importance": 10, "type": "port"},
            "singapore": {"lat": 1.3521, "lon": 103.8198, "importance": 9, "type": "port"},
            "rotterdam": {"lat": 51.9244, "lon": 4.4777, "importance": 8, "type": "port"},
            "los_angeles": {"lat": 34.0522, "lon": -118.2437, "importance": 8, "type": "port"},
            "shenzhen": {"lat": 22.5431, "lon": 114.0579, "importance": 7, "type": "port"},
            "hamburg": {"lat": 53.5511, "lon": 9.9937, "importance": 7, "type": "port"},
            "dubai": {"lat": 25.2048, "lon": 55.2708, "importance": 6, "type": "port"},
            "hong_kong": {"lat": 22.3193, "lon": 114.1694, "importance": 6, "type": "port"},
            "suez_canal": {"lat": 30.0444, "lon": 32.3013, "importance": 10, "type": "waterway"},
            "panama_canal": {"lat": 9.0820, "lon": -79.7821, "importance": 9, "type": "waterway"}
        }

    async def detect_disruptions_ai(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """AI-powered disruption detection with RAG capabilities"""
        disruptions = []
        
        for record in data_batch:
            try:
                # Step 1: Basic relevance filtering
                if not await self._is_supply_chain_relevant_ai(record):
                    continue
                
                # Step 2: Create embeddings for semantic analysis
                embedding = await self._create_event_embedding(record)
                
                # Step 3: RAG-based context retrieval
                context = await self._retrieve_relevant_context(record, embedding)
                
                # Step 4: AI-powered disruption analysis
                ai_analysis = await self._analyze_with_ai(record, context)
                
                # Step 5: Calculate comprehensive disruption score
                disruption_score = await self._calculate_ai_disruption_score(record, ai_analysis, context)
                
                if disruption_score >= 0.3:  # AI-adjusted threshold
                    disruption = {
                        "id": f"ai_{record.get('source', 'unknown')}_{datetime.utcnow().timestamp()}",
                        "source_data": record,
                        "disruption_score": disruption_score,
                        "detected_at": datetime.utcnow().isoformat(),
                        "ai_analysis": ai_analysis,
                        "context_used": context,
                        "embedding": embedding.tolist() if embedding is not None else None,
                        "disruption_type": ai_analysis.get("disruption_type", "unknown"),
                        "affected_sectors": ai_analysis.get("affected_sectors", []),
                        "geographic_scope": ai_analysis.get("geographic_scope", "regional"),
                        "urgency_level": ai_analysis.get("urgency_level", "medium"),
                        "confidence_level": ai_analysis.get("confidence_level", 0.5),
                        "predicted_duration_days": ai_analysis.get("predicted_duration_days", 7),
                        "mitigation_suggestions": ai_analysis.get("mitigation_suggestions", [])
                    }
                    disruptions.append(disruption)
                    
            except Exception as e:
                logger.error(f"Error in AI disruption detection for record: {e}")
        
        logger.info(f"AI detected {len(disruptions)} potential disruptions from {len(data_batch)} records")
        return disruptions

    async def _is_supply_chain_relevant_ai(self, record: Dict[str, Any]) -> bool:
        """AI-enhanced supply chain relevance detection"""
        text = f"{record.get('title', '')} {record.get('description', '')}".lower()
        
        # Basic keyword check first
        basic_relevance = any(
            keyword in text 
            for category in self.supply_chain_keywords.values() 
            for keyword in category
        )
        
        if not basic_relevance:
            return False
        
        # If OpenAI is available, use AI for more sophisticated relevance detection
        if self.openai_client:
            try:
                prompt = f"""
                Analyze if this event is relevant to global supply chain operations:
                
                Title: {record.get('title', '')}
                Description: {record.get('description', '')}
                Location: {record.get('location', '')}
                Event Type: {record.get('event_type', '')}
                
                Consider:
                - Impact on logistics, shipping, manufacturing, or trade
                - Effect on critical supply chain infrastructure
                - Potential for cascading supply chain effects
                
                Respond with only: RELEVANT or NOT_RELEVANT
                """
                
                response = await self._call_openai(prompt, max_tokens=10)
                return "RELEVANT" in response.upper()
                
            except Exception as e:
                logger.error(f"Error in AI relevance check: {e}")
        
        return basic_relevance

    async def _create_event_embedding(self, record: Dict[str, Any]) -> Optional[np.ndarray]:
        """Create semantic embedding for the event"""
        try:
            text = f"{record.get('title', '')} {record.get('description', '')} {record.get('location', '')}"
            embedding = self.embedding_model.encode([text])[0]
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return None

    async def _retrieve_relevant_context(self, record: Dict[str, Any], embedding: Optional[np.ndarray]) -> Dict[str, Any]:
        """Retrieve relevant context from supply chain knowledge base using RAG"""
        context = {
            "relevant_routes": [],
            "affected_sectors": [],
            "historical_patterns": [],
            "location_importance": 0
        }
        
        try:
            location = record.get('location', '').lower()
            event_type = record.get('event_type', '')
            
            # Find relevant trade routes
            for route_name, route_info in self.supply_chain_knowledge["critical_routes"].items():
                if any(port.lower() in location for port in route_info["key_ports"]):
                    context["relevant_routes"].append({
                        "route": route_name,
                        "info": route_info
                    })
            
            # Find affected sectors based on location and event type
            for sector, sector_info in self.supply_chain_knowledge["sector_vulnerabilities"].items():
                if any(region.lower() in location for region in sector_info["key_regions"]):
                    context["affected_sectors"].append({
                        "sector": sector,
                        "info": sector_info
                    })
            
            # Get historical disruption patterns
            if event_type in ["weather", "storm", "hurricane", "typhoon"]:
                weather_patterns = self.supply_chain_knowledge["disruption_patterns"]["weather_events"]
                context["historical_patterns"] = weather_patterns
            
            # Calculate location importance
            for loc_name, loc_info in self.critical_locations.items():
                if loc_name in location:
                    context["location_importance"] = loc_info["importance"]
                    break
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
        
        return context

    async def _analyze_with_ai(self, record: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI for advanced disruption analysis"""
        default_analysis = {
            "disruption_type": "general_disruption",
            "affected_sectors": ["general"],
            "geographic_scope": "regional",
            "urgency_level": "medium",
            "confidence_level": 0.5,
            "predicted_duration_days": 7,
            "mitigation_suggestions": ["Monitor situation closely"]
        }
        
        if not self.openai_client:
            return default_analysis
        
        try:
            prompt = f"""
            As a supply chain expert, analyze this disruption event:
            
            EVENT DETAILS:
            Title: {record.get('title', '')}
            Description: {record.get('description', '')}
            Location: {record.get('location', '')}
            Event Type: {record.get('event_type', '')}
            Severity: {record.get('severity', '')}
            
            CONTEXT:
            Relevant Trade Routes: {context.get('relevant_routes', [])}
            Affected Sectors: {context.get('affected_sectors', [])}
            Location Importance (1-10): {context.get('location_importance', 0)}
            
            Provide analysis in JSON format:
            {{
                "disruption_type": "weather_event|geopolitical|infrastructure|cyber|labor|natural_disaster|other",
                "affected_sectors": ["electronics", "automotive", "pharmaceuticals", "agriculture", "energy", "retail"],
                "geographic_scope": "local|regional|national|international|global",
                "urgency_level": "low|medium|high|critical",
                "confidence_level": 0.0-1.0,
                "predicted_duration_days": number,
                "impact_severity": "minor|moderate|major|severe",
                "cascading_effects": ["list of potential cascading effects"],
                "mitigation_suggestions": ["list of actionable mitigation strategies"]
            }}
            """
            
            response = await self._call_openai(prompt, max_tokens=500)
            
            # Parse JSON response
            try:
                ai_analysis = json.loads(response)
                return ai_analysis
            except json.JSONDecodeError:
                logger.error("Failed to parse AI response as JSON")
                return default_analysis
                
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return default_analysis

    async def _calculate_ai_disruption_score(self, record: Dict[str, Any], ai_analysis: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate comprehensive disruption score using AI insights"""
        base_score = 0.0
        
        # Base score from AI confidence
        base_score += ai_analysis.get("confidence_level", 0.5) * 0.3
        
        # Impact severity multiplier
        severity_multipliers = {
            "minor": 0.2,
            "moderate": 0.5,
            "major": 0.8,
            "severe": 1.0
        }
        severity = ai_analysis.get("impact_severity", "moderate")
        base_score += severity_multipliers.get(severity, 0.5) * 0.3
        
        # Geographic scope multiplier
        scope_multipliers = {
            "local": 0.2,
            "regional": 0.4,
            "national": 0.6,
            "international": 0.8,
            "global": 1.0
        }
        scope = ai_analysis.get("geographic_scope", "regional")
        base_score += scope_multipliers.get(scope, 0.4) * 0.2
        
        # Location importance boost
        location_importance = context.get("location_importance", 0)
        if location_importance > 7:
            base_score += 0.2
        elif location_importance > 5:
            base_score += 0.1
        
        # Trade route impact
        if context.get("relevant_routes"):
            route_impact = max([route["info"]["impact_multiplier"] for route in context["relevant_routes"]])
            base_score += (route_impact - 1.0) * 0.1
        
        # Sector vulnerability
        if context.get("affected_sectors"):
            max_dependency = max([
                sector["info"]["dependency_score"] 
                for sector in context["affected_sectors"]
            ])
            base_score += max_dependency * 0.1
        
        return min(1.0, base_score)

    async def _call_openai(self, prompt: str, max_tokens: int = 150) -> str:
        """Make async call to OpenAI API"""
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return ""

    def get_supply_chain_insights(self, location: str, event_type: str) -> Dict[str, Any]:
        """Get supply chain insights for a specific location and event type"""
        insights = {
            "critical_infrastructure": [],
            "vulnerable_sectors": [],
            "trade_route_impacts": [],
            "historical_precedents": []
        }
        
        location_lower = location.lower()
        
        # Find critical infrastructure
        for loc_name, loc_info in self.critical_locations.items():
            if loc_name in location_lower:
                insights["critical_infrastructure"].append({
                    "name": loc_name,
                    "type": loc_info["type"],
                    "importance": loc_info["importance"]
                })
        
        # Find vulnerable sectors
        for sector, sector_info in self.supply_chain_knowledge["sector_vulnerabilities"].items():
            if any(region.lower() in location_lower for region in sector_info["key_regions"]):
                insights["vulnerable_sectors"].append({
                    "sector": sector,
                    "sensitivity": sector_info["disruption_sensitivity"],
                    "recovery_time": sector_info["recovery_time_days"]
                })
        
        return insights 