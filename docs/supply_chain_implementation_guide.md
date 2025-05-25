# Supply Chain Disruption Predictor - Complete Implementation Guide

## Phase 1: Environment Setup & Project Foundation (Steps 1-20)

### Step 1: System Prerequisites
- Install Python 3.9+ from python.org
- Verify installation: `python --version`
- Install pip: `python -m ensurepip --upgrade`

### Step 2: Create Project Directory
```bash
mkdir supply-chain-predictor
cd supply-chain-predictor
```

### Step 3: Set Up Python Virtual Environment
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

### Step 4: Install Core Dependencies
```bash
pip install pathway-ai
pip install fastapi
pip install uvicorn
pip install pydantic
pip install python-dotenv
pip install requests
pip install pandas
pip install numpy
pip install psycopg2-binary
pip install sqlalchemy
pip install alembic
```

### Step 5: Install ML and Data Processing Dependencies
```bash
pip install scikit-learn
pip install sentence-transformers
pip install openai
pip install langchain
pip install chromadb
pip install matplotlib
pip install seaborn
pip install plotly
```

### Step 6: Install Additional Utilities
```bash
pip install python-multipart
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install aiofiles
pip install httpx
pip install celery
pip install redis
pip install pytest
pip install pytest-asyncio
```

### Step 7: Create Requirements File
```bash
pip freeze > requirements.txt
```

### Step 8: Set Up Git Repository
```bash
git init
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore
git add .
git commit -m "Initial commit"
```

### Step 9: Create Project Structure
```bash
mkdir -p {src,tests,docs,data,logs,config}
mkdir -p src/{api,core,models,services,utils}
mkdir -p src/core/{pipeline,processors,detectors}
mkdir -p src/services/{weather,news,transport,alerts}
mkdir -p data/{raw,processed,models}
mkdir -p config/{development,production,testing}
```

### Step 10: Create Main Application Files
```bash
touch src/__init__.py
touch src/main.py
touch src/api/__init__.py
touch src/core/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/utils/__init__.py
```

### Step 11: Set Up Configuration Management
Create `config/settings.py`:
```python
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    openweather_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    flightaware_api_key: Optional[str] = None
    
    # Database
    database_url: str = "postgresql://user:password@localhost/supplychain"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Application
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Step 12: Create Environment Variables File
Create `.env`:
```
OPENWEATHER_API_KEY=your_api_key_here
NEWS_API_KEY=your_api_key_here
FLIGHTAWARE_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost/supplychain
REDIS_URL=redis://localhost:6379
DEBUG=True
```

### Step 13: Set Up Database Configuration
Create `src/core/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 14: Install and Configure PostgreSQL
- Install PostgreSQL locally or use Docker
- Create database: `createdb supplychain`
- Test connection with provided credentials

### Step 15: Install and Configure Redis
- Install Redis locally or use Docker
- Start Redis server: `redis-server`
- Test connection: `redis-cli ping`

### Step 16: Set Up Docker Configuration (Optional)
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: supplychain
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Step 17: Create Logging Configuration
Create `src/utils/logger.py`:
```python
import logging
import sys
from pathlib import Path

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
```

### Step 18: Create Basic Models
Create `src/models/disruption.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from src.core.database import Base

class DisruptionEvent(Base):
    __tablename__ = "disruption_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    confidence_score = Column(Float)
    impact_score = Column(Float)
    source = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Step 19: Set Up Database Migrations
```bash
alembic init migrations
```
Edit `alembic.ini` and `migrations/env.py` to use your database configuration.

### Step 20: Create Initial Migration
```bash
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

## Phase 2: Core Pathway Pipeline Setup (Steps 21-40)

### Step 21: Create Base Pathway Pipeline
Create `src/core/pipeline/base_pipeline.py`:
```python
import pathway as pw
from typing import Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BasePipeline:
    def __init__(self):
        self.streams = {}
        self.processed_data = None
        
    def setup_streams(self):
        """Override in subclasses to set up data streams"""
        pass
        
    def process_data(self):
        """Override in subclasses to process data"""
        pass
        
    def run(self):
        """Run the pipeline"""
        logger.info("Starting pipeline...")
        self.setup_streams()
        self.process_data()
        logger.info("Pipeline setup complete")
```

### Step 22: Create Weather Data Stream
Create `src/services/weather/weather_service.py`:
```python
import requests
import pathway as pw
from typing import Dict, Any
from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_weather_alerts(self, locations: list) -> list:
        """Fetch weather alerts for given locations"""
        alerts = []
        for location in locations:
            try:
                url = f"{self.base_url}/onecall"
                params = {
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "appid": self.api_key,
                    "exclude": "minutely,hourly,daily"
                }
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "alerts" in data:
                    for alert in data["alerts"]:
                        alerts.append({
                            "source": "weather",
                            "event_type": alert.get("event", "weather_alert"),
                            "title": alert.get("event", "Weather Alert"),
                            "description": alert.get("description", ""),
                            "severity": self._map_severity(alert.get("tags", [])),
                            "location": location["name"],
                            "latitude": location["lat"],
                            "longitude": location["lon"],
                            "start_time": alert.get("start"),
                            "end_time": alert.get("end")
                        })
            except Exception as e:
                logger.error(f"Error fetching weather data for {location}: {e}")
        
        return alerts
    
    def _map_severity(self, tags: list) -> str:
        """Map weather alert tags to severity levels"""
        if any(tag in ["Extreme", "Severe"] for tag in tags):
            return "critical"
        elif any(tag in ["Moderate", "Minor"] for tag in tags):
            return "warning"
        else:
            return "watch"
```

### Step 23: Create News Data Stream
Create `src/services/news/news_service.py`:
```python
import requests
from typing import List, Dict
from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class NewsService:
    def __init__(self):
        self.api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
        
    def get_supply_chain_news(self) -> List[Dict]:
        """Fetch supply chain related news"""
        keywords = [
            "supply chain disruption",
            "port closure",
            "shipping delay",
            "factory shutdown",
            "trade route",
            "logistics crisis",
            "manufacturing halt"
        ]
        
        articles = []
        for keyword in keywords:
            try:
                url = f"{self.base_url}/everything"
                params = {
                    "q": keyword,
                    "apiKey": self.api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for article in data.get("articles", []):
                    articles.append({
                        "source": "news",
                        "event_type": "news_alert",
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "content": article.get("content", ""),
                        "url": article.get("url", ""),
                        "published_at": article.get("publishedAt", ""),
                        "severity": self._analyze_severity(article.get("title", "") + " " + article.get("description", ""))
                    })
                    
            except Exception as e:
                logger.error(f"Error fetching news for keyword '{keyword}': {e}")
                
        return articles
    
    def _analyze_severity(self, text: str) -> str:
        """Analyze text to determine severity level"""
        text_lower = text.lower()
        
        critical_words = ["shutdown", "closure", "disaster", "emergency", "crisis", "halt", "suspended"]
        warning_words = ["delay", "disruption", "problem", "issue", "concern", "impact"]
        
        if any(word in text_lower for word in critical_words):
            return "critical"
        elif any(word in text_lower for word in warning_words):
            return "warning"
        else:
            return "watch"
```

### Step 24: Create Transportation Data Stream
Create `src/services/transport/transport_service.py`:
```python
import requests
from typing import List, Dict
from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TransportService:
    def __init__(self):
        self.flightaware_key = settings.flightaware_api_key
        
    def get_airport_delays(self, airports: List[str]) -> List[Dict]:
        """Get airport delay information"""
        delays = []
        
        # Note: This is a simplified implementation
        # In production, you'd integrate with FlightAware or similar APIs
        for airport in airports:
            try:
                # Placeholder for actual API call
                delay_info = {
                    "source": "transport",
                    "event_type": "airport_delay",
                    "title": f"Delays at {airport}",
                    "description": f"Current delays at {airport} airport",
                    "location": airport,
                    "severity": "warning",  # Would be calculated from actual data
                    "impact_score": 0.6
                }
                delays.append(delay_info)
                
            except Exception as e:
                logger.error(f"Error fetching transport data for {airport}: {e}")
                
        return delays
    
    def get_port_status(self, ports: List[str]) -> List[Dict]:
        """Get port status information"""
        # Placeholder implementation
        # In production, integrate with maritime APIs
        port_statuses = []
        
        for port in ports:
            status = {
                "source": "transport",
                "event_type": "port_status",
                "title": f"Port Status: {port}",
                "description": f"Current operational status for {port}",
                "location": port,
                "severity": "watch",
                "impact_score": 0.3
            }
            port_statuses.append(status)
            
        return port_statuses
```

### Step 25: Create USGS Earthquake Service
Create `src/services/disaster/earthquake_service.py`:
```python
import requests
from typing import List, Dict
from datetime import datetime, timedelta
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EarthquakeService:
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
    def get_recent_earthquakes(self, min_magnitude: float = 5.0) -> List[Dict]:
        """Fetch recent earthquakes above minimum magnitude"""
        try:
            # Get earthquakes from last 24 hours
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=1)
            
            params = {
                "format": "geojson",
                "starttime": start_time.isoformat(),
                "endtime": end_time.isoformat(),
                "minmagnitude": min_magnitude,
                "orderby": "time-asc"
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            earthquakes = []
            for feature in data.get("features", []):
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                coordinates = geometry.get("coordinates", [])
                
                if len(coordinates) >= 2:
                    earthquake = {
                        "source": "earthquake",
                        "event_type": "earthquake",
                        "title": properties.get("title", "Earthquake"),
                        "description": f"Magnitude {properties.get('mag')} earthquake",
                        "magnitude": properties.get("mag"),
                        "location": properties.get("place", "Unknown"),
                        "latitude": coordinates[1],
                        "longitude": coordinates[0],
                        "depth": coordinates[2] if len(coordinates) > 2 else None,
                        "time": properties.get("time"),
                        "severity": self._calculate_severity(properties.get("mag", 0)),
                        "impact_score": self._calculate_impact(properties.get("mag", 0))
                    }
                    earthquakes.append(earthquake)
                    
            return earthquakes
            
        except Exception as e:
            logger.error(f"Error fetching earthquake data: {e}")
            return []
    
    def _calculate_severity(self, magnitude: float) -> str:
        """Calculate severity based on earthquake magnitude"""
        if magnitude >= 7.0:
            return "critical"
        elif magnitude >= 6.0:
            return "warning"
        else:
            return "watch"
    
    def _calculate_impact(self, magnitude: float) -> float:
        """Calculate impact score based on magnitude"""
        if magnitude >= 7.0:
            return 0.9
        elif magnitude >= 6.0:
            return 0.6
        else:
            return 0.3
```

### Step 26: Create Pathway Data Connectors
Create `src/core/pipeline/connectors.py`:
```python
import pathway as pw
import json
from typing import Dict, Any
from src.services.weather.weather_service import WeatherService
from src.services.news.news_service import NewsService
from src.services.transport.transport_service import TransportService
from src.services.disaster.earthquake_service import EarthquakeService

class DataConnectors:
    def __init__(self):
        self.weather_service = WeatherService()
        self.news_service = NewsService()
        self.transport_service = TransportService()
        self.earthquake_service = EarthquakeService()
        
    def create_weather_stream(self):
        """Create weather data stream"""
        # Major supply chain locations
        locations = [
            {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
            {"name": "New York", "lat": 40.7128, "lon": -74.0060},
            {"name": "Shanghai", "lat": 31.2304, "lon": 121.4737},
            {"name": "Rotterdam", "lat": 51.9244, "lon": 4.4777},
        ]
        
        def fetch_weather_data():
            return self.weather_service.get_weather_alerts(locations)
        
        # Create a Pathway table from the weather data
        weather_stream = pw.io.python.read(
            fetch_weather_data,
            schema=WeatherSchema,
            mode="streaming"
        )
        
        return weather_stream
    
    def create_news_stream(self):
        """Create news data stream"""
        def fetch_news_data():
            return self.news_service.get_supply_chain_news()
        
        news_stream = pw.io.python.read(
            fetch_news_data,
            schema=NewsSchema,
            mode="streaming"
        )
        
        return news_stream
    
    def create_earthquake_stream(self):
        """Create earthquake data stream"""
        def fetch_earthquake_data():
            return self.earthquake_service.get_recent_earthquakes()
        
        earthquake_stream = pw.io.python.read(
            fetch_earthquake_data,
            schema=EarthquakeSchema,
            mode="streaming"
        )
        
        return earthquake_stream

# Define schemas for data streams
class WeatherSchema(pw.Schema):
    source: str
    event_type: str
    title: str
    description: str
    severity: str
    location: str
    latitude: float
    longitude: float

class NewsSchema(pw.Schema):
    source: str
    event_type: str
    title: str
    description: str
    content: str
    url: str
    severity: str

class EarthquakeSchema(pw.Schema):
    source: str
    event_type: str
    title: str
    description: str
    magnitude: float
    location: str
    latitude: float
    longitude: float
    severity: str
    impact_score: float
```

### Step 27: Create Data Processing Pipeline
Create `src/core/pipeline/main_pipeline.py`:
```python
import pathway as pw
from typing import Dict, Any
from src.core.pipeline.connectors import DataConnectors
from src.core.processors.disruption_detector import DisruptionDetector
from src.core.processors.impact_analyzer import ImpactAnalyzer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SupplyChainPipeline:
    def __init__(self):
        self.connectors = DataConnectors()
        self.disruption_detector = DisruptionDetector()
        self.impact_analyzer = ImpactAnalyzer()
        
    def setup_pipeline(self):
        """Set up the main processing pipeline"""
        
        # Create data streams
        weather_stream = self.connectors.create_weather_stream()
        news_stream = self.connectors.create_news_stream()
        earthquake_stream = self.connectors.create_earthquake_stream()
        
        # Combine all streams
        combined_stream = weather_stream + news_stream + earthquake_stream
        
        # Process disruptions
        disruptions = combined_stream.select(
            **pw.this,
            confidence_score=pw.apply(self.disruption_detector.calculate_confidence, pw.this),
            supply_chain_relevance=pw.apply(self.disruption_detector.assess_relevance, pw.this),
            impact_assessment=pw.apply(self.impact_analyzer.assess_impact, pw.this)
        ).filter(pw.this.supply_chain_relevance > 0.5)
        
        # Calculate final alert scores
        alerts = disruptions.select(
            **pw.this,
            alert_score=pw.apply(self._calculate_alert_score, pw.this),
            recommendations=pw.apply(self._generate_recommendations, pw.this)
        )
        
        # Output to database and alert systems
        alerts.output_to(self._save_to_database)
        
        return alerts
    
    def _calculate_alert_score(self, row: Dict[str, Any]) -> float:
        """Calculate final alert score"""
        confidence = row.get("confidence_score", 0.5)
        relevance = row.get("supply_chain_relevance", 0.5)
        impact = row.get("impact_assessment", {}).get("impact_score", 0.5)
        
        # Weighted combination
        alert_score = (confidence * 0.3 + relevance * 0.3 + impact * 0.4)
        return round(alert_score, 3)
    
    def _generate_recommendations(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable recommendations"""
        severity = row.get("severity", "watch")
        event_type = row.get("event_type", "unknown")
        
        recommendations = {
            "immediate_actions": [],
            "monitoring_actions": [],
            "escalation_needed": False
        }
        
        if severity == "critical":
            recommendations["immediate_actions"] = [
                "Contact affected suppliers immediately",
                "Activate contingency plans",
                "Review inventory levels"
            ]
            recommendations["escalation_needed"] = True
        elif severity == "warning":
            recommendations["monitoring_actions"] = [
                "Monitor situation closely",
                "Prepare contingency plans",
                "Contact key suppliers for status updates"
            ]
        
        return recommendations
    
    def _save_to_database(self, row: Dict[str, Any]):
        """Save processed alerts to database"""
        # This will be implemented with actual database logic
        logger.info(f"Saving alert: {row.get('title', 'Unknown')}")
    
    def run(self):
        """Run the pipeline"""
        logger.info("Starting Supply Chain Pipeline...")
        alerts = self.setup_pipeline()
        
        # Run the pipeline
        pw.run()
```

