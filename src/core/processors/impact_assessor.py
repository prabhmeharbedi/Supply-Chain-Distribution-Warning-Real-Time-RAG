from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ImpactAssessor:
    def __init__(self):
        # Trade routes and their daily trade volumes (in millions USD)
        self.trade_routes = {
            "trans_pacific": {
                "daily_volume": 50,
                "locations": ["pacific", "asia", "china", "japan", "korea", "california", "seattle"]
            },
            "trans_atlantic": {
                "daily_volume": 30,
                "locations": ["atlantic", "europe", "uk", "germany", "new york", "boston"]
            },
            "asia_europe": {
                "daily_volume": 40,
                "locations": ["suez", "mediterranean", "middle east", "singapore", "rotterdam"]
            },
            "panama_canal": {
                "daily_volume": 200,
                "locations": ["panama", "canal", "central america", "caribbean"]
            },
            "suez_canal": {
                "daily_volume": 300,
                "locations": ["suez", "egypt", "red sea", "mediterranean"]
            }
        }
        
    def assess_impact(self, disruption: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the comprehensive impact of a detected disruption"""
        try:
            source_data = disruption.get("source_data", {})
            
            # Calculate impact score
            impact_score = self._calculate_impact_score(disruption)
            
            # Estimate duration
            duration_estimate = self._estimate_duration(disruption)
            
            # Identify affected routes
            affected_routes = self._identify_affected_routes(disruption)
            
            # Estimate financial impact
            financial_impact = self._estimate_financial_impact(
                impact_score, affected_routes, duration_estimate
            )
            
            # Generate mitigation strategies
            mitigation_strategies = self._generate_mitigation_strategies(
                disruption, impact_score
            )
            
            impact_assessment = {
                "disruption_id": disruption.get("id"),
                "impact_score": round(impact_score, 3),
                "severity_level": self._determine_severity_level(impact_score),
                "duration_estimate": duration_estimate,
                "affected_routes": affected_routes,
                "financial_impact": financial_impact,
                "mitigation_strategies": mitigation_strategies,
                "assessed_at": datetime.utcnow().isoformat()
            }
            
            return impact_assessment
            
        except Exception as e:
            logger.error(f"Error assessing impact for disruption {disruption.get('id')}: {e}")
            return {"error": str(e), "disruption_id": disruption.get("id")}
    
    def _calculate_impact_score(self, disruption: Dict[str, Any]) -> float:
        """Calculate overall impact score (0-1)"""
        base_score = disruption.get("disruption_score", 0.5)
        
        # Factor in geographic scope
        geographic_scope = disruption.get("geographic_scope", "regional")
        if "trade_route" in geographic_scope:
            base_score *= 1.3
        elif geographic_scope in ["asia_pacific", "europe", "north_america"]:
            base_score *= 1.1
        
        # Factor in urgency level
        urgency = disruption.get("urgency_level", "low")
        urgency_multipliers = {
            "immediate": 1.3,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.8
        }
        base_score *= urgency_multipliers.get(urgency, 1.0)
        
        return min(1.0, base_score)
    
    def _estimate_duration(self, disruption: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate how long the disruption might last"""
        disruption_type = disruption.get("disruption_type", "general_disruption")
        source_data = disruption.get("source_data", {})
        severity = source_data.get("severity", "watch")
        
        # Duration estimates by type and severity
        duration_map = {
            "earthquake": {"critical": 14, "warning": 5, "watch": 2},
            "weather": {"critical": 7, "warning": 3, "watch": 1},
            "labor_disruption": {"critical": 21, "warning": 7, "watch": 2},
            "transportation_disruption": {"critical": 10, "warning": 3, "watch": 1}
        }
        
        avg_days = duration_map.get(disruption_type, {}).get(severity, 3)
        
        return {
            "estimated_avg_days": avg_days,
            "confidence": 0.7 if disruption_type in duration_map else 0.4
        }
    
    def _identify_affected_routes(self, disruption: Dict[str, Any]) -> List[str]:
        """Identify which trade routes might be affected"""
        source_data = disruption.get("source_data", {})
        location = source_data.get("location", "").lower()
        
        affected_routes = []
        
        for route_name, route_data in self.trade_routes.items():
            if any(loc in location for loc in route_data["locations"]):
                affected_routes.append(route_name)
        
        return affected_routes
    
    def _estimate_financial_impact(self, impact_score: float, affected_routes: List[str], 
                                 duration_estimate: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate financial impact in monetary terms"""
        
        total_daily_impact = 0
        
        for route in affected_routes:
            if route in self.trade_routes:
                daily_volume = self.trade_routes[route]["daily_volume"]
                route_impact = daily_volume * impact_score
                total_daily_impact += route_impact
        
        # If no specific routes, estimate based on general impact
        if not affected_routes:
            total_daily_impact = 10 * impact_score  # Base estimate
        
        avg_duration = duration_estimate.get("estimated_avg_days", 3)
        
        return {
            "daily_impact_usd_millions": round(total_daily_impact, 1),
            "weekly_impact_usd_millions": round(total_daily_impact * 7, 1),
            "estimated_total_impact_usd_millions": round(total_daily_impact * avg_duration, 1),
            "affected_trade_volume_percent": round(impact_score * 100, 1)
        }
    
    def _generate_mitigation_strategies(self, disruption: Dict[str, Any], 
                                      impact_score: float) -> List[str]:
        """Generate mitigation strategies based on disruption type and impact"""
        disruption_type = disruption.get("disruption_type", "")
        
        strategies = []
        
        # High-impact general strategies
        if impact_score >= 0.7:
            strategies.extend([
                "Activate emergency procurement protocols",
                "Contact backup suppliers immediately",
                "Consider expedited shipping for critical items",
                "Increase safety stock levels for affected routes"
            ])
        
        # Type-specific strategies
        if disruption_type == "weather_event":
            strategies.extend([
                "Monitor weather forecasts for route planning",
                "Consider alternative transportation modes",
                "Coordinate with logistics partners for rerouting"
            ])
        elif disruption_type == "natural_disaster":
            strategies.extend([
                "Assess supplier facility damage",
                "Activate disaster recovery plans",
                "Consider temporary supplier alternatives"
            ])
        elif disruption_type == "transportation_disruption":
            strategies.extend([
                "Explore alternative routes and carriers",
                "Negotiate priority handling with logistics providers",
                "Consider multimodal transportation options"
            ])
        
        return strategies
    
    def _determine_severity_level(self, impact_score: float) -> str:
        """Determine severity level based on impact score"""
        if impact_score >= 0.8:
            return "critical"
        elif impact_score >= 0.6:
            return "high"
        elif impact_score >= 0.4:
            return "medium"
        else:
            return "low" 