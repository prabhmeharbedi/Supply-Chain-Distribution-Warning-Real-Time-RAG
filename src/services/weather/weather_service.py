import requests
import pathway as pw
from typing import Dict, Any, List
from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Major supply chain locations to monitor
        self.key_locations = [
            {"name": "Los Angeles Port", "lat": 33.7361, "lon": -118.2639},
            {"name": "Long Beach Port", "lat": 33.7701, "lon": -118.2137},
            {"name": "New York Port", "lat": 40.6892, "lon": -74.0445},
            {"name": "Shanghai Port", "lat": 31.2304, "lon": 121.4737},
            {"name": "Singapore Port", "lat": 1.2966, "lon": 103.8764},
            {"name": "Rotterdam Port", "lat": 51.9225, "lon": 4.4792},
            {"name": "Hamburg Port", "lat": 53.5511, "lon": 9.9937},
            {"name": "Suez Canal", "lat": 30.5234, "lon": 32.2569},
            {"name": "Panama Canal", "lat": 9.0820, "lon": -79.7674},
        ]
        
    def get_weather_alerts(self) -> List[Dict[str, Any]]:
        """Fetch weather alerts for key supply chain locations"""
        alerts = []
        
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
            return alerts
            
        for location in self.key_locations:
            try:
                url = f"{self.base_url}/onecall"
                params = {
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "appid": self.api_key,
                    "exclude": "minutely,hourly,daily"
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if "alerts" in data:
                    for alert in data["alerts"]:
                        alerts.append({
                            "source": "weather",
                            "event_type": "weather",
                            "title": alert.get("event", "Weather Alert"),
                            "description": alert.get("description", ""),
                            "severity": self._map_severity(alert.get("tags", [])),
                            "location": location["name"],
                            "latitude": location["lat"],
                            "longitude": location["lon"],
                            "start_time": alert.get("start"),
                            "end_time": alert.get("end"),
                            "raw_data": alert
                        })
                        
                # Also check current weather for severe conditions
                current_weather = data.get("current", {})
                weather_conditions = current_weather.get("weather", [])
                
                for condition in weather_conditions:
                    if self._is_severe_weather(condition):
                        alerts.append({
                            "source": "weather",
                            "event_type": "weather",
                            "title": f"Severe Weather: {condition.get('main', 'Unknown')}",
                            "description": condition.get("description", ""),
                            "severity": self._map_weather_severity(condition),
                            "location": location["name"],
                            "latitude": location["lat"],
                            "longitude": location["lon"],
                            "raw_data": condition
                        })
                        
            except Exception as e:
                logger.error(f"Error fetching weather data for {location['name']}: {e}")
        
        logger.info(f"Fetched {len(alerts)} weather alerts")
        return alerts
    
    def _map_severity(self, tags: List[str]) -> str:
        """Map weather alert tags to severity levels"""
        if any(tag.lower() in ["extreme", "severe"] for tag in tags):
            return "critical"
        elif any(tag.lower() in ["moderate", "minor"] for tag in tags):
            return "warning"
        else:
            return "watch"
    
    def _is_severe_weather(self, condition: Dict[str, Any]) -> bool:
        """Check if weather condition is severe enough to impact supply chains"""
        severe_conditions = [
            "thunderstorm", "tornado", "hurricane", "typhoon",
            "blizzard", "ice storm", "heavy snow", "freezing rain",
            "extreme cold", "extreme heat", "dust storm", "sandstorm"
        ]
        
        main = condition.get("main", "").lower()
        description = condition.get("description", "").lower()
        
        return any(severe in main or severe in description for severe in severe_conditions)
    
    def _map_weather_severity(self, condition: Dict[str, Any]) -> str:
        """Map weather condition to severity level"""
        main = condition.get("main", "").lower()
        description = condition.get("description", "").lower()
        
        critical_conditions = ["tornado", "hurricane", "typhoon", "blizzard"]
        warning_conditions = ["thunderstorm", "heavy snow", "ice storm"]
        
        if any(crit in main or crit in description for crit in critical_conditions):
            return "critical"
        elif any(warn in main or warn in description for warn in warning_conditions):
            return "warning"
        else:
            return "watch" 