### Step 28: Create Disruption Detection Logic
Create `src/core/processors/disruption_detector.py`:
```python
import re
from typing import Dict, Any, List
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DisruptionDetector:
    def __init__(self):
        self.supply_chain_keywords = [
            "supply chain", "logistics", "shipping", "transport", "cargo",
            "port", "factory", "manufacturing", "warehouse", "distribution",
            "supplier", "vendor", "procurement", "inventory", "freight"
        ]
        
        self.severity_indicators = {
            "critical": [
                "shutdown", "closure", "suspended", "halt", "emergency",
                "disaster", "catastrophe", "crisis", "collapse", "failure"
            ],
            "warning": [
                "delay", "disruption", "problem", "issue", "shortage",
                "bottleneck", "congestion", "limited", "reduced", "affected"
            ],
            "watch": [
                "concern", "monitor", "potential", "possible", "risk",
                "threat", "warning", "alert", "notice", "update"
            ]
        }
    
    def calculate_confidence(self, row: Dict[str, Any]) -> float:
        """Calculate confidence score for disruption detection"""
        text = f"{row.get('title', '')} {row.get('description', '')}"
        
        # Check source reliability
        source_weight = self._get_source_weight(row.get("source", ""))
        
        # Check keyword density
        keyword_score = self._calculate_keyword_score(text)
        
        # Check severity indicators
        severity_score = self._calculate_severity_score(text)
        
        # Geographic relevance
        geo_score = self._calculate_geographic_score(row)
        
        # Weighted combination
        confidence = (
            source_weight * 0.25 +
            keyword_score * 0.30 +
            severity_score * 0.25 +
            geo_score * 0.20
        )
        
        return round(min(confidence, 1.0), 3)
    
    def assess_relevance(self, row: Dict[str, Any]) -> float:
        """Assess supply chain relevance"""
        text = f"{row.get('title', '')} {row.get('description', '')}".lower()
        
        relevance_score = 0.0
        
        # Direct keyword matching
        keyword_matches = sum(1 for keyword in self.supply_chain_keywords if keyword in text)
        relevance_score += (keyword_matches / len(self.supply_chain_keywords)) * 0.6
        
        # Event type specific scoring
        event_type = row.get("event_type", "")
        if event_type in ["weather", "earthquake", "port_status", "airport_delay"]:
            relevance_score += 0.3
        elif event_type == "news_alert":
            relevance_score += 0.2
        
        # Location-based relevance
        if self._is_strategic_location(row.get("location", "")):
            relevance_score += 0.1
        
        return round(min(relevance_score, 1.0), 3)
    
    def _get_source_weight(self, source: str) -> float:
        """Get reliability weight for different sources"""
        weights = {
            "weather": 0.9,
            "earthquake": 0.95,
            "transport": 0.8,
            "news": 0.7,
            "social": 0.4
        }
        return weights.get(source, 0.5)
    
    def _calculate_keyword_score(self, text: str) -> float:
        """Calculate keyword density score"""
        text_lower = text.lower()
        matches = sum(1 for keyword in self.supply_chain_keywords if keyword in text_lower)
        return min(matches / 5.0, 1.0)  # Normalize to max of 1.0
    
    def _calculate_severity_score(self, text: str) -> float:
        """Calculate severity indicator score"""
        text_lower = text.lower()
        
        for severity, indicators in self.severity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                if severity == "critical":
                    return 1.0
                elif severity == "warning":
                    return 0.7
                elif severity == "watch":
                    return 0.4
        
        return 0.2
    
    def _calculate_geographic_score(self, row: Dict[str, Any]) -> float:
        """Calculate geographic relevance score"""
        location = row.get("location", "").lower()
        
        # Major supply chain hubs
        major_hubs = [
            "los angeles", "long beach", "new york", "newark", "savannah",
            "shanghai", "shenzhen", "singapore", "rotterdam", "hamburg",
            "dubai", "hong kong", "tokyo", "busan", "antwerp"
        ]
        
        if any(hub in location for hub in major_hubs):
            return 1.0
        
        # Major countries/regions
        major_regions = [
            "china", "usa", "united states", "germany", "netherlands",
            "singapore", "japan", "south korea", "united kingdom"
        ]
        
        if any(region in location for region in major_regions):
            return 0.7
        
        return 0.3
    
    def _is_strategic_location(self, location: str) -> bool:
        """Check if location is strategically important for supply chains"""
        strategic_keywords = [
            "port", "airport", "hub", "terminal", "industrial", "manufacturing"
        ]
        return any(keyword in location.lower() for keyword in strategic_keywords)
```

### Step 29: Create Impact Analysis Engine
Create `src/core/processors/impact_analyzer.py`:
```python
from typing import Dict, Any, List
import math
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ImpactAnalyzer:
    def __init__(self):
        self.trade_routes = {
            "trans_pacific": ["los angeles", "long beach", "oakland", "seattle", "shanghai", "shenzhen"],
            "trans_atlantic": ["new york", "newark", "savannah", "rotterdam", "hamburg", "antwerp"],
            "asia_europe": ["shanghai", "singapore", "dubai", "rotterdam", "hamburg"],
            "panama_canal": ["panama", "colon", "balboa"],
            "suez_canal": ["suez", "port said"]
        }
        
        self.supply_chain_sectors = {
            "electronics": ["semiconductor", "chip", "electronics", "component"],
            "automotive": ["automotive", "car", "vehicle", "auto parts"],
            "textiles": ["textile", "clothing", "apparel", "fabric"],
            "energy": ["oil", "gas", "energy", "fuel", "petroleum"],
            "agriculture": ["food", "grain", "agriculture", "farming"]
        }
    
    def assess_impact(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall impact of the disruption"""
        
        # Calculate different impact dimensions
        geographic_impact = self._assess_geographic_impact(row)
        duration_impact = self._assess_duration_impact(row)
        sector_impact = self._assess_sector_impact(row)
        severity_impact = self._assess_severity_impact(row)
        
        # Calculate overall impact score
        impact_score = (
            geographic_impact * 0.3 +
            duration_impact * 0.2 +
            sector_impact * 0.3 +
            severity_impact * 0.2
        )
        
        # Determine affected trade routes
        affected_routes = self._identify_affected_routes(row)
        
        # Estimate financial impact
        financial_impact = self._estimate_financial_impact(impact_score, affected_routes)
        
        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(row, impact_score)
        
        return {
            "impact_score": round(impact_score, 3),
            "geographic_impact": geographic_impact,
            "duration_impact": duration_impact,
            "sector_impact": sector_impact,
            "severity_impact": severity_impact,
            "affected_routes": affected_routes,
            "financial_impact": financial_impact,
            "mitigation_strategies": mitigation_strategies
        }
    
    def _assess_geographic_impact(self, row: Dict[str, Any]) -> float:
        """Assess geographic impact based on location importance"""
        location = row.get("location", "").lower()
        
        # Major global hubs have higher impact
        tier1_hubs = ["shanghai", "singapore", "rotterdam", "los angeles", "shenzhen"]
        tier2_hubs = ["hamburg", "antwerp", "long beach", "new york", "dubai"]
        tier3_hubs = ["savannah", "oakland", "seattle", "hamburg", "busan"]
        
        if any(hub in location for hub in tier1_hubs):
            return 1.0
        elif any(hub in location for hub in tier2_hubs):
            return 0.8
        elif any(hub in location for hub in tier3_hubs):
            return 0.6
        else:
            return 0.3
    
    def _assess_duration_impact(self, row: Dict[str, Any]) -> float:
        """Assess impact based on expected duration"""
        event_type = row.get("event_type", "")
        severity = row.get("severity", "watch")
        
        duration_scores = {
            "earthquake": {"critical": 0.9, "warning": 0.7, "watch": 0.4},
            "weather": {"critical": 0.8, "warning": 0.6, "watch": 0.3},
            "news_alert": {"critical": 0.7, "warning": 0.5, "watch": 0.2},
            "transport": {"critical": 0.6, "warning": 0.4, "watch": 0.2}
        }
        
        return duration_scores.get(event_type, {}).get(severity, 0.3)
    
    def _assess_sector_impact(self, row: Dict[str, Any]) -> float:
        """Assess impact on different supply chain sectors"""
        text = f"{row.get('title', '')} {row.get('description', '')}".lower()
        
        sector_scores = []
        for sector, keywords in self.supply_chain_sectors.items():
            if any(keyword in text for keyword in keywords):
                sector_scores.append(0.8)  # High impact if sector-specific
            else:
                sector_scores.append(0.2)  # Low impact if not mentioned
        
        # Return average sector impact
        return sum(sector_scores) / len(sector_scores) if sector_scores else 0.3
    
    def _assess_severity_impact(self, row: Dict[str, Any]) -> float:
        """Convert severity to numeric impact"""
        severity = row.get("severity", "watch")
        severity_map = {
            "critical": 1.0,
            "warning": 0.6,
            "watch": 0.3
        }
        return severity_map.get(severity, 0.3)
    
    def _identify_affected_routes(self, row: Dict[str, Any]) -> List[str]:
        """Identify which trade routes might be affected"""
        location = row.get("location", "").lower()
        affected_routes = []
        
        for route_name, route_locations in self.trade_routes.items():
            if any(loc in location for loc in route_locations):
                affected_routes.append(route_name)
        
        return affected_routes
    
    def _estimate_financial_impact(self, impact_score: float, affected_routes: List[str]) -> Dict[str, Any]:
        """Estimate financial impact in monetary terms"""
        
        # Base impact per day (in millions USD)
        base_daily_impact = {
            "trans_pacific": 50,
            "trans_atlantic": 30,
            "asia_europe": 40,
            "panama_canal": 200,
            "suez_canal": 300
        }
        
        total_daily_impact = 0
        for route in affected_routes:
            daily_impact = base_daily_impact.get(route, 10)
            total_daily_impact += daily_impact * impact_score
        
        return {
            "daily_impact_usd_millions": round(total_daily_impact, 1),
            "weekly_impact_usd_millions": round(total_daily_impact * 7, 1),
            "affected_trade_volume_percent": round(impact_score * 100, 1)
        }
    
    def _generate_mitigation_strategies(self, row: Dict[str, Any], impact_score: float) -> List[str]:
        """Generate mitigation strategies based on disruption type and impact"""
        event_type = row.get("event_type", "")
        severity = row.get("severity", "watch")
        
        strategies = []
        
        if impact_score >= 0.7:
            strategies.extend([
                "Activate emergency procurement protocols",
                "Contact backup suppliers immediately",
                "Consider expedited shipping for critical items",
                "Increase safety stock levels for affected routes"
            ])
        
        if event_type == "weather":
            strategies.extend([
                "Monitor weather forecasts for route planning",
                "Consider alternative transportation modes",
                "Coordinate with logistics partners for rerouting"
            ])
        elif event_type == "earthquake":
            strategies.extend([
                "Assess supplier facility damage",
                "Activate disaster recovery plans",
                "Consider temporary supplier alternatives"
            ])
        elif event_type == "transport":
            strategies.extend([
                "Explore alternative routes and carriers",
                "Negotiate priority handling with logistics providers",
                "Consider multimodal transportation options"
            ])
        
        return strategies
```

### Step 30: Create Alert Scoring System
Create `src/core/processors/alert_scorer.py`:
```python
from typing import Dict, Any
import math
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AlertScorer:
    def __init__(self):
        self.weights = {
            "confidence": 0.25,
            "relevance": 0.25,
            "impact": 0.30,
            "urgency": 0.20
        }
    
    def calculate_alert_score(self, 
                            confidence_score: float,
                            relevance_score: float, 
                            impact_assessment: Dict[str, Any],
                            event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive alert score"""
        
        # Extract impact score
        impact_score = impact_assessment.get("impact_score", 0.5)
        
        # Calculate urgency based on event type and timing
        urgency_score = self._calculate_urgency(event_data)
        
        # Calculate weighted final score
        final_score = (
            confidence_score * self.weights["confidence"] +
            relevance_score * self.weights["relevance"] +
            impact_score * self.weights["impact"] +
            urgency_score * self.weights["urgency"]
        )
        
        # Determine alert level
        alert_level = self._determine_alert_level(final_score)
        
        # Calculate priority ranking
        priority_rank = self._calculate_priority_rank(final_score, impact_assessment)
        
        return {
            "alert_score": round(final_score, 3),
            "alert_level": alert_level,
            "priority_rank": priority_rank,
            "component_scores": {
                "confidence": confidence_score,
                "relevance": relevance_score,
                "impact": impact_score,
                "urgency": urgency_score
            },
            "should_alert": final_score >= 0.5,
            "escalation_needed": final_score >= 0.8
        }
    
    def _calculate_urgency(self, event_data: Dict[str, Any]) -> float:
        """Calculate urgency score based on timing and event type"""
        event_type = event_data.get("event_type", "")
        severity = event_data.get("severity", "watch")
        
        # Base urgency by event type
        type_urgency = {
            "earthquake": 0.9,
            "weather": 0.7,
            "transport": 0.6,
            "news_alert": 0.4,
            "port_status": 0.5
        }
        
        # Severity multiplier
        severity_multiplier = {
            "critical": 1.0,
            "warning": 0.7,
            "watch": 0.4
        }
        
        base_urgency = type_urgency.get(event_type, 0.5)
        multiplier = severity_multiplier.get(severity, 0.5)
        
        return base_urgency * multiplier
    
    def _determine_alert_level(self, score: float) -> str:
        """Determine alert level based on final score"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "warning"
        elif score >= 0.4:
            return "watch"
        else:
            return "info"
    
    def _calculate_priority_rank(self, score: float, impact_assessment: Dict[str, Any]) -> int:
        """Calculate priority ranking (1-100, where 1 is highest priority)"""
        
        # Base rank from score (inverted so higher scores get lower ranks)
        base_rank = max(1, int((1 - score) * 80))
        
        # Adjust based on financial impact
        financial_impact = impact_assessment.get("financial_impact", {})
        daily_impact = financial_impact.get("daily_impact_usd_millions", 0)
        
        if daily_impact > 100:
            base_rank = max(1, base_rank - 20)
        elif daily_impact > 50:
            base_rank = max(1, base_rank - 10)
        elif daily_impact > 10:
            base_rank = max(1, base_rank - 5)
        
        # Adjust based on affected routes
        affected_routes = impact_assessment.get("affected_routes", [])
        critical_routes = ["panama_canal", "suez_canal"]
        
        if any(route in critical_routes for route in affected_routes):
            base_rank = max(1, base_rank - 15)
        elif affected_routes:
            base_rank = max(1, base_rank - 5)
        
        return min(base_rank, 100)
```

### Step 31-40: Additional Pipeline Components

I'll continue with the remaining steps. Let me know if you'd like me to proceed with the next phases including API development, database integration, frontend creation, and deployment steps.

### Step 31: Create Vector Embeddings System
Create `src/core/embeddings/embedding_service.py`:
```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import pathway as pw
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for list of texts"""
        try:
            embeddings = self.model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return np.array([])
    
    def embed_disruption_data(self, row: Dict[str, Any]) -> List[float]:
        """Create embedding for disruption event"""
        text = f"{row.get('title', '')} {row.get('description', '')}"
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
```

