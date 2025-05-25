#!/usr/bin/env python3
"""
Supply Chain Disruption Predictor - Demo Script
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.detectors.disruption_detector import DisruptionDetector
from src.core.processors.impact_assessor import ImpactAssessor
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def demo_disruption_detection():
    """Demonstrate disruption detection capabilities"""
    print_header("SUPPLY CHAIN DISRUPTION PREDICTOR - DEMO")
    
    detector = DisruptionDetector()
    assessor = ImpactAssessor()
    
    # Sample data representing different types of events
    sample_events = [
        {
            "source": "earthquake",
            "event_type": "earthquake",
            "title": "Magnitude 6.8 Earthquake Strikes Japan",
            "description": "Major earthquake hits manufacturing region near Tokyo",
            "severity": "critical",
            "location": "Tokyo, Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "magnitude": 6.8,
            "confidence_score": 0.95
        },
        {
            "source": "news",
            "event_type": "news_alert",
            "title": "Suez Canal Blocked by Container Ship",
            "description": "Major container vessel runs aground in Suez Canal",
            "severity": "critical",
            "location": "Suez Canal, Egypt",
            "latitude": 30.5234,
            "longitude": 32.2569,
            "confidence_score": 0.98
        }
    ]
    
    print(f"Processing {len(sample_events)} sample events...")
    
    # Detect disruptions
    disruptions = detector.detect_disruptions(sample_events)
    
    print(f"✓ Detected {len(disruptions)} potential supply chain disruptions")
    
    # Process each disruption
    for i, disruption in enumerate(disruptions, 1):
        print(f"\n--- Disruption {i}: {disruption['source_data']['title']} ---")
        
        source_data = disruption['source_data']
        print(f"Source: {source_data['source']}")
        print(f"Location: {source_data['location']}")
        print(f"Disruption Score: {disruption['disruption_score']:.3f}")
        print(f"Urgency Level: {disruption['urgency_level']}")
        
        # Assess impact
        impact_assessment = assessor.assess_impact(disruption)
        
        if "error" not in impact_assessment:
            print(f"Impact Score: {impact_assessment['impact_score']:.3f}")
            print(f"Severity Level: {impact_assessment['severity_level']}")
            
            financial = impact_assessment['financial_impact']
            print(f"Daily Impact: ${financial['daily_impact_usd_millions']:.1f}M USD")

def main():
    """Main demo function"""
    try:
        print("🌟 Welcome to the Supply Chain Disruption Predictor Demo!")
        demo_disruption_detection()
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main() 