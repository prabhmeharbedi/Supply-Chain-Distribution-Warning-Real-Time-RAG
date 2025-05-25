from typing import Dict, Any, List
import json
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DisruptionDetector:
    def __init__(self):
        # Supply chain sectors and their keywords
        self.supply_chain_sectors = {
            "manufacturing": ["factory", "plant", "production", "assembly", "manufacturing"],
            "transportation": ["shipping", "freight", "cargo", "transport", "logistics"],
            "ports": ["port", "harbor", "terminal", "dock", "wharf"],
            "energy": ["oil", "gas", "fuel", "energy", "power", "electricity"],
            "technology": ["semiconductor", "chip", "electronics", "tech", "computer"],
            "automotive": ["car", "auto", "vehicle", "automotive", "truck"],
            "retail": ["retail", "store", "shopping", "consumer", "goods"],
            "agriculture": ["farm", "crop", "food", "agriculture", "harvest"]
        }
        
        # Major trade routes
        self.trade_routes = {
            "trans_pacific": ["pacific", "asia", "china", "japan", "korea", "california", "seattle"],
            "trans_atlantic": ["atlantic", "europe", "uk", "germany", "new york", "boston"],
            "asia_europe": ["suez", "mediterranean", "middle east", "singapore", "rotterdam"],
            "panama_canal": ["panama", "canal", "central america", "caribbean"],
            "suez_canal": ["suez", "egypt", "red sea", "mediterranean"]
        }
        
        # Disruption keywords by severity
        self.disruption_keywords = {
            "critical": ["shutdown", "closed", "suspended", "halted", "blocked", "collapsed"],
            "warning": ["delayed", "disrupted", "reduced", "limited", "restricted", "strike"],
            "watch": ["monitoring", "potential", "risk", "concern", "weather", "planned"]
        }
    
    def detect_disruptions(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect supply chain disruptions from incoming data"""
        disruptions = []
        
        for record in data_batch:
            try:
                # Basic filtering - must be supply chain relevant
                if not self._is_supply_chain_relevant(record):
                    continue
                
                # Calculate disruption probability
                disruption_score = self._calculate_disruption_score(record)
                
                if disruption_score >= 0.3:  # Threshold for potential disruption
                    disruption = {
                        "id": f"{record.get('source', 'unknown')}_{datetime.utcnow().timestamp()}",
                        "source_data": record,
                        "disruption_score": disruption_score,
                        "detected_at": datetime.utcnow().isoformat(),
                        "disruption_type": self._classify_disruption_type(record),
                        "affected_sectors": self._identify_affected_sectors(record),
                        "geographic_scope": self._determine_geographic_scope(record),
                        "urgency_level": self._assess_urgency(record, disruption_score),
                        "keywords_matched": self._extract_matched_keywords(record)
                    }
                    disruptions.append(disruption)
                    
            except Exception as e:
                logger.error(f"Error processing record for disruption detection: {e}")
        
        logger.info(f"Detected {len(disruptions)} potential disruptions from {len(data_batch)} records")
        return disruptions
    
    def _is_supply_chain_relevant(self, record: Dict[str, Any]) -> bool:
        """Check if record is relevant to supply chain operations"""
        text = f"{record.get('title', '')} {record.get('description', '')}".lower()
        
        # Must contain supply chain related terms
        supply_chain_terms = [
            "supply chain", "logistics", "shipping", "freight", "cargo",
            "port", "warehouse", "manufacturing", "factory", "trade",
            "import", "export", "customs", "border", "transportation",
            "distribution", "procurement", "supplier", "vendor"
        ]
        
        return any(term in text for term in supply_chain_terms)
    
    def _calculate_disruption_score(self, record: Dict[str, Any]) -> float:
        """Calculate probability that this record indicates a supply chain disruption"""
        text = f"{record.get('title', '')} {record.get('description', '')}".lower()
        score = 0.0
        
        # Check for disruption keywords
        for severity, keywords in self.disruption_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in text)
            if severity == "critical":
                score += keyword_count * 0.3
            elif severity == "warning":
                score += keyword_count * 0.2
            elif severity == "watch":
                score += keyword_count * 0.1
        
        # Boost score for specific event types
        event_type = record.get("event_type", "")
        if event_type == "earthquake":
            magnitude = record.get("magnitude", 0)
            if magnitude >= 6.0:
                score += 0.4
            elif magnitude >= 5.0:
                score += 0.2
        elif event_type == "weather":
            severity = record.get("severity", "")
            if severity == "critical":
                score += 0.3
            elif severity == "warning":
                score += 0.2
        
        # Boost score for critical locations
        location = record.get("location", "").lower()
        critical_locations = [
            "suez canal", "panama canal", "strait of hormuz",
            "los angeles", "long beach", "shanghai", "singapore",
            "rotterdam", "hamburg", "new york"
        ]
        
        if any(loc in location for loc in critical_locations):
            score += 0.2
        
        # Factor in existing confidence score
        confidence = record.get("confidence_score", 0.5)
        score *= confidence
        
        return min(1.0, score)
    
    def _classify_disruption_type(self, record: Dict[str, Any]) -> str:
        """Classify the type of disruption"""
        text = f"{record.get('title', '')} {record.get('description', '')}".lower()
        event_type = record.get("event_type", "")
        
        # Direct event type mapping
        if event_type == "earthquake":
            return "natural_disaster"
        elif event_type == "weather":
            return "weather_event"
        
        # Keyword-based classification
        if any(word in text for word in ["strike", "labor", "union", "workers"]):
            return "labor_disruption"
        elif any(word in text for word in ["cyber", "hack", "security", "breach"]):
            return "cyber_incident"
        elif any(word in text for word in ["fire", "explosion", "accident", "incident"]):
            return "facility_incident"
        elif any(word in text for word in ["border", "customs", "tariff", "trade war"]):
            return "trade_policy"
        elif any(word in text for word in ["shortage", "supply", "material", "component"]):
            return "supply_shortage"
        elif any(word in text for word in ["transport", "shipping", "freight", "logistics"]):
            return "transportation_disruption"
        else:
            return "general_disruption"
    
    def _identify_affected_sectors(self, record: Dict[str, Any]) -> List[str]:
        """Identify which supply chain sectors are affected"""
        text = f"{record.get('title', '')} {record.get('description', '')}".lower()
        affected_sectors = []
        
        for sector, keywords in self.supply_chain_sectors.items():
            if any(keyword in text for keyword in keywords):
                affected_sectors.append(sector)
        
        return affected_sectors if affected_sectors else ["general"]
    
    def _determine_geographic_scope(self, record: Dict[str, Any]) -> str:
        """Determine the geographic scope of the disruption"""
        location = record.get("location", "").lower()
        
        # Check for global trade routes
        for route, keywords in self.trade_routes.items():
            if any(keyword in location for keyword in keywords):
                return f"trade_route_{route}"
        
        # Check for specific regions
        if any(region in location for region in ["asia", "pacific", "china", "japan"]):
            return "asia_pacific"
        elif any(region in location for region in ["europe", "eu", "uk", "germany"]):
            return "europe"
        elif any(region in location for region in ["america", "usa", "canada", "mexico"]):
            return "north_america"
        elif any(region in location for region in ["middle east", "gulf", "arabia"]):
            return "middle_east"
        else:
            return "regional"
    
    def _assess_urgency(self, record: Dict[str, Any], disruption_score: float) -> str:
        """Assess the urgency level of the disruption"""
        severity = record.get("severity", "watch")
        
        if disruption_score >= 0.8 or severity == "critical":
            return "immediate"
        elif disruption_score >= 0.6 or severity == "warning":
            return "high"
        elif disruption_score >= 0.4 or severity == "watch":
            return "medium"
        else:
            return "low"
    
    def _extract_matched_keywords(self, record: Dict[str, Any]) -> List[str]:
        """Extract keywords that matched disruption patterns"""
        text = f"{record.get('title', '')} {record.get('description', '')}".lower()
        matched_keywords = []
        
        for severity, keywords in self.disruption_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    matched_keywords.append(keyword)
        
        return matched_keywords 