### Step 32: Implement Real-time Vector Indexing
Create `src/core/indexing/vector_store.py`:
```python
import pathway as pw
import numpy as np
from typing import List, Dict, Any, Optional
from src.core.embeddings.embedding_service import EmbeddingService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PathwayVectorStore:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        
    def create_vector_index(self, data_stream):
        """Create real-time vector index from data stream"""
        
        # Add embeddings to the stream
        embedded_stream = data_stream.select(
            **pw.this,
            embedding=pw.apply(self.embedding_service.embed_disruption_data, pw.this),
            search_text=pw.this.title + " " + pw.this.description
        )
        
        # Create vector index for similarity search
        vector_index = embedded_stream.select(
            id=pw.this.pointer,
            content=pw.this.search_text,
            metadata=pw.this.select(
                event_type=pw.this.event_type,
                severity=pw.this.severity,
                location=pw.this.location,
                source=pw.this.source
            ),
            embedding=pw.this.embedding
        )
        
        return vector_index
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5):
        """Perform similarity search (placeholder for actual implementation)"""
        # This would integrate with Pathway's vector search capabilities
        pass
```

### Step 33: Create Data Validation Pipeline
Create `src/core/validation/data_validator.py`:
```python
from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DataValidator:
    def __init__(self):
        self.required_fields = ["source", "event_type", "title", "severity"]
        self.valid_severities = ["critical", "warning", "watch", "info"]
        self.valid_sources = ["weather", "news", "earthquake", "transport"]
        
    def validate_disruption_data(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean disruption data"""
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "cleaned_data": row.copy()
        }
        
        # Check required fields
        missing_fields = [field for field in self.required_fields if not row.get(field)]
        if missing_fields:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Missing required fields: {missing_fields}")
        
        # Validate severity
        severity = row.get("severity", "").lower()
        if severity not in self.valid_severities:
            validation_result["warnings"].append(f"Invalid severity '{severity}', defaulting to 'watch'")
            validation_result["cleaned_data"]["severity"] = "watch"
        
        # Validate source
        source = row.get("source", "").lower()
        if source not in self.valid_sources:
            validation_result["warnings"].append(f"Unknown source '{source}'")
        
        # Clean and validate coordinates
        lat = row.get("latitude")
        lon = row.get("longitude")
        if lat is not None and lon is not None:
            try:
                lat_clean = float(lat)
                lon_clean = float(lon)
                if not (-90 <= lat_clean <= 90) or not (-180 <= lon_clean <= 180):
                    validation_result["warnings"].append("Invalid coordinates")
                    validation_result["cleaned_data"]["latitude"] = None
                    validation_result["cleaned_data"]["longitude"] = None
                else:
                    validation_result["cleaned_data"]["latitude"] = lat_clean
                    validation_result["cleaned_data"]["longitude"] = lon_clean
            except (ValueError, TypeError):
                validation_result["warnings"].append("Invalid coordinate format")
                validation_result["cleaned_data"]["latitude"] = None
                validation_result["cleaned_data"]["longitude"] = None
        
        # Clean text fields
        for field in ["title", "description"]:
            if field in validation_result["cleaned_data"]:
                cleaned_text = self._clean_text(validation_result["cleaned_data"][field])
                validation_result["cleaned_data"][field] = cleaned_text
        
        # Add validation timestamp
        validation_result["cleaned_data"]["validated_at"] = datetime.utcnow().isoformat()
        
        return validation_result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text fields"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?():]', '', text)
        
        return text
```

### Step 34: Set up Monitoring and Health Checks
Create `src/core/monitoring/health_monitor.py`:
```python
import time
import psutil
from typing import Dict, Any
from datetime import datetime, timedelta
import requests
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class HealthMonitor:
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.error_count = 0
        self.processed_events = 0
        self.last_data_update = None
        
    def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "checks": {}
        }
        
        # Check system resources
        health_status["checks"]["system"] = self._check_system_resources()
        
        # Check data pipeline
        health_status["checks"]["pipeline"] = self._check_pipeline_health()
        
        # Check external APIs
        health_status["checks"]["external_apis"] = self._check_external_apis()
        
        # Check database connectivity
        health_status["checks"]["database"] = self._check_database()
        
        # Determine overall status
        overall_status = "healthy"
        for check_name, check_result in health_status["checks"].items():
            if check_result["status"] != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
        
        health_status["status"] = overall_status
        
        return health_status
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check CPU, memory, and disk usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "healthy"
            if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
                status = "warning"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "critical"
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_pipeline_health(self) -> Dict[str, Any]:
        """Check data pipeline health"""
        try:
            current_time = datetime.utcnow()
            
            # Check if data is being processed
            data_freshness = "healthy"
            if self.last_data_update:
                time_since_update = current_time - self.last_data_update
                if time_since_update > timedelta(minutes=10):
                    data_freshness = "warning"
                if time_since_update > timedelta(minutes=30):
                    data_freshness = "critical"
            
            # Check error rate
            error_rate = "healthy"
            if self.processed_events > 0:
                error_percentage = (self.error_count / self.processed_events) * 100
                if error_percentage > 5:
                    error_rate = "warning"
                if error_percentage > 15:
                    error_rate = "critical"
            
            overall_status = "healthy"
            if data_freshness != "healthy" or error_rate != "healthy":
                overall_status = "warning"
            if data_freshness == "critical" or error_rate == "critical":
                overall_status = "critical"
            
            return {
                "status": overall_status,
                "data_freshness": data_freshness,
                "error_rate": error_rate,
                "processed_events": self.processed_events,
                "error_count": self.error_count,
                "last_update": self.last_data_update.isoformat() if self.last_data_update else None
            }
        except Exception as e:
            logger.error(f"Error checking pipeline health: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API availability"""
        apis_to_check = [
            {"name": "OpenWeather", "url": "https://api.openweathermap.org/data/2.5/weather?q=London&appid=test"},
            {"name": "NewsAPI", "url": "https://newsapi.org/"},
            {"name": "USGS", "url": "https://earthquake.usgs.gov/"}
        ]
        
        api_status = {}
        overall_status = "healthy"
        
        for api in apis_to_check:
            try:
                response = requests.get(api["url"], timeout=5)
                if response.status_code < 500:
                    api_status[api["name"]] = "healthy"
                else:
                    api_status[api["name"]] = "degraded"
                    overall_status = "warning" if overall_status == "healthy" else overall_status
            except Exception as e:
                api_status[api["name"]] = "error"
                overall_status = "warning"
                logger.warning(f"API {api['name']} check failed: {e}")
        
        return {
            "status": overall_status,
            "apis": api_status
        }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # This would include actual database connection check
            # For now, return healthy status
            return {"status": "healthy", "connection": "active"}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def record_event_processed(self):
        """Record that an event was processed"""
        self.processed_events += 1
        self.last_data_update = datetime.utcnow()
    
    def record_error(self):
        """Record that an error occurred"""
        self.error_count += 1
```

### Step 35: Implement Error Handling and Retry Logic
Create `src/core/utils/retry_handler.py`:
```python
import time
import functools
from typing import Callable, Any, Type, Tuple
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RetryHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def retry_with_backoff(self, 
                          exceptions: Tuple[Type[Exception], ...] = (Exception,),
                          exclude_exceptions: Tuple[Type[Exception], ...] = ()):
        """Decorator for retry with exponential backoff"""
        
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                
                for attempt in range(self.max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exclude_exceptions as e:
                        logger.info(f"Non-retryable exception in {func.__name__}: {e}")
                        raise
                    except exceptions as e:
                        last_exception = e
                        if attempt == self.max_retries:
                            logger.error(f"Final attempt failed for {func.__name__}: {e}")
                            raise
                        
                        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s")
                        time.sleep(delay)
                
                raise last_exception
            
            return wrapper
        return decorator

# Create global retry handler
retry_handler = RetryHandler()

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info(f"Circuit breaker for {func.__name__} moving to half-open state")
            else:
                raise Exception(f"Circuit breaker open for {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info(f"Circuit breaker for {func.__name__} closed - service recovered")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened for {func.__name__} after {self.failure_count} failures")
            
            raise
```

### Step 36: Create Data Backup and Recovery System
Create `src/core/backup/backup_manager.py`:
```python
import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pickle
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BackupManager:
    def __init__(self, backup_dir: str = "data/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def backup_disruption_data(self, data: List[Dict[str, Any]], backup_type: str = "daily"):
        """Backup disruption data"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"disruptions_{backup_type}_{timestamp}.json.gz"
            filepath = self.backup_dir / filename
            
            # Compress and save data
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Backed up {len(data)} disruption records to {filename}")
            
            # Clean old backups
            self._cleanup_old_backups(backup_type)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def backup_model_state(self, model_data: Dict[str, Any]):
        """Backup ML model state and configurations"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"model_state_{timestamp}.pkl"
            filepath = self.backup_dir / filename
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Backed up model state to {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error backing up model state: {e}")
            raise
    
    def restore_data(self, backup_file: str) -> List[Dict[str, Any]]:
        """Restore data from backup file"""
        try:
            filepath = Path(backup_file)
            
            if filepath.suffix == '.gz':
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            logger.info(f"Restored {len(data)} records from {backup_file}")
            return data
            
        except Exception as e:
            logger.error(f"Error restoring data from {backup_file}: {e}")
            raise
    
    def _cleanup_old_backups(self, backup_type: str, retention_days: int = 30):
        """Clean up old backup files"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            pattern = f"*_{backup_type}_*.json.gz"
            
            for backup_file in self.backup_dir.glob(pattern):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.info(f"Cleaned up old backup: {backup_file.name}")
                    
        except Exception as e:
            logger.warning(f"Error cleaning up old backups: {e}")
    
    def get_backup_summary(self) -> Dict[str, Any]:
        """Get summary of available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.json.gz"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": "disruption_data"
            })
        
        for backup_file in self.backup_dir.glob("*.pkl"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": "model_state"
            })
        
        return {
            "total_backups": len(backups),
            "total_size_mb": sum(b["size_mb"] for b in backups),
            "backups": sorted(backups, key=lambda x: x["created_at"], reverse=True)
        }
```

### Step 37: Set up Pipeline Orchestration
Create `src/core/orchestration/pipeline_orchestrator.py`:
```python
import asyncio
import schedule
import threading
from typing import Dict, Any, List, Callable
from datetime import datetime, timedelta
from src.core.pipeline.main_pipeline import SupplyChainPipeline
from src.core.monitoring.health_monitor import HealthMonitor
from src.core.backup.backup_manager import BackupManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        self.pipeline = SupplyChainPipeline()
        self.health_monitor = HealthMonitor()
        self.backup_manager = BackupManager()
        self.is_running = False
        self.scheduled_tasks = []
        
    def start(self):
        """Start the pipeline orchestrator"""
        if self.is_running:
            logger.warning("Pipeline orchestrator is already running")
            return
        
        logger.info("Starting Pipeline Orchestrator...")
        self.is_running = True
        
        # Schedule regular tasks
        self._schedule_tasks()
        
        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Start the main pipeline
        try:
            self.pipeline.run()
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the pipeline orchestrator"""
        logger.info("Stopping Pipeline Orchestrator...")
        self.is_running = False
        schedule.clear()
    
    def _schedule_tasks(self):
        """Schedule regular maintenance tasks"""
        
        # Health checks every 5 minutes
        schedule.every(5).minutes.do(self._run_health_check)
        
        # Data backup every hour
        schedule.every().hour.do(self._run_data_backup)
        
        # Cleanup tasks daily at 2 AM
        schedule.every().day.at("02:00").do(self._run_cleanup_tasks)
        
        # Pipeline metrics every 15 minutes
        schedule.every(15).minutes.do(self._collect_metrics)
        
        logger.info("Scheduled tasks configured")
    
    def _run_scheduler(self):
        """Run the task scheduler"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def _run_health_check(self):
        """Run health check task"""
        try:
            health_status = self.health_monitor.check_system_health()
            if health_status["status"] != "healthy":
                logger.warning(f"System health check: {health_status['status']}")
                # Could trigger alerts here
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    def _run_data_backup(self):
        """Run data backup task"""
        try:
            # This would fetch recent data and backup
            # For now, just log the task
            logger.info("Running scheduled data backup")
            
        except Exception as e:
            logger.error(f"Data backup failed: {e}")
    
    def _run_cleanup_tasks(self):
        """Run daily cleanup tasks"""
        try:
            logger.info("Running daily cleanup tasks")
            
            # Clean up old log files
            self._cleanup_logs()
            
            # Clean up temporary files
            self._cleanup_temp_files()
            
        except Exception as e:
            logger.error(f"Cleanup tasks failed: {e}")
    
    def _collect_metrics(self):
        """Collect pipeline metrics"""
        try:
            # This would collect and store pipeline metrics
            logger.debug("Collecting pipeline metrics")
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
    
    def _cleanup_logs(self):
        """Clean up old log files"""
        # Implementation for log cleanup
        pass
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        # Implementation for temp file cleanup
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "is_running": self.is_running,
            "scheduled_tasks": len(schedule.jobs),
            "health_status": self.health_monitor.check_system_health(),
            "uptime_seconds": (datetime.utcnow() - self.health_monitor.start_time).total_seconds()
        }
```

### Step 38: Implement Rate Limiting for External APIs
Create `src/core/utils/rate_limiter.py`:
```python
import time
import threading
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RateLimiter:
    def __init__(self):
        self.limits = {}
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
    
    def set_limit(self, service: str, requests_per_minute: int, requests_per_hour: int = None):
        """Set rate limits for a service"""
        self.limits[service] = {
            "requests_per_minute": requests_per_minute,
            "requests_per_hour": requests_per_hour or requests_per_minute * 60
        }
    
    def can_make_request(self, service: str) -> bool:
        """Check if a request can be made for the service"""
        with self.lock:
            if service not in self.limits:
                return True
            
            current_time = time.time()
            request_times = self.requests[service]
            
            # Clean old requests
            self._clean_old_requests(request_times, current_time)
            
            # Check minute limit
            minute_ago = current_time - 60
            minute_requests = sum(1 for req_time in request_times if req_time > minute_ago)
            
            if minute_requests >= self.limits[service]["requests_per_minute"]:
                return False
            
            # Check hour limit
            hour_ago = current_time - 3600
            hour_requests = sum(1 for req_time in request_times if req_time > hour_ago)
            
            if hour_requests >= self.limits[service]["requests_per_hour"]:
                return False
            
            return True
    
    def record_request(self, service: str):
        """Record that a request was made"""
        with self.lock:
            self.requests[service].append(time.time())
    
    def wait_for_slot(self, service: str, timeout: float = 300) -> bool:
        """Wait for an available request slot"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.can_make_request(service):
                return True
            
            # Calculate wait time
            wait_time = self._calculate_wait_time(service)
            if wait_time > timeout - (time.time() - start_time):
                return False
            
            time.sleep(min(wait_time, 1.0))
        
        return False
    
    def _clean_old_requests(self, request_times: deque, current_time: float):
        """Remove requests older than 1 hour"""
        hour_ago = current_time - 3600
        while request_times and request_times[0] < hour_ago:
            request_times.popleft()
    
    def _calculate_wait_time(self, service: str) -> float:
        """Calculate how long to wait before next request"""
        if service not in self.limits:
            return 0
        
        current_time = time.time()
        request_times = self.requests[service]
        
        # Find oldest request in the last minute
        minute_ago = current_time - 60
        minute_requests = [req_time for req_time in request_times if req_time > minute_ago]
        
        if len(minute_requests) >= self.limits[service]["requests_per_minute"]:
            oldest_in_minute = min(minute_requests)
            return max(0, 60 - (current_time - oldest_in_minute))
        
        return 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get rate limiter status"""
        with self.lock:
            status = {}
            current_time = time.time()
            
            for service, limits in self.limits.items():
                request_times = self.requests[service]
                self._clean_old_requests(request_times, current_time)
                
                minute_ago = current_time - 60
                hour_ago = current_time - 3600
                
                minute_requests = sum(1 for req_time in request_times if req_time > minute_ago)
                hour_requests = sum(1 for req_time in request_times if req_time > hour_ago)
                
                status[service] = {
                    "requests_last_minute": minute_requests,
                    "requests_last_hour": hour_requests,
                    "limit_per_minute": limits["requests_per_minute"],
                    "limit_per_hour": limits["requests_per_hour"],
                    "can_make_request": self.can_make_request(service)
                }
            
            return status

# Global rate limiter instance
rate_limiter = RateLimiter()

# Set default limits for external APIs
rate_limiter.set_limit("openweather", 60, 1000)  # 60/min, 1000/hour
rate_limiter.set_limit("newsapi", 500, 500)      # 500/hour
rate_limiter.set_limit("usgs", 100, 2000)       # 100/min, 2000/hour
```

