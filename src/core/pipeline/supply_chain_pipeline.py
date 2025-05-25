import pathway as pw
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.services.weather.weather_service import WeatherService
from src.services.news.news_service import NewsService
from src.services.transport.earthquake_service import EarthquakeService
from src.core.detectors.disruption_detector import DisruptionDetector
from src.core.processors.impact_assessor import ImpactAssessor
from src.models.disruption import DisruptionEvent
from src.core.database import SessionLocal
from src.utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

class SupplyChainPipeline:
    def __init__(self):
        self.weather_service = WeatherService()
        self.news_service = NewsService()
        self.earthquake_service = EarthquakeService()
        self.disruption_detector = DisruptionDetector()
        self.impact_assessor = ImpactAssessor()
        
        # Pipeline state
        self.is_running = False
        self.last_refresh = {}
        
        # Data streams
        self.weather_stream = None
        self.news_stream = None
        self.earthquake_stream = None
        self.combined_stream = None
        
    def setup_data_streams(self):
        """Set up Pathway data streams for real-time processing"""
        logger.info("Setting up data streams...")
        
        # Create a simple data source that we can feed data to
        # For now, we'll use a simpler approach with periodic data collection
        self.data_queue = []
        
        # Create a single input stream that we'll populate with data
        self.input_stream = pw.io.python.read(
            pw.io.python.ConnectorSubject(),
            schema=pw.schema_from_types(
                source=str,
                event_type=str,
                title=str,
                description=str,
                severity=str,
                location=str,
                latitude=float,
                longitude=float,
                confidence_score=float,
                timestamp=str,
                magnitude=float,
                url=str
            ),
            mode="streaming"
        )
        
        logger.info("Data streams configured successfully")
    
    def setup_processing_pipeline(self):
        """Set up the main processing pipeline"""
        logger.info("Setting up processing pipeline...")
        
        # Apply disruption detection to the input stream
        disruptions = self.input_stream.select(
            *pw.this,
            disruption_data=pw.apply(self._detect_disruptions, pw.this)
        ).filter(pw.this.disruption_data.is_not_none())
        
        # Apply impact assessment
        assessed_disruptions = disruptions.select(
            *pw.this,
            impact_assessment=pw.apply(self._assess_impact, pw.this.disruption_data)
        )
        
        # Filter for significant disruptions
        significant_disruptions = assessed_disruptions.filter(
            pw.this.impact_assessment["impact_score"] >= settings.alert_threshold
        )
        
        # Store to database
        pw.io.python.write(significant_disruptions, self._store_disruption)
        
        logger.info("Processing pipeline configured successfully")
    
    def collect_data_batch(self):
        """Collect data from all sources and return as a batch"""
        all_data = []
        
        try:
            # Collect weather data
            if self._should_refresh("weather"):
                weather_alerts = self.weather_service.get_weather_alerts()
                for alert in weather_alerts:
                    formatted = self._format_for_pathway(alert)
                    all_data.append(formatted)
                self.last_refresh["weather"] = datetime.utcnow()
                logger.info(f"Collected {len(weather_alerts)} weather alerts")
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}")
        
        try:
            # Collect news data
            if self._should_refresh("news"):
                news_articles = self.news_service.get_supply_chain_news()
                for article in news_articles:
                    formatted = self._format_for_pathway(article)
                    all_data.append(formatted)
                self.last_refresh["news"] = datetime.utcnow()
                logger.info(f"Collected {len(news_articles)} news articles")
        except Exception as e:
            logger.error(f"Error collecting news data: {e}")
        
        try:
            # Collect earthquake data
            if self._should_refresh("earthquake"):
                earthquake_alerts = self.earthquake_service.get_earthquake_alerts()
                for alert in earthquake_alerts:
                    formatted = self._format_for_pathway(alert)
                    all_data.append(formatted)
                self.last_refresh["earthquake"] = datetime.utcnow()
                logger.info(f"Collected {len(earthquake_alerts)} earthquake alerts")
        except Exception as e:
            logger.error(f"Error collecting earthquake data: {e}")
        
        return all_data
    
    def _should_refresh(self, source: str) -> bool:
        """Check if data source should be refreshed"""
        if source not in self.last_refresh:
            return True
        
        refresh_intervals = {
            "weather": settings.weather_refresh_interval,
            "news": settings.news_refresh_interval,
            "earthquake": settings.earthquake_refresh_interval
        }
        
        interval = refresh_intervals.get(source, 300)
        time_since_refresh = (datetime.utcnow() - self.last_refresh[source]).total_seconds()
        
        return time_since_refresh >= interval
    
    def _format_for_pathway(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for Pathway processing"""
        formatted = {
            "source": data.get("source", "unknown"),
            "event_type": data.get("event_type", "unknown"),
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "severity": data.get("severity", "watch"),
            "location": data.get("location", ""),
            "confidence_score": data.get("confidence_score", 0.5),
            "timestamp": datetime.utcnow().isoformat(),
            "latitude": float(data.get("latitude", 0.0)),
            "longitude": float(data.get("longitude", 0.0)),
            "magnitude": float(data.get("magnitude", 0.0)),
            "url": data.get("url", "")
        }
        
        return formatted
    
    def _detect_disruptions(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Apply disruption detection to a data row"""
        try:
            # Convert row to format expected by disruption detector
            data_batch = [row]
            disruptions = self.disruption_detector.detect_disruptions(data_batch)
            
            if disruptions:
                return disruptions[0]  # Return first disruption
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in disruption detection: {e}")
            return None
    
    def _assess_impact(self, disruption: Dict[str, Any]) -> Dict[str, Any]:
        """Apply impact assessment to a disruption"""
        try:
            return self.impact_assessor.assess_impact(disruption)
        except Exception as e:
            logger.error(f"Error in impact assessment: {e}")
            return {"error": str(e)}
    
    def _store_disruption(self, row: Dict[str, Any]):
        """Store disruption to database"""
        try:
            db = SessionLocal()
            
            impact_assessment = row.get("impact_assessment", {})
            disruption_data = row.get("disruption_data", {})
            source_data = disruption_data.get("source_data", {})
            
            # Create disruption event record
            disruption_event = DisruptionEvent(
                event_type=source_data.get("event_type", "unknown"),
                severity=impact_assessment.get("severity_level", "low"),
                title=source_data.get("title", ""),
                description=source_data.get("description", ""),
                location=source_data.get("location", ""),
                latitude=source_data.get("latitude"),
                longitude=source_data.get("longitude"),
                confidence_score=source_data.get("confidence_score", 0.5),
                impact_score=impact_assessment.get("impact_score", 0.0),
                source=source_data.get("source", "unknown"),
                alert_level=impact_assessment.get("severity_level", "low"),
                priority_rank=self._calculate_priority_rank(impact_assessment),
                affected_routes=json.dumps(impact_assessment.get("affected_routes", [])),
                mitigation_strategies=json.dumps(impact_assessment.get("mitigation_strategies", [])),
                financial_impact=json.dumps(impact_assessment.get("financial_impact", {})),
                is_active=True
            )
            
            db.add(disruption_event)
            db.commit()
            
            logger.info(f"Stored disruption: {disruption_event.title}")
            
        except Exception as e:
            logger.error(f"Error storing disruption: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
    
    def _calculate_priority_rank(self, impact_assessment: Dict[str, Any]) -> int:
        """Calculate priority rank (1-100, where 1 is highest priority)"""
        impact_score = impact_assessment.get("impact_score", 0.5)
        
        # Convert impact score to priority rank (inverted)
        priority_rank = int((1.0 - impact_score) * 100)
        return max(1, min(100, priority_rank))
    
    def start(self):
        """Start the pipeline"""
        logger.info("Starting Supply Chain Pipeline...")
        
        self.is_running = True
        
        # For now, we'll use a simpler batch processing approach
        # instead of the complex Pathway streaming setup
        logger.info("Supply Chain Pipeline started successfully in batch mode")
    
    def stop(self):
        """Stop the pipeline"""
        logger.info("Stopping Supply Chain Pipeline...")
        self.is_running = False
        logger.info("Supply Chain Pipeline stopped")
    
    def process_batch(self):
        """Process a batch of data manually"""
        if not self.is_running:
            return []
        
        try:
            # Collect data from all sources
            data_batch = self.collect_data_batch()
            
            if not data_batch:
                return []
            
            # Process each data item
            processed_disruptions = []
            
            for data_item in data_batch:
                # Detect disruptions
                disruption_data = self._detect_disruptions(data_item)
                
                if disruption_data:
                    # Assess impact
                    impact_assessment = self._assess_impact(disruption_data)
                    
                    # Check if significant enough to store
                    if impact_assessment.get("impact_score", 0) >= settings.alert_threshold:
                        # Store to database
                        combined_data = {
                            "disruption_data": disruption_data,
                            "impact_assessment": impact_assessment
                        }
                        self._store_disruption(combined_data)
                        processed_disruptions.append(combined_data)
            
            logger.info(f"Processed {len(data_batch)} data items, found {len(processed_disruptions)} significant disruptions")
            return processed_disruptions
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        return {
            "is_running": self.is_running,
            "last_refresh": {
                source: refresh_time.isoformat() if refresh_time else None
                for source, refresh_time in self.last_refresh.items()
            },
            "next_refresh": {
                source: (refresh_time + timedelta(seconds=settings.weather_refresh_interval)).isoformat()
                if refresh_time else None
                for source, refresh_time in self.last_refresh.items()
            }
        } 