import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EarthquakeService:
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
        # Major supply chain regions to monitor
        self.supply_chain_regions = {
            "California Ports": {"min_lat": 32.0, "max_lat": 38.0, "min_lon": -125.0, "max_lon": -117.0},
            "Japan Manufacturing": {"min_lat": 30.0, "max_lat": 46.0, "min_lon": 129.0, "max_lon": 146.0},
            "Turkey Trade Route": {"min_lat": 35.0, "max_lat": 42.0, "min_lon": 25.0, "max_lon": 45.0},
            "Chile Mining": {"min_lat": -56.0, "max_lat": -17.0, "min_lon": -76.0, "max_lon": -66.0},
            "Indonesia Shipping": {"min_lat": -11.0, "max_lat": 6.0, "min_lon": 95.0, "max_lon": 141.0},
            "Mediterranean Trade": {"min_lat": 30.0, "max_lat": 47.0, "min_lon": -6.0, "max_lon": 42.0},
        }
        
    def get_earthquake_alerts(self) -> List[Dict[str, Any]]:
        """Fetch recent earthquake data that could impact supply chains"""
        alerts = []
        
        # Get earthquakes from the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        try:
            params = {
                "format": "geojson",
                "starttime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "endtime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "minmagnitude": 4.0,  # Only significant earthquakes
                "orderby": "time-asc"
            }
            
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            for feature in data.get("features", []):
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                coordinates = geometry.get("coordinates", [])
                
                if len(coordinates) >= 2:
                    longitude, latitude = coordinates[0], coordinates[1]
                    magnitude = properties.get("mag", 0)
                    
                    # Check if earthquake is in a supply chain critical region
                    affected_region = self._get_affected_region(latitude, longitude)
                    if affected_region or magnitude >= 6.0:  # Include all major earthquakes
                        
                        alert = {
                            "source": "earthquake",
                            "event_type": "earthquake",
                            "title": f"Magnitude {magnitude} Earthquake",
                            "description": f"Earthquake detected near {properties.get('place', 'Unknown location')}",
                            "severity": self._calculate_severity(magnitude, affected_region),
                            "location": properties.get("place", "Unknown"),
                            "latitude": latitude,
                            "longitude": longitude,
                            "magnitude": magnitude,
                            "depth": coordinates[2] if len(coordinates) > 2 else None,
                            "time": properties.get("time"),
                            "affected_region": affected_region,
                            "confidence_score": self._calculate_confidence(magnitude, properties),
                            "raw_data": feature
                        }
                        alerts.append(alert)
            
            logger.info(f"Fetched {len(alerts)} earthquake alerts")
            
        except Exception as e:
            logger.error(f"Error fetching earthquake data: {e}")
        
        return alerts
    
    def _get_affected_region(self, latitude: float, longitude: float) -> str:
        """Determine which supply chain region is affected by the earthquake"""
        for region_name, bounds in self.supply_chain_regions.items():
            if (bounds["min_lat"] <= latitude <= bounds["max_lat"] and
                bounds["min_lon"] <= longitude <= bounds["max_lon"]):
                return region_name
        return ""
    
    def _calculate_severity(self, magnitude: float, affected_region: str) -> str:
        """Calculate severity based on magnitude and location"""
        # Base severity on magnitude
        if magnitude >= 7.0:
            base_severity = "critical"
        elif magnitude >= 6.0:
            base_severity = "warning"
        elif magnitude >= 5.0:
            base_severity = "watch"
        else:
            base_severity = "info"
        
        # Increase severity if in critical supply chain region
        if affected_region:
            if magnitude >= 6.0:
                return "critical"
            elif magnitude >= 5.0:
                return "warning"
            elif magnitude >= 4.5:
                return "watch"
        
        return base_severity
    
    def _calculate_confidence(self, magnitude: float, properties: Dict[str, Any]) -> float:
        """Calculate confidence score for earthquake impact"""
        confidence = 0.7  # Base confidence for earthquake data (generally reliable)
        
        # Increase confidence for higher magnitudes
        if magnitude >= 6.0:
            confidence += 0.2
        elif magnitude >= 5.0:
            confidence += 0.1
        
        # Check data quality indicators
        if properties.get("status") == "reviewed":
            confidence += 0.1
        
        # Reduce confidence for very deep earthquakes (less surface impact)
        depth = properties.get("depth", 0)
        if depth > 100:  # Very deep earthquake
            confidence -= 0.1
        
        return min(1.0, max(0.1, confidence)) 