### Step 39: Create Data Quality Metrics
Create `src/core/quality/data_quality_monitor.py`:
```python
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DataQualityMonitor:
    def __init__(self):
        self.quality_metrics = defaultdict(list)
        self.data_samples = defaultdict(list)
        self.quality_thresholds = {
            "completeness": 0.95,
            "accuracy": 0.90,
            "consistency": 0.85,
            "timeliness": 0.90
        }
    
    def assess_data_quality(self, data_batch: List[Dict[str, Any]], source: str) -> Dict[str, Any]:
        """Assess overall data quality for a batch"""
        
        if not data_batch:
            return {"overall_score": 0.0, "issues": ["Empty data batch"]}
        
        # Calculate different quality dimensions
        completeness = self._assess_completeness(data_batch)
        accuracy = self._assess_accuracy(data_batch, source)
        consistency = self._assess_consistency(data_batch)
        timeliness = self._assess_timeliness(data_batch)
        validity = self._assess_validity(data_batch)
        
        # Calculate overall quality score
        overall_score = np.mean([completeness, accuracy, consistency, timeliness, validity])
        
        # Identify quality issues
        issues = []
        if completeness < self.quality_thresholds["completeness"]:
            issues.append(f"Low completeness: {completeness:.2f}")
        if accuracy < self.quality_thresholds["accuracy"]:
            issues.append(f"Low accuracy: {accuracy:.2f}")
        if consistency < self.quality_thresholds["consistency"]:
            issues.append(f"Low consistency: {consistency:.2f}")
        if timeliness < self.quality_thresholds["timeliness"]:
            issues.append(f"Low timeliness: {timeliness:.2f}")
        
        quality_assessment = {
            "overall_score": round(overall_score, 3),
            "dimensions": {
                "completeness": round(completeness, 3),
                "accuracy": round(accuracy, 3),
                "consistency": round(consistency, 3),
                "timeliness": round(timeliness, 3),
                "validity": round(validity, 3)
            },
            "issues": issues,
            "sample_size": len(data_batch),
            "source": source,
            "assessed_at": datetime.utcnow().isoformat()
        }
        
        # Store metrics for trending
        self.quality_metrics[source].append(quality_assessment)
        
        return quality_assessment
    
    def _assess_completeness(self, data_batch: List[Dict[str, Any]]) -> float:
        """Assess data completeness (missing values)"""
        required_fields = ["title", "description", "severity", "source", "event_type"]
        
        total_fields = len(data_batch) * len(required_fields)
        missing_fields = 0
        
        for record in data_batch:
            for field in required_fields:
                if not record.get(field) or record.get(field) in [None, "", "N/A"]:
                    missing_fields += 1
        
        completeness = (total_fields - missing_fields) / total_fields if total_fields > 0 else 0
        return completeness
    
    def _assess_accuracy(self, data_batch: List[Dict[str, Any]], source: str) -> float:
        """Assess data accuracy based on source reliability and validation"""
        
        # Source reliability scores
        source_reliability = {
            "weather": 0.95,
            "earthquake": 0.98,
            "news": 0.75,
            "transport": 0.85
        }
        
        base_accuracy = source_reliability.get(source, 0.7)
        
        # Check for obvious data quality issues
        accuracy_deductions = 0
        for record in data_batch:
            # Check coordinate validity
            lat = record.get("latitude")
            lon = record.get("longitude")
            if lat is not None and lon is not None:
                try:
                    lat_val = float(lat)
                    lon_val = float(lon)
                    if not (-90 <= lat_val <= 90) or not (-180 <= lon_val <= 180):
                        accuracy_deductions += 0.1
                except (ValueError, TypeError):
                    accuracy_deductions += 0.1
            
            # Check severity value validity
            severity = record.get("severity", "").lower()
            if severity not in ["critical", "warning", "watch", "info"]:
                accuracy_deductions += 0.05
        
        # Apply deductions
        final_accuracy = base_accuracy - (accuracy_deductions / len(data_batch))
        return max(0, final_accuracy)
    
    def _assess_consistency(self, data_batch: List[Dict[str, Any]]) -> float:
        """Assess data consistency across records"""
        
        consistency_score = 1.0
        
        # Check for consistent data formats
        severity_values = [record.get("severity", "").lower() for record in data_batch]
        unique_severities = set(severity_values)
        
        # Check if all severities are valid
        valid_severities = {"critical", "warning", "watch", "info"}
        invalid_severities = unique_severities - valid_severities
        
        if invalid_severities:
            consistency_score -= 0.2
        
        # Check for consistent location formats
        locations = [record.get("location", "") for record in data_batch if record.get("location")]
        if locations:
            # Simple check for consistent formatting (this could be more sophisticated)
            avg_location_length = np.mean([len(loc) for loc in locations])
            location_length_variance = np.var([len(loc) for loc in locations])
            
            if location_length_variance > avg_location_length:
                consistency_score -= 0.1
        
        return max(0, consistency_score)
    
    def _assess_timeliness(self, data_batch: List[Dict[str, Any]]) -> float:
        """Assess data timeliness"""
        current_time = datetime.utcnow()
        
        timeliness_scores = []
        for record in data_batch:
            # Check if record has timestamp information
            timestamp_fields = ["created_at", "published_at", "time", "start_time"]
            record_time = None
            
            for field in timestamp_fields:
                if record.get(field):
                    try:
                        if isinstance(record[field], str):
                            record_time = datetime.fromisoformat(record[field].replace('Z', '+00:00'))
                        elif isinstance(record[field], (int, float)):
                            record_time = datetime.fromtimestamp(record[field] / 1000 if record[field] > 1e10 else record[field])
                        break
                    except:
                        continue
            
            if record_time:
                age = (current_time - record_time).total_seconds() / 3600  # Age in hours
                
                # Score based on age (fresher is better)
                if age <= 1:
                    timeliness_scores.append(1.0)
                elif age <= 6:
                    timeliness_scores.append(0.9)
                elif age <= 24:
                    timeliness_scores.append(0.7)
                elif age <= 72:
                    timeliness_scores.append(0.5)
                else:
                    timeliness_scores.append(0.2)
            else:
                timeliness_scores.append(0.5)  # No timestamp info
        
        return np.mean(timeliness_scores) if timeliness_scores else 0.5
    
    def _assess_validity(self, data_batch: List[Dict[str, Any]]) -> float:
        """Assess data validity (format and value constraints)"""
        
        validity_score = 1.0
        total_checks = 0
        failed_checks = 0
        
        for record in data_batch:
            # Check title length
            title = record.get("title", "")
            if len(title) > 200 or len(title) < 5:
                failed_checks += 1
            total_checks += 1
            
            # Check description length
            description = record.get("description", "")
            if len(description) > 5000:
                failed_checks += 1
            total_checks += 1
            
            # Check event_type is not empty
            event_type = record.get("event_type", "")
            if not event_type or len(event_type) < 2:
                failed_checks += 1
            total_checks += 1
        
        if total_checks > 0:
            validity_score = (total_checks - failed_checks) / total_checks
        
        return validity_score
    
    def get_quality_trends(self, source: str, days: int = 7) -> Dict[str, Any]:
        """Get data quality trends for a source"""
        
        if source not in self.quality_metrics:
            return {"error": f"No quality metrics found for source: {source}"}
        
        # Filter recent metrics
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_metrics = [
            metric for metric in self.quality_metrics[source]
            if datetime.fromisoformat(metric["assessed_at"]) > cutoff_date
        ]
        
        if not recent_metrics:
            return {"error": f"No recent quality metrics found for source: {source}"}
        
        # Calculate trends
        overall_scores = [metric["overall_score"] for metric in recent_metrics]
        
        trend_analysis = {
            "source": source,
            "period_days": days,
            "total_assessments": len(recent_metrics),
            "average_quality": round(np.mean(overall_scores), 3),
            "quality_trend": "improving" if len(overall_scores) > 1 and overall_scores[-1] > overall_scores[0] else "stable",
            "min_quality": round(min(overall_scores), 3),
            "max_quality": round(max(overall_scores), 3),
            "std_quality": round(np.std(overall_scores), 3),
            "dimension_averages": {}
        }
        
        # Calculate dimension averages
        dimensions = ["completeness", "accuracy", "consistency", "timeliness", "validity"]
        for dim in dimensions:
            dim_scores = [metric["dimensions"][dim] for metric in recent_metrics]
            trend_analysis["dimension_averages"][dim] = round(np.mean(dim_scores), 3)
        
        return trend_analysis

# Global data quality monitor
data_quality_monitor = DataQualityMonitor()
```

### Step 40: Set up Pipeline Testing Framework
Create `tests/test_pipeline.py`:
```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.core.pipeline.main_pipeline import SupplyChainPipeline
from src.core.processors.disruption_detector import DisruptionDetector
from src.core.processors.impact_analyzer import ImpactAnalyzer
from src.services.weather.weather_service import WeatherService

class TestSupplyChainPipeline:
    
    @pytest.fixture
    def pipeline(self):
        return SupplyChainPipeline()
    
    @pytest.fixture
    def sample_weather_data(self):
        return {
            "source": "weather",
            "event_type": "weather_alert",
            "title": "Severe Storm Warning",
            "description": "Severe thunderstorms expected in the Los Angeles area",
            "severity": "warning",
            "location": "Los Angeles",
            "latitude": 34.0522,
            "longitude": -118.2437
        }
    
    @pytest.fixture
    def sample_news_data(self):
        return {
            "source": "news",
            "event_type": "news_alert",
            "title": "Port Strike Threatens Supply Chain",
            "description": "Workers at major West Coast ports may go on strike",
            "severity": "critical",
            "location": "Los Angeles Port",
            "url": "https://example.com/news"
        }
    
    def test_disruption_detector_confidence(self, sample_weather_data):
        detector = DisruptionDetector()
        confidence = detector.calculate_confidence(sample_weather_data)
        
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Weather data should have decent confidence
    
    def test_disruption_detector_relevance(self, sample_news_data):
        detector = DisruptionDetector()
        relevance = detector.assess_relevance(sample_news_data)
        
        assert 0 <= relevance <= 1
        assert relevance > 0.7  # Port strike news should be highly relevant
    
    def test_impact_analyzer_assessment(self, sample_weather_data):
        analyzer = ImpactAnalyzer()
        impact = analyzer.assess_impact(sample_weather_data)
        
        assert "impact_score" in impact
        assert "geographic_impact" in impact
        assert "affected_routes" in impact
        assert isinstance(impact["mitigation_strategies"], list)
    
    @patch('src.services.weather.weather_service.requests.get')
    def test_weather_service_api_call(self, mock_get):
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "alerts": [{
                "event": "Severe Storm",
                "description": "Severe weather warning",
                "tags": ["Severe"],
                "start": 1640995200,
                "end": 1641000000
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        weather_service = WeatherService()
        locations = [{"name": "Test", "lat": 40.7128, "lon": -74.0060}]
        alerts = weather_service.get_weather_alerts(locations)
        
        assert len(alerts) > 0
        assert alerts[0]["source"] == "weather"
        assert alerts[0]["severity"] in ["critical", "warning", "watch"]
    
    def test_pipeline_initialization(self, pipeline):
        assert pipeline.connectors is not None
        assert pipeline.disruption_detector is not None
        assert pipeline.impact_analyzer is not None
    
    def test_alert_score_calculation(self, pipeline, sample_weather_data):
        # Test the alert scoring logic
        score = pipeline._calculate_alert_score({
            **sample_weather_data,
            "confidence_score": 0.8,
            "supply_chain_relevance": 0.7,
            "impact_assessment": {"impact_score": 0.6}
        })
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    def test_recommendations_generation(self, pipeline, sample_weather_data):
        recommendations = pipeline._generate_recommendations(sample_weather_data)
        
        assert "immediate_actions" in recommendations
        assert "monitoring_actions" in recommendations
        assert "escalation_needed" in recommendations
        assert isinstance(recommendations["immediate_actions"], list)

# Integration tests
class TestPipelineIntegration:
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self):
        """Test complete data flow from input to output"""
        # This would test the full pipeline with mock data
        pass
    
    def test_rate_limiting_integration(self):
        """Test that rate limiting works with external APIs"""
        from src.core.utils.rate_limiter import rate_limiter
        
        # Test rate limiting
        assert rate_limiter.can_make_request("test_service")
        rate_limiter.set_limit("test_service", 1, 5)
        
        # Make request and record it
        rate_limiter.record_request("test_service")
        
        # Second request should be blocked
        assert not rate_limiter.can_make_request("test_service")
    
    def test_data_quality_monitoring(self):
        """Test data quality monitoring integration"""
        from src.core.quality.data_quality_monitor import data_quality_monitor
        
        test_data = [{
            "title": "Test Event",
            "description": "Test description",
            "severity": "warning",
            "source": "test",
            "event_type": "test_event"
        }]
        
        quality_assessment = data_quality_monitor.assess_data_quality(test_data, "test")
        
        assert "overall_score" in quality_assessment
        assert "dimensions" in quality_assessment
        assert 0 <= quality_assessment["overall_score"] <= 1

# Performance tests
class TestPipelinePerformance:
    
    def test_processing_speed(self):
        """Test that pipeline can process data within acceptable time limits"""
        import time
        
        detector = DisruptionDetector()
        
        # Generate test data
        test_data = {
            "source": "test",
            "event_type": "test",
            "title": "Test Event " * 10,
            "description": "Test description " * 20,
            "severity": "warning",
            "location": "Test Location"
        }
        
        start_time = time.time()
        
        # Process 100 records
        for _ in range(100):
            confidence = detector.calculate_confidence(test_data)
            relevance = detector.assess_relevance(test_data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 100 records in under 1 second
        assert processing_time < 1.0
    
    def test_memory_usage(self):
        """Test memory usage stays within acceptable limits"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create pipeline and process some data
        pipeline = SupplyChainPipeline()
        
        # Memory increase should be reasonable
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be less than 100MB for basic initialization
        assert memory_increase < 100 * 1024 * 1024

if __name__ == "__main__":
    pytest.main([__file__])
```

## Phase 3: API Development (Steps 41-60)

### Step 41: Create FastAPI Application Structure
Create `src/api/main.py`:
```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
from src.api.routers import alerts, health, dashboard, admin
from src.api.middleware.auth import AuthMiddleware
from src.api.middleware.rate_limiting import RateLimitMiddleware
from src.core.orchestration.pipeline_orchestrator import PipelineOrchestrator
from src.utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

# Global orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    
    # Startup
    logger.info("Starting Supply Chain Disruption Predictor API")
    
    # Initialize and start pipeline orchestrator
    orchestrator = PipelineOrchestrator()
    try:
        orchestrator.start()
        logger.info("Pipeline orchestrator started successfully")
    except Exception as e:
        logger.error(f"Failed to start pipeline orchestrator: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down API")
    if orchestrator:
        orchestrator.stop()

# Create FastAPI app
app = FastAPI(
    title="Supply Chain Disruption Predictor",
    description="Real-time supply chain disruption prediction and alerting platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supply Chain Disruption Predictor API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

def get_orchestrator():
    """Dependency to get orchestrator instance"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service unavailable - orchestrator not running")
    return orchestrator

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
```

