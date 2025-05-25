import pytest
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.detectors.disruption_detector import DisruptionDetector
from src.core.processors.impact_assessor import ImpactAssessor
from src.services.weather.weather_service import WeatherService
from src.services.news.news_service import NewsService
from src.services.transport.earthquake_service import EarthquakeService

class TestDisruptionDetector:
    def setup_method(self):
        self.detector = DisruptionDetector()
    
    def test_detector_initialization(self):
        """Test that the disruption detector initializes correctly"""
        assert self.detector is not None
        assert hasattr(self.detector, 'supply_chain_sectors')
        assert hasattr(self.detector, 'trade_routes')
        assert hasattr(self.detector, 'disruption_keywords')
    
    def test_supply_chain_relevance_detection(self):
        """Test supply chain relevance detection"""
        # Relevant record
        relevant_record = {
            "title": "Port of Los Angeles experiences shipping delays",
            "description": "Supply chain disruption at major port facility"
        }
        assert self.detector._is_supply_chain_relevant(relevant_record) == True
        
        # Irrelevant record
        irrelevant_record = {
            "title": "Local restaurant opens new location",
            "description": "New dining establishment in downtown area"
        }
        assert self.detector._is_supply_chain_relevant(irrelevant_record) == False
    
    def test_disruption_score_calculation(self):
        """Test disruption score calculation"""
        high_impact_record = {
            "title": "Major port shutdown due to earthquake",
            "description": "Critical supply chain disruption at Los Angeles port",
            "event_type": "earthquake",
            "magnitude": 6.5,
            "severity": "critical",
            "location": "Los Angeles Port",
            "confidence_score": 0.9
        }
        
        score = self.detector._calculate_disruption_score(high_impact_record)
        assert score > 0.5  # Should be high impact
        
        low_impact_record = {
            "title": "Minor weather advisory",
            "description": "Light rain expected in the area",
            "event_type": "weather",
            "severity": "watch",
            "location": "Unknown",
            "confidence_score": 0.3
        }
        
        score = self.detector._calculate_disruption_score(low_impact_record)
        assert score < 0.5  # Should be low impact
    
    def test_disruption_type_classification(self):
        """Test disruption type classification"""
        earthquake_record = {
            "title": "Earthquake hits manufacturing region",
            "description": "Seismic activity affects production facilities",
            "event_type": "earthquake"
        }
        
        disruption_type = self.detector._classify_disruption_type(earthquake_record)
        assert disruption_type == "natural_disaster"
        
        labor_record = {
            "title": "Port workers go on strike",
            "description": "Labor union calls for work stoppage at major port",
            "event_type": "news_alert"
        }
        
        disruption_type = self.detector._classify_disruption_type(labor_record)
        assert disruption_type == "labor_disruption"

class TestImpactAssessor:
    def setup_method(self):
        self.assessor = ImpactAssessor()
    
    def test_assessor_initialization(self):
        """Test that the impact assessor initializes correctly"""
        assert self.assessor is not None
        assert hasattr(self.assessor, 'trade_routes')
    
    def test_impact_score_calculation(self):
        """Test impact score calculation"""
        high_impact_disruption = {
            "disruption_score": 0.8,
            "geographic_scope": "trade_route_suez_canal",
            "urgency_level": "immediate"
        }
        
        score = self.assessor._calculate_impact_score(high_impact_disruption)
        assert score > 0.8  # Should be high impact
        
        low_impact_disruption = {
            "disruption_score": 0.3,
            "geographic_scope": "regional",
            "urgency_level": "low"
        }
        
        score = self.assessor._calculate_impact_score(low_impact_disruption)
        assert score < 0.5  # Should be low impact
    
    def test_affected_routes_identification(self):
        """Test identification of affected trade routes"""
        disruption = {
            "source_data": {
                "location": "suez canal"
            }
        }
        
        routes = self.assessor._identify_affected_routes(disruption)
        assert "suez_canal" in routes
    
    def test_mitigation_strategies_generation(self):
        """Test mitigation strategies generation"""
        high_impact_disruption = {
            "disruption_type": "weather_event",
            "urgency_level": "immediate"
        }
        
        strategies = self.assessor._generate_mitigation_strategies(high_impact_disruption, 0.8)
        assert len(strategies) > 0
        assert any("emergency" in strategy.lower() for strategy in strategies)

class TestDataServices:
    def test_weather_service_initialization(self):
        """Test weather service initialization"""
        service = WeatherService()
        assert service is not None
        assert hasattr(service, 'key_locations')
        assert len(service.key_locations) > 0
    
    def test_news_service_initialization(self):
        """Test news service initialization"""
        service = NewsService()
        assert service is not None
        assert hasattr(service, 'supply_chain_keywords')
        assert len(service.supply_chain_keywords) > 0
    
    def test_earthquake_service_initialization(self):
        """Test earthquake service initialization"""
        service = EarthquakeService()
        assert service is not None
        assert hasattr(service, 'supply_chain_regions')
        assert len(service.supply_chain_regions) > 0

class TestIntegration:
    def test_end_to_end_disruption_processing(self):
        """Test end-to-end disruption processing"""
        detector = DisruptionDetector()
        assessor = ImpactAssessor()
        
        # Sample data batch
        data_batch = [
            {
                "source": "earthquake",
                "event_type": "earthquake",
                "title": "Magnitude 6.2 Earthquake",
                "description": "Earthquake detected near major shipping port",
                "severity": "warning",
                "location": "Los Angeles Port",
                "latitude": 33.7361,
                "longitude": -118.2639,
                "magnitude": 6.2,
                "confidence_score": 0.85
            }
        ]
        
        # Detect disruptions
        disruptions = detector.detect_disruptions(data_batch)
        assert len(disruptions) > 0
        
        # Assess impact
        disruption = disruptions[0]
        impact_assessment = assessor.assess_impact(disruption)
        
        assert "impact_score" in impact_assessment
        assert "severity_level" in impact_assessment
        assert "financial_impact" in impact_assessment
        assert "mitigation_strategies" in impact_assessment
        
        # Verify impact score is reasonable
        assert 0 <= impact_assessment["impact_score"] <= 1
        
        # Verify mitigation strategies are provided
        assert len(impact_assessment["mitigation_strategies"]) > 0

if __name__ == "__main__":
    pytest.main([__file__]) 