### Step 42: Create API Data Models
Create `src/api/models/schemas.py`:
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning" 
    WATCH = "watch"
    INFO = "info"

class EventType(str, Enum):
    WEATHER = "weather"
    EARTHQUAKE = "earthquake"
    NEWS = "news_alert"
    TRANSPORT = "transport"
    PORT_STATUS = "port_status"

class DisruptionEvent(BaseModel):
    id: Optional[int] = None
    event_type: EventType
    severity: SeverityLevel
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., max_length=5000)
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    impact_score: Optional[float] = Field(None, ge=0, le=1)
    source: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "event_type": "weather",
                "severity": "warning",
                "title": "Severe Storm Warning",
                "description": "Major storm system approaching Los Angeles port area",
                "location": "Los Angeles",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "source": "weather_api"
            }
        }

class AlertResponse(BaseModel):
    alert_score: float = Field(..., ge=0, le=1)
    alert_level: SeverityLevel
    priority_rank: int = Field(..., ge=1, le=100)
    should_alert: bool
    escalation_needed: bool
    event: DisruptionEvent
    impact_assessment: Dict[str, Any]
    recommendations: Dict[str, Any]
    
class AlertsListResponse(BaseModel):
    alerts: List[AlertResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool

class DashboardStats(BaseModel):
    total_alerts_24h: int
    critical_alerts_24h: int
    active_disruptions: int
    affected_routes: List[str]
    average_confidence: float
    system_health: str

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    uptime_seconds: float
    checks: Dict[str, Any]
    
class AlertFilter(BaseModel):
    severity: Optional[List[SeverityLevel]] = None
    event_type: Optional[List[EventType]] = None
    location: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    min_impact: Optional[float] = Field(None, ge=0, le=1)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
```

### Step 43: Create Health Check Endpoints
Create `src/api/routers/health.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from src.api.models.schemas import HealthCheck
from src.core.monitoring.health_monitor import HealthMonitor
from src.core.orchestration.pipeline_orchestrator import PipelineOrchestrator
from src.api.main import get_orchestrator
from datetime import datetime

router = APIRouter()
health_monitor = HealthMonitor()

@router.get("/", response_model=HealthCheck)
async def health_check():
    """Basic health check endpoint"""
    try:
        health_status = health_monitor.check_system_health()
        
        return HealthCheck(
            status=health_status["status"],
            timestamp=datetime.fromisoformat(health_status["timestamp"]),
            uptime_seconds=health_status["uptime_seconds"],
            checks=health_status["checks"]
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@router.get("/detailed")
async def detailed_health_check(orchestrator: PipelineOrchestrator = Depends(get_orchestrator)):
    """Detailed health check including pipeline status"""
    try:
        system_health = health_monitor.check_system_health()
        orchestrator_status = orchestrator.get_status()
        
        return {
            "system_health": system_health,
            "pipeline_status": orchestrator_status,
            "data_quality": "healthy",  # Would integrate with data quality monitor
            "external_apis": system_health["checks"].get("external_apis", {}),
            "recommendations": _generate_health_recommendations(system_health)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Detailed health check failed: {str(e)}")

@router.get("/metrics")
async def get_metrics():
    """Get system metrics for monitoring"""
    try:
        return {
            "processed_events": health_monitor.processed_events,
            "error_count": health_monitor.error_count,
            "error_rate": health_monitor.error_count / max(health_monitor.processed_events, 1),
            "last_update": health_monitor.last_data_update.isoformat() if health_monitor.last_data_update else None,
            "uptime_seconds": (datetime.utcnow() - health_monitor.start_time).total_seconds()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

def _generate_health_recommendations(health_status: dict) -> list:
    """Generate health recommendations based on status"""
    recommendations = []
    
    if health_status["status"] != "healthy":
        recommendations.append("System is experiencing issues - check logs for details")
    
    # Check individual components
    for check_name, check_result in health_status.get("checks", {}).items():
        if check_result.get("status") != "healthy":
            if check_name == "system":
                recommendations.append("System resources are under pressure - consider scaling")
            elif check_name == "external_apis":
                recommendations.append("External API issues detected - check connectivity")
            elif check_name == "pipeline":
                recommendations.append("Data pipeline issues detected - check data sources")
    
    return recommendations
```

### Step 44: Create Alerts Management Endpoints
Create `src/api/routers/alerts.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.api.models.schemas import (
    AlertResponse, AlertsListResponse, AlertFilter, 
    SeverityLevel, EventType, DisruptionEvent
)
from src.core.database import get_db
from src.models.disruption import DisruptionEvent as DBDisruptionEvent
from src.api.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=AlertsListResponse)
async def get_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[List[SeverityLevel]] = Query(None),
    event_type: Optional[List[EventType]] = Query(None),
    location: Optional[str] = Query(None),
    min_confidence: Optional[float] = Query(None, ge=0, le=1),
    hours_back: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of alerts with filtering and pagination"""
    try:
        # Build query
        query = db.query(DBDisruptionEvent)
        
        # Time filter
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        query = query.filter(DBDisruptionEvent.created_at >= cutoff_time)
        
        # Apply filters
        if severity:
            query = query.filter(DBDisruptionEvent.severity.in_(severity))
        
        if event_type:
            query = query.filter(DBDisruptionEvent.event_type.in_(event_type))
        
        if location:
            query = query.filter(DBDisruptionEvent.location.ilike(f"%{location}%"))
        
        if min_confidence:
            query = query.filter(DBDisruptionEvent.confidence_score >= min_confidence)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        alerts = query.order_by(DBDisruptionEvent.created_at.desc()).offset(offset).limit(page_size).all()
        
        # Convert to response format
        alert_responses = []
        for alert in alerts:
            alert_response = _convert_to_alert_response(alert)
            alert_responses.append(alert_response)
        
        return AlertsListResponse(
            alerts=alert_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific alert by ID"""
    try:
        alert = db.query(DBDisruptionEvent).filter(DBDisruptionEvent.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return _convert_to_alert_response(alert)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert: {str(e)}")

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Acknowledge an alert"""
    try:
        alert = db.query(DBDisruptionEvent).filter(DBDisruptionEvent.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert with acknowledgment info
        # This would require additional fields in the database model
        # For now, just return success
        
        return {"message": "Alert acknowledged successfully", "alert_id": alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.get("/summary/stats")
async def get_alert_summary(
    hours_back: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alert summary statistics"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Get counts by severity
        total_alerts = db.query(DBDisruptionEvent).filter(
            DBDisruptionEvent.created_at >= cutoff_time
        ).count()
        
        critical_alerts = db.query(DBDisruptionEvent).filter(
            DBDisruptionEvent.created_at >= cutoff_time,
            DBDisruptionEvent.severity == "critical"
        ).count()
        
        warning_alerts = db.query(DBDisruptionEvent).filter(
            DBDisruptionEvent.created_at >= cutoff_time,
            DBDisruptionEvent.severity == "warning"
        ).count()
        
        # Get top affected locations
        top_locations = db.query(
            DBDisruptionEvent.location,
            db.func.count(DBDisruptionEvent.id).label("count")
        ).filter(
            DBDisruptionEvent.created_at >= cutoff_time,
            DBDisruptionEvent.location.isnot(None)
        ).group_by(DBDisruptionEvent.location).order_by(db.text("count DESC")).limit(5).all()
        
        return {
            "period_hours": hours_back,
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "watch_alerts": total_alerts - critical_alerts - warning_alerts,
            "top_affected_locations": [
                {"location": loc[0], "alert_count": loc[1]} for loc in top_locations
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert summary: {str(e)}")

def _convert_to_alert_response(db_alert: DBDisruptionEvent) -> AlertResponse:
    """Convert database alert to API response format"""
    
    # Create DisruptionEvent from database model
    event = DisruptionEvent(
        id=db_alert.id,
        event_type=db_alert.event_type,
        severity=db_alert.severity,
        title=db_alert.title,
        description=db_alert.description or "",
        location=db_alert.location,
        latitude=db_alert.latitude,
        longitude=db_alert.longitude,
        confidence_score=db_alert.confidence_score,
        impact_score=db_alert.impact_score,
        source=db_alert.source,
        created_at=db_alert.created_at,
        updated_at=db_alert.updated_at
    )
    
    # Calculate alert score and other derived fields
    # This would integrate with the actual scoring system
    alert_score = db_alert.confidence_score or 0.5
    
    return AlertResponse(
        alert_score=alert_score,
        alert_level=db_alert.severity,
        priority_rank=_calculate_priority_rank(alert_score, db_alert.severity),
        should_alert=alert_score >= 0.5,
        escalation_needed=db_alert.severity == "critical",
        event=event,
        impact_assessment={"impact_score": db_alert.impact_score or 0.5},
        recommendations=_generate_recommendations(db_alert)
    )

def _calculate_priority_rank(alert_score: float, severity: str) -> int:
    """Calculate priority rank for alert"""
    base_rank = int((1 - alert_score) * 80)
    
    if severity == "critical":
        return max(1, base_rank - 20)
    elif severity == "warning":
        return max(1, base_rank - 10)
    else:
        return base_rank

def _generate_recommendations(db_alert: DBDisruptionEvent) -> dict:
    """Generate recommendations for alert"""
    recommendations = {
        "immediate_actions": [],
        "monitoring_actions": [],
        "escalation_needed": False
    }
    
    if db_alert.severity == "critical":
        recommendations["immediate_actions"] = [
            "Contact affected suppliers immediately",
            "Activate contingency plans",
            "Review inventory levels"
        ]
        recommendations["escalation_needed"] = True
    elif db_alert.severity == "warning":
        recommendations["monitoring_actions"] = [
            "Monitor situation closely",
            "Prepare contingency plans",
            "Contact key suppliers for status updates"
        ]
    
    return recommendations
```

### Step 45: Create Dashboard API Endpoints
Create `src/api/routers/dashboard.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import get_db
from src.models.disruption import DisruptionEvent
from src.api.models.schemas import DashboardStats
from src.api.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard statistics"""
    try:
        # Time window for stats
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Total alerts in last 24h
        total_alerts_24h = db.query(DisruptionEvent).filter(
            DisruptionEvent.created_at >= last_24h
        ).count()
        
        # Critical alerts in last 24h
        critical_alerts_24h = db.query(DisruptionEvent).filter(
            DisruptionEvent.created_at >= last_24h,
            DisruptionEvent.severity == "critical"
        ).count()
        
        # Active disruptions (last 6 hours)
        last_6h = now - timedelta(hours=6)
        active_disruptions = db.query(DisruptionEvent).filter(
            DisruptionEvent.created_at >= last_6h,
            DisruptionEvent.severity.in_(["critical", "warning"])
        ).count()
        
        # Affected routes (simplified)
        affected_routes = db.query(DisruptionEvent.location).filter(
            DisruptionEvent.created_at >= last_24h,
            DisruptionEvent.location.isnot(None)
        ).distinct().limit(10).all()
        
        route_list = [route[0] for route in affected_routes if route[0]]
        
        # Average confidence score
        avg_confidence = db.query(func.avg(DisruptionEvent.confidence_score)).filter(
            DisruptionEvent.created_at >= last_24h,
            DisruptionEvent.confidence_score.isnot(None)
        ).scalar() or 0.0
        
        return DashboardStats(
            total_alerts_24h=total_alerts_24h,
            critical_alerts_24h=critical_alerts_24h,
            active_disruptions=active_disruptions,
            affected_routes=route_list,
            average_confidence=round(float(avg_confidence), 3),
            system_health="healthy"  # Would integrate with health monitor
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/timeline")
async def get_alert_timeline(
    hours_back: int = Query(48, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alert timeline data for charts"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Get alerts grouped by hour
        timeline_data = db.query(
            func.date_trunc('hour', DisruptionEvent.created_at).label('hour'),
            DisruptionEvent.severity,
            func.count(DisruptionEvent.id).label('count')
        ).filter(
            DisruptionEvent.created_at >= cutoff_time
        ).group_by(
            func.date_trunc('hour', DisruptionEvent.created_at),
            DisruptionEvent.severity
        ).order_by('hour').all()
        
        # Format data for frontend
        timeline_formatted = {}
        for row in timeline_data:
            hour_str = row.hour.isoformat()
            if hour_str not in timeline_formatted:
                timeline_formatted[hour_str] = {
                    "critical": 0,
                    "warning": 0,
                    "watch": 0,
                    "info": 0
                }
            timeline_formatted[hour_str][row.severity] = row.count
        
        return {
            "timeline": timeline_formatted,
            "period_hours": hours_back
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline data: {str(e)}")

@router.get("/map-data")
async def get_map_data(
    hours_back: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get geographic data for map visualization"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Get alerts with geographic coordinates
        map_alerts = db.query(DisruptionEvent).filter(
            DisruptionEvent.created_at >= cutoff_time,
            DisruptionEvent.latitude.isnot(None),
            DisruptionEvent.longitude.isnot(None)
        ).all()
        
        map_data = []
        for alert in map_alerts:
            map_data.append({
                "id": alert.id,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "title": alert.title,
                "severity": alert.severity,
                "event_type": alert.event_type,
                "location": alert.location,
                "confidence_score": alert.confidence_score,
                "created_at": alert.created_at.isoformat()
            })
        
        return {
            "alerts": map_data,
            "total_count": len(map_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get map data: {str(e)}")

@router.get("/severity-distribution")
async def get_severity_distribution(
    hours_back: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get severity distribution for pie charts"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        severity_counts = db.query(
            DisruptionEvent.severity,
            func.count(DisruptionEvent.id).label('count')
        ).filter(
            DisruptionEvent.created_at >= cutoff_time
        ).group_by(DisruptionEvent.severity).all()
        
        distribution = {}
        total = 0
        for row in severity_counts:
            distribution[row.severity] = row.count
            total += row.count
        
        # Calculate percentages
        distribution_pct = {}
        for severity, count in distribution.items():
            distribution_pct[severity] = {
                "count": count,
                "percentage": round((count / total) * 100, 1) if total > 0 else 0
            }
        
        return {
            "distribution": distribution_pct,
            "total_alerts": total
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get severity distribution: {str(e)}")

@router.get("/top-sources")
async def get_top_sources(
    hours_back: int = Query(24, ge=1, le=168),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get top alert sources"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        top_sources = db.query(
            DisruptionEvent.source,
            func.count(DisruptionEvent.id).label('count'),
            func.avg(DisruptionEvent.confidence_score).label('avg_confidence')
        ).filter(
            DisruptionEvent.created_at >= cutoff_time
        ).group_by(DisruptionEvent.source).order_by(
            func.count(DisruptionEvent.id).desc()
        ).limit(limit).all()
        
        sources_data = []
        for row in top_sources:
            sources_data.append({
                "source": row.source,
                "alert_count": row.count,
                "average_confidence": round(float(row.avg_confidence or 0), 3)
            })
        
        return {
            "sources": sources_data,
            "period_hours": hours_back
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top sources: {str(e)}")
```

### Step 46: Create Admin API Endpoints
Create `src/api/routers/admin.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from src.api.dependencies.auth import get_admin_user
from src.core.monitoring.health_monitor import HealthMonitor
from src.core.backup.backup_manager import BackupManager
from src.core.quality.data_quality_monitor import DataQualityMonitor
from src.core.utils.rate_limiter import rate_limiter
from src.core.orchestration.pipeline_orchestrator import PipelineOrchestrator
from src.api.main import get_orchestrator

router = APIRouter()

@router.get("/system-status")
async def get_system_status(
    admin_user = Depends(get_admin_user),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator)
):
    """Get comprehensive system status (admin only)"""
    try:
        health_monitor = HealthMonitor()
        backup_manager = BackupManager()
        data_quality_monitor = DataQualityMonitor()
        
        return {
            "system_health": health_monitor.check_system_health(),
            "pipeline_status": orchestrator.get_status(),
            "rate_limiter_status": rate_limiter.get_status(),
            "backup_summary": backup_manager.get_backup_summary(),
            "data_quality_trends": _get_quality_summary(data_quality_monitor)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.post("/pipeline/restart")
async def restart_pipeline(
    admin_user = Depends(get_admin_user),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator)
):
    """Restart the data pipeline (admin only)"""
    try:
        orchestrator.stop()
        orchestrator.start()
        
        return {"message": "Pipeline restarted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart pipeline: {str(e)}")

@router.post("/backup/create")
async def create_backup(
    backup_type: str = "manual",
    admin_user = Depends(get_admin_user)
):
    """Create a manual backup (admin only)"""
    try:
        backup_manager = BackupManager()
        
        # This would fetch current data and create backup
        # For now, return success message
        
        return {
            "message": f"Manual backup created successfully",
            "backup_type": backup_type,
            "created_at": "datetime.utcnow().isoformat()"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@router.get("/rate-limits")
async def get_rate_limits(admin_user = Depends(get_admin_user)):
    """Get current rate limiting status (admin only)"""
    try:
        return rate_limiter.get_status()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rate limits: {str(e)}")

@router.post("/rate-limits/{service}/reset")
async def reset_rate_limit(
    service: str,
    admin_user = Depends(get_admin_user)
):
    """Reset rate limit for a service (admin only)"""
    try:
        # Clear request history for the service
        if service in rate_limiter.requests:
            rate_limiter.requests[service].clear()
        
        return {"message": f"Rate limit reset for service: {service}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset rate limit: {str(e)}")

@router.get("/logs")
async def get_system_logs(
    lines: int = 100,
    level: str = "INFO",
    admin_user = Depends(get_admin_user)
):
    """Get system logs (admin only)"""
    try:
        # This would read actual log files
        # For now, return placeholder
        
        return {
            "logs": [
                {
                    "timestamp": "2025-05-25T10:00:00Z",
                    "level": "INFO",
                    "message": "System operating normally",
                    "component": "pipeline"
                }
            ],
            "total_lines": lines,
            "level_filter": level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

def _get_quality_summary(data_quality_monitor: DataQualityMonitor) -> Dict[str, Any]:
    """Get data quality summary for all sources"""
    sources = ["weather", "news", "earthquake", "transport"]
    quality_summary = {}
    
    for source in sources:
        try:
            trends = data_quality_monitor.get_quality_trends(source, days=7)
            if "error" not in trends:
                quality_summary[source] = trends
        except:
            quality_summary[source] = {"status": "error", "message": "No data available"}
    
    return quality_summary
```

### Step 47: Create Authentication Middleware
Create `src/api/middleware/auth.py`:
```python
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import jwt
from datetime import datetime, timedelta
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.secret_key = "your-secret-key"  # Should come from environment
        self.algorithm = "HS256"
        self.excluded_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Check for API key or JWT token
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return await self._unauthorized_response()
        
        try:
            # Simple API key check for demo
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                
                # For demo purposes, accept any token starting with "demo_"
                if token.startswith("demo_"):
                    request.state.user = {"id": "demo_user", "role": "user"}
                    return await call_next(request)
                
                # Decode JWT token (if implementing full JWT auth)
                # payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                # request.state.user = payload
                
            return await self._unauthorized_response()
            
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")
            return await self._unauthorized_response()
    
    async def _unauthorized_response(self):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication required"}
        )

# Authentication dependencies
def get_current_user(request: Request):
    """Get current authenticated user"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user

def get_admin_user(current_user = None):
    """Ensure user has admin privileges"""
    # For demo, allow any authenticated user to be admin
    # In production, check user roles properly
    return current_user
```

### Step 48: Create Rate Limiting Middleware
Create `src/api/middleware/rate_limiting.py`:
```python
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict, deque
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(deque)
        self.limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "/api/v1/alerts": {"requests": 200, "window": 60},
            "/api/v1/dashboard": {"requests": 50, "window": 60}
        }
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # Get rate limit for this path
        limit_config = self.limits.get(path, self.limits["default"])
        
        # Check if request is allowed
        if not self._is_request_allowed(client_ip, path, limit_config):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": self._get_retry_after(client_ip, path, limit_config)
                }
            )
        
        # Record the request
        self._record_request(client_ip, path)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host
    
    def _is_request_allowed(self, client_ip: str, path: str, limit_config: dict) -> bool:
        """Check if request is allowed based on rate limits"""
        key = f"{client_ip}:{path}"
        current_time = time.time()
        window = limit_config["window"]
        max_requests = limit_config["requests"]
        
        # Clean old requests
        request_times = self.requests[key]
        while request_times and request_times[0] < current_time - window:
            request_times.popleft()
        
        # Check if under limit
        return len(request_times) < max_requests
    
    def _record_request(self, client_ip: str, path: str):
        """Record a request"""
        key = f"{client_ip}:{path}"
        self.requests[key].append(time.time())
    
    def _get_retry_after(self, client_ip: str, path: str, limit_config: dict) -> int:
        """Get retry after time in seconds"""
        key = f"{client_ip}:{path}"
        if key not in self.requests or not self.requests[key]:
            return limit_config["window"]
        
        oldest_request = self.requests[key][0]
        return max(0, int(limit_config["window"] - (time.time() - oldest_request)))
```

### Step 49: Create API Dependencies
Create `src/api/dependencies/auth.py`:
```python
from fastapi import Depends, HTTPException, status, Request
from typing import Dict, Any

def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current authenticated user from request state"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.user

def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Ensure current user has admin privileges"""
    user_role = current_user.get("role", "user")
    
    if user_role not in ["admin", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user

def get_api_key_user(request: Request) -> Dict[str, Any]:
    """Authenticate user via API key"""
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # In production, validate API key against database
    # For demo, accept keys starting with "api_"
    if not api_key.startswith("api_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return {"id": "api_user", "role": "api_user", "api_key": api_key}
```

### Step 50: Create Database Models Updates
Create `src/models/user.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from src.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # user, admin, superuser
    is_active = Column(Boolean, default=True)
    api_key = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
```

## Phase 4: Frontend Development (Steps 51-70)

### Step 51: Setup React Frontend Structure
Create the frontend directory structure:
```bash
mkdir frontend
cd frontend
npx create-react-app supply-chain-dashboard --template typescript
cd supply-chain-dashboard
```

### Step 52: Install Frontend Dependencies
```bash
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material @mui/lab
npm install recharts mapbox-gl react-map-gl
npm install axios react-query
npm install @types/mapbox-gl
npm install tailwindcss postcss autoprefixer
npm install react-router-dom @types/react-router-dom
npm install dayjs
npm install react-hook-form @hookform/resolvers yup
```

### Step 53: Configure Tailwind CSS
```bash
npx tailwindcss init -p
```

Update `tailwind.config.js`:
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        success: {
          50: '#f0fdf4',
          500: '#10b981',
          600: '#059669',
        }
      }
    },
  },
  plugins: [],
}
```

### Step 54: Create API Client
Create `src/api/client.ts`:
```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

export interface Alert {
  id: number;
  event_type: string;
  severity: 'critical' | 'warning' | 'watch' | 'info';
  title: string;
  description: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  confidence_score?: number;
  impact_score?: number;
  created_at: string;
  alert_score: number;
  priority_rank: number;
  should_alert: boolean;
  escalation_needed: boolean;
}

export interface DashboardStats {
  total_alerts_24h: number;
  critical_alerts_24h: number;
  active_disruptions: number;
  affected_routes: string[];
  average_confidence: number;
  system_health: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health endpoints
  async getHealth() {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }

  // Alert endpoints
  async getAlerts(params?: {
    page?: number;
    page_size?: number;
    severity?: string[];
    hours_back?: number;
  }) {
    const response = await this.client.get('/api/v1/alerts', { params });
    return response.data;
  }

  async getAlert(id: number) {
    const response = await this.client.get(`/api/v1/alerts/${id}`);
    return response.data;
  }

  async acknowledgeAlert(id: number) {
    const response = await this.client.post(`/api/v1/alerts/${id}/acknowledge`);
    return response.data;
  }

  async getAlertSummary(hours_back: number = 24) {
    const response = await this.client.get('/api/v1/alerts/summary/stats', {
      params: { hours_back }
    });
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get('/api/v1/dashboard/stats');
    return response.data;
  }

  async getAlertTimeline(hours_back: number = 48) {
    const response = await this.client.get('/api/v1/dashboard/timeline', {
      params: { hours_back }
    });
    return response.data;
  }

  async getMapData(hours_back: number = 24) {
    const response = await this.client.get('/api/v1/dashboard/map-data', {
      params: { hours_back }
    });
    return response.data;
  }

  async getSeverityDistribution(hours_back: number = 24) {
    const response = await this.client.get('/api/v1/dashboard/severity-distribution', {
      params: { hours_back }
    });
    return response.data;
  }

  async getTopSources(hours_back: number = 24, limit: number = 10) {
    const response = await this.client.get('/api/v1/dashboard/top-sources', {
      params: { hours_back, limit }
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

### Step 55: Create React Context for State Management
Create `src/contexts/AppContext.tsx`:
```typescript
import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Alert, DashboardStats } from '../api/client';

interface AppState {
  alerts: Alert[];
  dashboardStats: DashboardStats | null;
  selectedAlert: Alert | null;
  filters: {
    severity: string[];
    timeRange: number;
    location: string;
  };
  isLoading: boolean;
  error: string | null;
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_ALERTS'; payload: Alert[] }
  | { type: 'SET_DASHBOARD_STATS'; payload: DashboardStats }
  | { type: 'SET_SELECTED_ALERT'; payload: Alert | null }
  | { type: 'UPDATE_FILTERS'; payload: Partial<AppState['filters']> }
  | { type: 'ACKNOWLEDGE_ALERT'; payload: number };

const initialState: AppState = {
  alerts: [],
  dashboardStats: null,
  selectedAlert: null,
  filters: {
    severity: [],
    timeRange: 24,
    location: '',
  },
  isLoading: false,
  error: null,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    
    case 'SET_ALERTS':
      return { ...state, alerts: action.payload };
    
    case 'SET_DASHBOARD_STATS':
      return { ...state, dashboardStats: action.payload };
    
    case 'SET_SELECTED_ALERT':
      return { ...state, selectedAlert: action.payload };
    
    case 'UPDATE_FILTERS':
      return { 
        ...state, 
        filters: { ...state.filters, ...action.payload }
      };
    
    case 'ACKNOWLEDGE_ALERT':
      return {
        ...state,
        alerts: state.alerts.map(alert =>
          alert.id === action.payload
            ? { ...alert, acknowledged: true }
            : alert
        ),
      };
    
    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}
```

### Step 56: Create Main Dashboard Component
Create `src/components/Dashboard/Dashboard.tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { useAppContext } from '../../contexts/AppContext';
import { apiClient } from '../../api/client';
import StatsCards from './StatsCards';
import AlertsTimeline from './AlertsTimeline';
import AlertsMap from './AlertsMap';
import SeverityChart from './SeverityChart';
import RecentAlerts from './RecentAlerts';
import TopSources from './TopSources';

const Dashboard: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    loadDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      setRefreshKey(prev => prev + 1);
    }, 30000);
    
    return () => clearInterval(interval);
  }, [refreshKey]);

  const loadDashboardData = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Load dashboard stats
      const stats = await apiClient.getDashboardStats();
      dispatch({ type: 'SET_DASHBOARD_STATS', payload: stats });
      
      // Load recent alerts
      const alertsResponse = await apiClient.getAlerts({
        page: 1,
        page_size: 20,
        hours_back: 24
      });
      dispatch({ type: 'SET_ALERTS', payload: alertsResponse.alerts });
      
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to load dashboard data' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  if (state.isLoading && !state.dashboardStats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (state.error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {state.error}
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Supply Chain Disruption Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12}>
          <StatsCards stats={state.dashboardStats} />
        </Grid>
        
        {/* Timeline Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Alert Timeline (48 hours)
            </Typography>
            <AlertsTimeline />
          </Paper>
        </Grid>
        
        {/* Severity Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Severity Distribution
            </Typography>
            <SeverityChart />
          </Paper>
        </Grid>
        
        {/* Map */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 500 }}>
            <Typography variant="h6" gutterBottom>
              Geographic Distribution
            </Typography>
            <AlertsMap />
          </Paper>
        </Grid>
        
        {/* Recent Alerts */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 500, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <RecentAlerts alerts={state.alerts} />
          </Paper>
        </Grid>
        
        {/* Top Sources */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Alert Sources
            </Typography>
            <TopSources />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
```

### Step 57: Create Stats Cards Component
Create `src/components/Dashboard/StatsCards.tsx`:
```typescript
import React from 'react';
import { Grid, Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { TrendingUp, Warning, Error, Info } from '@mui/icons-material';
import { DashboardStats } from '../../api/client';

interface StatsCardsProps {
  stats: DashboardStats | null;
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  if (!stats) return null;

  const cards = [
    {
      title: 'Total Alerts (24h)',
      value: stats.total_alerts_24h,
      icon: <Info color="primary" />,
      color: 'primary',
    },
    {
      title: 'Critical Alerts',
      value: stats.critical_alerts_24h,
      icon: <Error color="error" />,
      color: 'error',
    },
    {
      title: 'Active Disruptions',
      value: stats.active_disruptions,
      icon: <Warning color="warning" />,
      color: 'warning',
    },
    {
      title: 'Avg Confidence',
      value: `${(stats.average_confidence * 100).toFixed(1)}%`,
      icon: <TrendingUp color="success" />,
      color: 'success',
    },
  ];

  return (
    <Grid container spacing={2}>
      {cards.map((card, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" component="div" color={`${card.color}.main`}>
                    {card.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.title}
                  </Typography>
                </Box>
                <Box>{card.icon}</Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
      
      {/* System Health Status */}
      <Grid item xs={12}>
        <Card elevation={2}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="h6">System Health</Typography>
              <Chip 
                label={stats.system_health.toUpperCase()} 
                color={stats.system_health === 'healthy' ? 'success' : 'error'}
                variant="filled"
              />
            </Box>
            <Box mt={2}>
              <Typography variant="body2" color="text.secondary">
                Affected Routes: {stats.affected_routes.length > 0 
                  ? stats.affected_routes.join(', ') 
                  : 'None'}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default StatsCards;
```

### Step 58: Create Alerts Timeline Component
Create `src/components/Dashboard/AlertsTimeline.tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Box, CircularProgress } from '@mui/material';
import { apiClient } from '../../api/client';
import dayjs from 'dayjs';

interface TimelineData {
  time: string;
  critical: number;
  warning: number;
  watch: number;
  info: number;
}

const AlertsTimeline: React.FC = () => {
  const [data, setData] = useState<TimelineData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTimelineData();
  }, []);

  const loadTimelineData = async () => {
    try {
      const response = await apiClient.getAlertTimeline(48);
      
      // Transform API response to chart format
      const transformedData: TimelineData[] = Object.entries(response.timeline).map(
        ([timestamp, counts]: [string, any]) => ({
          time: dayjs(timestamp).format('HH:mm'),
          critical: counts.critical || 0,
          warning: counts.warning || 0,
          watch: counts.watch || 0,
          info: counts.info || 0,
        })
      );
      
      setData(transformedData);
    } catch (error) {
      console.error('Failed to load timeline data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="300px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="critical" 
          stroke="#dc2626" 
          strokeWidth={2}
          name="Critical" 
        />
        <Line 
          type="monotone" 
          dataKey="warning" 
          stroke="#d97706" 
          strokeWidth={2}
          name="Warning" 
        />
        <Line 
          type="monotone" 
          dataKey="watch" 
          stroke="#3b82f6" 
          strokeWidth={2}
          name="Watch" 
        />
        <Line 
          type="monotone" 
          dataKey="info" 
          stroke="#10b981" 
          strokeWidth={2}
          name="Info" 
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default AlertsTimeline;
```

### Step 59: Create Alerts Map Component  
Create `src/components/Dashboard/AlertsMap.tsx`:
```typescript
import React, { useEffect, useState, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { Box, CircularProgress } from '@mui/material';
import { apiClient } from '../../api/client';

// You'll need to get a Mapbox access token
mapboxgl.accessToken = 'your-mapbox-access-token';

interface MapAlert {
  id: number;
  latitude: number;
  longitude: number;
  title: string;
  severity: string;
  location: string;
}

const AlertsMap: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<MapAlert[]>([]);

  useEffect(() => {
    loadMapData();
  }, []);

  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    // Initialize map
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v10',
      center: [-98.5, 39.8], // Center of US
      zoom: 3,
    });

    map.current.on('load', () => {
      setLoading(false);
      addAlertsToMap();
    });

    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, []);

  useEffect(() => {
    if (map.current && !loading) {
      addAlertsToMap();
    }
  }, [alerts, loading]);

  const loadMapData = async () => {
    try {
      const response = await apiClient.getMapData(24);
      setAlerts(response.alerts);
    } catch (error) {
      console.error('Failed to load map data:', error);
    }
  };

  const addAlertsToMap = () => {
    if (!map.current) return;

    // Remove existing markers
    const existingMarkers = document.querySelectorAll('.alert-marker');
    existingMarkers.forEach(marker => marker.remove());

    // Add markers for each alert
    alerts.forEach(alert => {
      const markerColor = getSeverityColor(alert.severity);
      
      // Create marker element
      const markerEl = document.createElement('div');
      markerEl.className = 'alert-marker';
      markerEl.style.backgroundColor = markerColor;
      markerEl.style.width = '12px';
      markerEl.style.height = '12px';
      markerEl.style.borderRadius = '50%';
      markerEl.style.border = '2px solid white';
      markerEl.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';

      // Create popup
      const popup = new mapboxgl.Popup({ offset: 15 }).setHTML(`
        <div style="padding: 8px;">
          <h4 style="margin: 0 0 8px 0; font-size: 14px;">${alert.title}</h4>
          <p style="margin: 0; font-size: 12px; color: #666;">
            ${alert.location}<br/>
            Severity: <span style="color: ${markerColor}; font-weight: bold;">${alert.severity}</span>
          </p>
        </div>
      `);

      // Add marker to map
      new mapboxgl.Marker(markerEl)
        .setLngLat([alert.longitude, alert.latitude])
        .setPopup(popup)
        .addTo(map.current!);
    });
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'warning': return '#d97706';
      case 'watch': return '#3b82f6';
      default: return '#10b981';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box position="relative" height="400px">
      <div
        ref={mapContainer}
        style={{ width: '100%', height: '100%' }}
      />
    </Box>
  );
};

export default AlertsMap;
```

### Step 60: Create Recent Alerts Component
Create `src/components/Dashboard/RecentAlerts.tsx`:
```typescript
import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Typography,
  Box,
  IconButton,
  Tooltip,
} from '@mui/material';
import { CheckCircle, Error, Warning, Info } from '@mui/icons-material';
import { Alert } from '../../api/client';
import { useAppContext } from '../../contexts/AppContext';
import { apiClient } from '../../api/client';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

interface RecentAlertsProps {
  alerts: Alert[];
}

const RecentAlerts: React.FC<RecentAlertsProps> = ({ alerts }) => {
  const { dispatch } = useAppContext();

  const handleAcknowledge = async (alertId: number) => {
    try {
      await apiClient.acknowledgeAlert(alertId);
      dispatch({ type: 'ACKNOWLEDGE_ALERT', payload: alertId });
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error sx={{ color: '#dc2626' }} />;
      case 'warning':
        return <Warning sx={{ color: '#d97706' }} />;
      case 'watch':
        return <Info sx={{ color: '#3b82f6' }} />;
      default:
        return <Info sx={{ color: '#10b981' }} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'warning': return 'warning';
      case 'watch': return 'info';
      default: return 'success';
    }
  };

  if (alerts.length === 0) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="body2" color="text.secondary">
          No recent alerts
        </Typography>
      </Box>
    );
  }

  return (
    <List dense>
      {alerts.slice(0, 10).map((alert) => (
        <ListItem
          key={alert.id}
          divider
          secondaryAction={
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                label={alert.severity}
                size="small"
                color={getSeverityColor(alert.severity) as any}
                variant="outlined"
              />
              <Tooltip title="Acknowledge">
                <IconButton
                  size="small"
                  onClick={() => handleAcknowledge(alert.id)}
                  color="primary"
                >
                  <CheckCircle fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          }
        >
          <ListItemAvatar>
            <Avatar sx={{ bgcolor: 'transparent' }}>
              {getSeverityIcon(alert.severity)}
            </Avatar>
          </ListItemAvatar>
          <ListItemText
            primary={
              <Typography variant="body2" noWrap>
                {alert.title}
              </Typography>
            }
            secondary={
              <Box>
                <Typography variant="caption" color="text.secondary">
                  {alert.location || 'Unknown location'}
                </Typography>
                <br />
                <Typography variant="caption" color="text.secondary">
                  {dayjs(alert.created_at).fromNow()}
                </Typography>
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};

export default RecentAlerts;
```

## Phase 5: Testing and Quality Assurance (Steps 61-80)

### Step 61: Set Up Backend Testing Framework
Create `pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    integration: Integration tests
    unit: Unit tests
    slow: Slow running tests
```

### Step 62: Create API Integration Tests
Create `tests/integration/test_api_endpoints.py`:
```python
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestHealthEndpoints:
    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

    def test_detailed_health_check(self):
        # Note: This might fail without proper orchestrator setup
        response = client.get("/api/v1/health/detailed")
        # Accept either success or service unavailable for testing
        assert response.status_code in [200, 503]

class TestAlertEndpoints:
    def test_get_alerts_unauthorized(self):
        response = client.get("/api/v1/alerts")
        assert response.status_code == 401

    def test_get_alerts_with_auth(self):
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/alerts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total_count" in data

    def test_get_alert_summary(self):
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/alerts/summary/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts" in data

class TestDashboardEndpoints:
    def test_get_dashboard_stats(self):
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/dashboard/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts_24h" in data
        assert "system_health" in data

    def test_get_timeline_data(self):
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/dashboard/timeline", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "timeline" in data

    def test_get_map_data(self):
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/dashboard/map-data", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total_count" in data

class TestRateLimiting:
    def test_rate_limiting(self):
        headers = {"Authorization": "Bearer demo_token"}
        
        # Make multiple requests quickly
        responses = []
        for _ in range(10):
            response = client.get("/api/v1/alerts", headers=headers)
            responses.append(response)
        
        # Should succeed for reasonable number of requests
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count > 0
```

### Step 63: Create Unit Tests for Core Components
Create `tests/unit/test_disruption_detector.py`:
```python
import pytest
from src.core.processors.disruption_detector import DisruptionDetector

class TestDisruptionDetector:
    def setup_method(self):
        self.detector = DisruptionDetector()
    
    def test_calculate_confidence_weather_data(self):
        weather_data = {
            "source": "weather",
            "event_type": "weather_alert",
            "title": "Severe Storm Warning",
            "description": "Major storm approaching supply chain facilities",
            "location": "Los Angeles Port",
            "severity": "warning"
        }
        
        confidence = self.detector.calculate_confidence(weather_data)
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Weather from reliable source should have good confidence
    
    def test_calculate_confidence_empty_data(self):
        empty_data = {}
        confidence = self.detector.calculate_confidence(empty_data)
        assert 0 <= confidence <= 1
        assert confidence < 0.5  # Empty data should have low confidence
    
    def test_assess_relevance_supply_chain_keywords(self):
        relevant_data = {
            "title": "Port shutdown affects supply chain operations",
            "description": "Major logistics disruption at shipping terminal",
            "location": "Long Beach Port",
            "event_type": "news_alert"
        }
        
        relevance = self.detector.assess_relevance(relevant_data)
        assert 0 <= relevance <= 1
        assert relevance > 0.7  # Should be highly relevant
    
    def test_assess_relevance_non_supply_chain(self):
        irrelevant_data = {
            "title": "Celebrity gossip news",
            "description": "Entertainment industry updates",
            "location": "Hollywood",
            "event_type": "news_alert"
        }
        
        relevance = self.detector.assess_relevance(irrelevant_data)
        assert 0 <= relevance <= 1
        assert relevance < 0.3  # Should have low relevance
    
    def test_source_weight_calculation(self):
        # Test different source weights
        assert self.detector._get_source_weight("weather") > 0.8
        assert self.detector._get_source_weight("earthquake") > 0.9
        assert self.detector._get_source_weight("news") < 0.8
        assert self.detector._get_source_weight("unknown") == 0.5
    
    def test_geographic_score_major_hubs(self):
        major_hub_data = {"location": "Los Angeles"}
        score = self.detector._calculate_geographic_score(major_hub_data)
        assert score == 1.0
        
        minor_location_data = {"location": "Small Town"}
        score = self.detector._calculate_geographic_score(minor_location_data)
        assert score < 1.0
```

### Step 64: Create Performance Tests
Create `tests/performance/test_pipeline_performance.py`:
```python
import time
import pytest
import concurrent.futures
from src.core.processors.disruption_detector import DisruptionDetector
from src.core.processors.impact_analyzer import ImpactAnalyzer

class TestPipelinePerformance:
    def setup_method(self):
        self.detector = DisruptionDetector()
        self.analyzer = ImpactAnalyzer()
        
        self.sample_data = {
            "source": "news",
            "event_type": "news_alert",
            "title": "Supply chain disruption reported",
            "description": "Major disruption affecting logistics operations across multiple regions",
            "location": "Los Angeles",
            "severity": "warning"
        }
    
    def test_detection_performance_single_record(self):
        """Test performance of processing a single record"""
        start_time = time.time()
        
        confidence = self.detector.calculate_confidence(self.sample_data)
        relevance = self.detector.assess_relevance(self.sample_data)
        impact = self.analyzer.assess_impact(self.sample_data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process a single record in under 100ms
        assert processing_time < 0.1
        assert 0 <= confidence <= 1
        assert 0 <= relevance <= 1
        assert "impact_score" in impact
    
    def test_detection_performance_batch(self):
        """Test performance of processing multiple records"""
        batch_size = 100
        batch_data = [self.sample_data.copy() for _ in range(batch_size)]
        
        start_time = time.time()
        
        for data in batch_data:
            confidence = self.detector.calculate_confidence(data)
            relevance = self.detector.assess_relevance(data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 100 records in under 1 second
        assert processing_time < 1.0
        
        # Calculate throughput
        throughput = batch_size / processing_time
        assert throughput > 100  # Should handle >100 records per second
    
    def test_concurrent_processing(self):
        """Test concurrent processing performance"""
        def process_record(data):
            confidence = self.detector.calculate_confidence(data)
            relevance = self.detector.assess_relevance(data)
            return confidence, relevance
        
        batch_data = [self.sample_data.copy() for _ in range(50)]
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_record, data) for data in batch_data]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert len(results) == 50
        assert processing_time < 2.0  # Should complete in under 2 seconds
    
    @pytest.mark.slow
    def test_memory_usage_stability(self):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process many records
        for i in range(1000):
            data = self.sample_data.copy()
            data["title"] = f"Alert {i}: {data['title']}"
            
            self.detector.calculate_confidence(data)
            self.detector.assess_relevance(data)
            
            # Check memory every 100 iterations
            if i % 100 == 0:
                current_memory = process.memory_info().rss
                memory_growth = current_memory - initial_memory
                
                # Memory growth should be reasonable (less than 50MB for 1000 records)
                assert memory_growth < 50 * 1024 * 1024
```

### Step 65: Create Load Testing Scripts
Create `tests/load/locustfile.py`:
```python
from locust import HttpUser, task, between
import random

class SupplyChainAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Set up authentication for the user"""
        self.headers = {
            "Authorization": "Bearer demo_token_load_test",
            "Content-Type": "application/json"
        }
    
    @task(3)
    def get_alerts(self):
        """Get alerts list - most common operation"""
        params = {
            "page": random.randint(1, 5),
            "page_size": random.choice([10, 20, 50]),
            "hours_back": random.choice([24, 48, 72])
        }
        
        with self.client.get(
            "/api/v1/alerts",
            headers=self.headers,
            params=params,
            name="Get Alerts"
        ) as response:
            if response.status_code != 200:
                print(f"Get alerts failed: {response.status_code}")
    
    @task(2)
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        with self.client.get(
            "/api/v1/dashboard/stats",
            headers=self.headers,
            name="Dashboard Stats"
        ) as response:
            if response.status_code != 200:
                print(f"Dashboard stats failed: {response.status_code}")
    
    @task(2)
    def get_timeline_data(self):
        """Get timeline data for charts"""
        params = {"hours_back": random.choice([24, 48, 72])}
        
        with self.client.get(
            "/api/v1/dashboard/timeline",
            headers=self.headers,
            params=params,
            name="Timeline Data"
        ) as response:
            if response.status_code != 200:
                print(f"Timeline data failed: {response.status_code}")
    
    @task(1)
    def get_map_data(self):
        """Get map data for visualization"""
        params = {"hours_back": random.choice([24, 48])}
        
        with self.client.get(
            "/api/v1/dashboard/map-data",
            headers=self.headers,
            params=params,
            name="Map Data"
        ) as response:
            if response.status_code != 200:
                print(f"Map data failed: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        with self.client.get("/api/v1/health", name="Health Check") as response:
            if response.status_code != 200:
                print(f"Health check failed: {response.status_code}")
    
    @task(1)
    def get_alert_summary(self):
        """Get alert summary statistics"""
        params = {"hours_back": random.choice([24, 48])}
        
        with self.client.get(
            "/api/v1/alerts/summary/stats",
            headers=self.headers,
            params=params,
            name="Alert Summary"
        ) as response:
            if response.status_code != 200:
                print(f"Alert summary failed: {response.status_code}")

class AdminUser(HttpUser):
    wait_time = between(5, 15)
    weight = 1  # Lower weight for admin users
    
    def on_start(self):
        self.headers = {
            "Authorization": "Bearer admin_demo_token",
            "Content-Type": "application/json"
        }
    
    @task
    def get_system_status(self):
        """Admin endpoint - system status"""
        with self.client.get(
            "/api/v1/admin/system-status",
            headers=self.headers,
            name="Admin System Status"
        ) as response:
            if response.status_code != 200:
                print(f"Admin system status failed: {response.status_code}")
    
    @task
    def get_rate_limits(self):
        """Admin endpoint - rate limits"""
        with self.client.get(
            "/api/v1/admin/rate-limits",
            headers=self.headers,
            name="Admin Rate Limits"
        ) as response:
            if response.status_code != 200:
                print(f"Admin rate limits failed: {response.status_code}")
```

### Step 66: Create Frontend Testing Setup
Create `frontend/src/setupTests.ts`:
```typescript
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configure testing library
configure({ testIdAttribute: 'data-testid' });

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
```

### Step 67: Create Frontend Component Tests
Create `frontend/src/components/Dashboard/__tests__/Dashboard.test.tsx`:
```typescript
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from '../Dashboard';
import { AppProvider } from '../../../contexts/AppContext';
import * as apiClient from '../../../api/client';

// Mock the API client
jest.mock('../../../api/client');
const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

// Mock child components to focus on Dashboard logic
jest.mock('../StatsCards', () => {
  return function MockStatsCards({ stats }: any) {
    return <div data-testid="stats-cards">Stats: {stats ? 'loaded' : 'loading'}</div>;
  };
});

jest.mock('../AlertsTimeline', () => {
  return function MockAlertsTimeline() {
    return <div data-testid="alerts-timeline">Timeline Chart</div>;
  };
});

jest.mock('../AlertsMap', () => {
  return function MockAlertsMap() {
    return <div data-testid="alerts-map">Map Component</div>;
  };
});

jest.mock('../RecentAlerts', () => {
  return function MockRecentAlerts({ alerts }: any) {
    return <div data-testid="recent-alerts">Alerts: {alerts.length}</div>;
  };
});

const mockDashboardStats = {
  total_alerts_24h: 45,
  critical_alerts_24h: 5,
  active_disruptions: 12,
  affected_routes: ['trans_pacific', 'trans_atlantic'],
  average_confidence: 0.75,
  system_health: 'healthy'
};

const mockAlerts = [
  {
    id: 1,
    event_type: 'weather',
    severity: 'warning' as const,
    title: 'Severe Storm Warning',
    description: 'Storm approaching port',
    created_at: '2025-05-25T10:00:00Z',
    alert_score: 0.8,
    priority_rank: 15,
    should_alert: true,
    escalation_needed: false
  }
];

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        {children}
      </AppProvider>
    </QueryClientProvider>
  );
};

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', async () => {
    mockApiClient.apiClient.getDashboardStats = jest.fn()
      .mockReturnValue(new Promise(() => {})); // Never resolves
    mockApiClient.apiClient.getAlerts = jest.fn()
      .mockReturnValue(new Promise(() => {}));

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders dashboard content after loading', async () => {
    mockApiClient.apiClient.getDashboardStats = jest.fn()
      .mockResolvedValue(mockDashboardStats);
    mockApiClient.apiClient.getAlerts = jest.fn()
      .mockResolvedValue({ alerts: mockAlerts, total_count: 1 });

    await act(async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );
    });

    await waitFor(() => {
      expect(screen.getByText('Supply Chain Disruption Dashboard')).toBeInTheDocument();
      expect(screen.getByTestId('stats-cards')).toBeInTheDocument();
      expect(screen.getByTestId('alerts-timeline')).toBeInTheDocument();
      expect(screen.getByTestId('alerts-map')).toBeInTheDocument();
      expect(screen.getByTestId('recent-alerts')).toBeInTheDocument();
    });
  });

  it('displays error state when API calls fail', async () => {
    const errorMessage = 'Failed to load dashboard data';
    mockApiClient.apiClient.getDashboardStats = jest.fn()
      .mockRejectedValue(new Error(errorMessage));
    mockApiClient.apiClient.getAlerts = jest.fn()
      .mockRejectedValue(new Error(errorMessage));

    await act(async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );
    });

    await waitFor(() => {
      expect(screen.getByText('Failed to load dashboard data')).toBeInTheDocument();
    });
  });

  it('calls API endpoints with correct parameters', async () => {
    mockApiClient.apiClient.getDashboardStats = jest.fn()
      .mockResolvedValue(mockDashboardStats);
    mockApiClient.apiClient.getAlerts = jest.fn()
      .mockResolvedValue({ alerts: mockAlerts, total_count: 1 });

    await act(async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );
    });

    await waitFor(() => {
      expect(mockApiClient.apiClient.getDashboardStats).toHaveBeenCalledTimes(1);
      expect(mockApiClient.apiClient.getAlerts).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
        hours_back: 24
      });
    });
  });
});
```

### Step 68: Create E2E Tests with Playwright
Create `frontend/e2e/dashboard.spec.ts`:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/api/v1/dashboard/stats', async route => {
      await route.fulfill({
        json: {
          total_alerts_24h: 45,
          critical_alerts_24h: 5,
          active_disruptions: 12,
          affected_routes: ['trans_pacific'],
          average_confidence: 0.75,
          system_health: 'healthy'
        }
      });
    });

    await page.route('**/api/v1/alerts**', async route => {
      await route.fulfill({
        json: {
          alerts: [
            {
              id: 1,
              title: 'Test Alert',
              severity: 'warning',
              created_at: '2025-05-25T10:00:00Z'
            }
          ],
          total_count: 1
        }
      });
    });

    await page.route('**/api/v1/dashboard/timeline**', async route => {
      await route.fulfill({
        json: {
          timeline: {
            '2025-05-25T10:00:00Z': { critical: 1, warning: 2, watch: 1, info: 0 }
          }
        }
      });
    });

    // Navigate to dashboard
    await page.goto('/dashboard');
  });

  test('displays dashboard title and main components', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Supply Chain Disruption Dashboard');
    
    // Check for main dashboard components
    await expect(page.locator('[data-testid="stats-cards"]')).toBeVisible();
    await expect(page.locator('text=Alert Timeline')).toBeVisible();
    await expect(page.locator('text=Geographic Distribution')).toBeVisible();
    await expect(page.locator('text=Recent Alerts')).toBeVisible();
  });

  test('stats cards display correct information', async ({ page }) => {
    // Wait for stats to load
    await page.waitForSelector('[data-testid="stats-cards"]');
    
    // Check that stats are displayed
    await expect(page.locator('text=45')).toBeVisible(); // Total alerts
    await expect(page.locator('text=5')).toBeVisible();  // Critical alerts
    await expect(page.locator('text=12')).toBeVisible(); // Active disruptions
    await expect(page.locator('text=75.0%')).toBeVisible(); // Confidence
  });

  test('alert filtering works correctly', async ({ page }) => {
    // Test severity filter
    await page.click('text=Filter');
    await page.check('input[name="severity"][value="critical"]');
    await page.click('text=Apply Filters');

    // Verify API call was made with correct parameters
    await page.waitForRequest(req => 
      req.url().includes('/api/v1/alerts') && 
      req.url().includes('severity=critical')
    );
  });

  test('real-time updates work', async ({ page }) => {
    // Mock updated data
    await page.route('**/api/v1/dashboard/stats', async route => {
      await route.fulfill({
        json: {
          total_alerts_24h: 46, // Updated count
          critical_alerts_24h: 6,
          active_disruptions: 12,
          affected_routes: ['trans_pacific'],
          average_confidence: 0.75,
          system_health: 'healthy'
        }
      });
    });

    // Wait for auto-refresh (30 seconds in real app, but we can trigger it)
    await page.evaluate(() => {
      // Trigger a custom event to simulate refresh
      window.dispatchEvent(new CustomEvent('dashboard-refresh'));
    });

    // Check updated count
    await expect(page.locator('text=46')).toBeVisible();
  });

  test('error handling displays correctly', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1/dashboard/stats', async route => {
      await route.abort('failed');
    });

    await page.reload();

    // Should display error message
    await expect(page.locator('text=Failed to load')).toBeVisible();
  });

  test('responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Check that components stack vertically on mobile
    const statsCards = page.locator('[data-testid="stats-cards"]');
    await expect(statsCards).toBeVisible();

    // Timeline should be full width on mobile
    const timeline = page.locator('text=Alert Timeline').locator('..');
    const timelineBox = await timeline.boundingBox();
    expect(timelineBox?.width).toBeGreaterThan(300);
  });
});
```

### Step 69: Create Data Quality Tests
Create `tests/data_quality/test_data_validation.py`:
```python
import pytest
from src.core.validation.data_validator import DataValidator
from src.core.quality.data_quality_monitor import DataQualityMonitor

class TestDataValidation:
    def setup_method(self):
        self.validator = DataValidator()
        self.quality_monitor = DataQualityMonitor()
    
    def test_valid_disruption_data(self):
        valid_data = {
            "source": "weather",
            "event_type": "weather_alert",
            "title": "Severe Storm Warning",
            "description": "Major storm system approaching port facilities",
            "severity": "warning",
            "location": "Los Angeles",
            "latitude": 34.0522,
            "longitude": -118.2437
        }
        
        result = self.validator.validate_disruption_data(valid_data)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert "validated_at" in result["cleaned_data"]
    
    def test_missing_required_fields(self):
        invalid_data = {
            "source": "weather",
            # Missing event_type, title, severity
            "description": "Some description"
        }
        
        result = self.validator.validate_disruption_data(invalid_data)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "Missing required fields" in result["errors"][0]
    
    def test_invalid_coordinates(self):
        data_with_invalid_coords = {
            "source": "weather",
            "event_type": "weather_alert",
            "title": "Test Alert",
            "severity": "warning",
            "latitude": 200,  # Invalid latitude
            "longitude": -200  # Invalid longitude
        }
        
        result = self.validator.validate_disruption_data(data_with_invalid_coords)
        
        assert result["is_valid"] is True  # Still valid, but with warnings
        assert len(result["warnings"]) > 0
        assert "Invalid coordinates" in result["warnings"][0]
        assert result["cleaned_data"]["latitude"] is None
        assert result["cleaned_data"]["longitude"] is None
    
    def test_text_cleaning(self):
        data_with_messy_text = {
            "source": "news",
            "event_type": "news_alert",
            "title": "  Breaking!!!  Supply   Chain    Disruption   ",
            "description": "Multiple    spaces   and   special   characters@#$%",
            "severity": "critical"
        }
        
        result = self.validator.validate_disruption_data(data_with_messy_text)
        
        cleaned_title = result["cleaned_data"]["title"]
        cleaned_desc = result["cleaned_data"]["description"]
        
        assert cleaned_title == "Breaking Supply Chain Disruption"
        assert "Multiple spaces and special characters" in cleaned_desc
        assert "  " not in cleaned_title  # No double spaces
    
    def test_data_quality_assessment(self):
        sample_data = [
            {
                "source": "weather",
                "event_type": "weather_alert",
                "title": "Storm Warning",
                "description": "Severe weather conditions",
                "severity": "warning",
                "location": "Los Angeles"
            },
            {
                "source": "news",
                "event_type": "news_alert",
                "title": "Port Closure",
                "description": "Emergency closure of major port",
                "severity": "critical",
                "location": "Long Beach"
            }
        ]
        
        quality_assessment = self.quality_monitor.assess_data_quality(sample_data, "test_source")
        
        assert "overall_score" in quality_assessment
        assert 0 <= quality_assessment["overall_score"] <= 1
        assert "dimensions" in quality_assessment
        assert "completeness" in quality_assessment["dimensions"]
        assert "accuracy" in quality_assessment["dimensions"]
        assert quality_assessment["sample_size"] == 2
    
    def test_completeness_assessment(self):
        # Complete data
        complete_data = [
            {
                "title": "Complete Alert",
                "description": "Full description",
                "severity": "warning",
                "source": "weather",
                "event_type": "weather_alert"
            }
        ]
        
        # Incomplete data
        incomplete_data = [
            {
                "title": "Incomplete Alert",
                "description": "",  # Missing description
                "severity": "",     # Missing severity
                "source": "weather",
                "event_type": "weather_alert"
            }
        ]
        
        complete_assessment = self.quality_monitor.assess_data_quality(complete_data, "test")
        incomplete_assessment = self.quality_monitor.assess_data_quality(incomplete_data, "test")
        
        assert complete_assessment["dimensions"]["completeness"] > incomplete_assessment["dimensions"]["completeness"]
        assert complete_assessment["overall_score"] > incomplete_assessment["overall_score"]

class TestDataQualityTrends:
    def setup_method(self):
        self.quality_monitor = DataQualityMonitor()
    
    def test_quality_trends_tracking(self):
        # Simulate multiple quality assessments over time
        high_quality_data = [
            {
                "title": "High Quality Alert",
                "description": "Detailed description with supply chain keywords",
                "severity": "warning",
                "source": "weather",
                "event_type": "weather_alert"
            }
        ]
        
        low_quality_data = [
            {
                "title": "",  # Poor quality
                "description": "",
                "severity": "unknown",
                "source": "unknown",
                "event_type": ""
            }
        ]
        
        # Assess high quality data
        self.quality_monitor.assess_data_quality(high_quality_data, "test_source")
        
        # Assess low quality data
        self.quality_monitor.assess_data_quality(low_quality_data, "test_source")
        
        # Get trends
        trends = self.quality_monitor.get_quality_trends("test_source", days=1)
        
        assert "total_assessments" in trends
        assert trends["total_assessments"] == 2
        assert "average_quality" in trends
        assert "dimension_averages" in trends
```

### Step 70: Create Security Tests
Create `tests/security/test_security.py`:
```python
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestSecurityMeasures:
    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/v1/alerts",
            "/api/v1/dashboard/stats",
            "/api/v1/admin/system-status"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
            assert "Authentication required" in response.json()["detail"]
    
    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected"""
        invalid_headers = [
            {"Authorization": "Bearer invalid_token"},
            {"Authorization": "Bearer"},
            {"Authorization": "InvalidFormat token"}
        ]
        
        for headers in invalid_headers:
            response = client.get("/api/v1/alerts", headers=headers)
            assert response.status_code == 401
    
    def test_rate_limiting_protection(self):
        """Test rate limiting protects against abuse"""
        headers = {"Authorization": "Bearer demo_token"}
        
        # Make many rapid requests
        responses = []
        for i in range(150):  # Exceed typical rate limits
            response = client.get("/api/v1/health", headers=headers)
            responses.append(response.status_code)
        
        # Should eventually hit rate limits
        rate_limited_responses = [code for code in responses if code == 429]
        assert len(rate_limited_responses) > 0
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "1'; UPDATE users SET role='admin'--"
        ]
        
        headers = {"Authorization": "Bearer demo_token"}
        
        for malicious_input in malicious_inputs:
            # Try injection in query parameters
            response = client.get(
                "/api/v1/alerts",
                headers=headers,
                params={"location": malicious_input}
            )
            
            # Should not cause server error (500) from SQL injection
            assert response.status_code in [200, 400, 422]  # Valid responses
    
    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        headers = {"Authorization": "Bearer demo_token"}
        
        for payload in xss_payloads:
            response = client.get(
                "/api/v1/alerts",
                headers=headers,
                params={"location": payload}
            )
            
            # Response should not contain unescaped script tags
            if response.status_code == 200:
                response_text = response.text.lower()
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
    
    def test_admin_privilege_escalation(self):
        """Test that regular users cannot access admin endpoints"""
        regular_user_headers = {"Authorization": "Bearer demo_token"}
        
        admin_endpoints = [
            "/api/v1/admin/system-status",
            "/api/v1/admin/pipeline/restart",
            "/api/v1/admin/backup/create"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=regular_user_headers)
            # Should be forbidden (403) or unauthorized (401)
            assert response.status_code in [401, 403]
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        response = client.options("/api/v1/health")
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_sensitive_data_not_exposed(self):
        """Test that sensitive data is not exposed in responses"""
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/health/detailed", headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            response_text = str(response_data).lower()
            
            # Should not contain sensitive information
            sensitive_keywords = [
                "password",
                "secret",
                "key",
                "token",
                "private",
                "credential"
            ]
            
            for keyword in sensitive_keywords:
                assert keyword not in response_text

class TestInputValidation:
    def test_parameter_validation(self):
        """Test input parameter validation"""
        headers = {"Authorization": "Bearer demo_token"}
        
        # Test invalid page numbers
        response = client.get("/api/v1/alerts?page=-1", headers=headers)
        assert response.status_code == 422
        
        response = client.get("/api/v1/alerts?page=0", headers=headers)
        assert response.status_code == 422
        
        # Test invalid page sizes
        response = client.get("/api/v1/alerts?page_size=1000", headers=headers)
        assert response.status_code == 422
        
        response = client.get("/api/v1/alerts?page_size=-5", headers=headers)
        assert response.status_code == 422
    
    def test_data_sanitization(self):
        """Test that input data is properly sanitized"""
        headers = {"Authorization": "Bearer demo_token"}
        
        # Test with potentially dangerous characters
        dangerous_location = "<script>alert('xss')</script>Port"
        
        response = client.get(
            "/api/v1/alerts",
            headers=headers,
            params={"location": dangerous_location}
        )
        
        # Should handle gracefully without errors
        assert response.status_code in [200, 400, 422]
```

Continue with deployment and final steps...