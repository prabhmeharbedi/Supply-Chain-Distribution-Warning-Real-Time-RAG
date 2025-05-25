"""
AI-Powered Analysis Service for Supply Chain Intelligence
"""

import openai
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from src.utils.logger import setup_logger
from src.core.rag.vector_store import vector_store
from config.settings import settings

logger = setup_logger(__name__)

class AIAnalysisService:
    def __init__(self):
        self.openai_client = None
        
        # Initialize OpenAI if API key is available
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
            logger.info("AI Analysis Service initialized with OpenAI")
        else:
            logger.warning("OpenAI API key not found. AI analysis will be limited.")
    
    async def generate_supply_chain_report(self, disruptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive supply chain analysis report"""
        try:
            if not disruptions:
                return self._generate_empty_report()
            
            # Analyze disruptions
            analysis = await self._analyze_disruption_patterns(disruptions)
            
            # Generate insights
            insights = await self._generate_insights(disruptions, analysis)
            
            # Create recommendations
            recommendations = await self._generate_recommendations(disruptions, analysis)
            
            # Risk assessment
            risk_assessment = await self._assess_overall_risk(disruptions)
            
            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_disruptions": len(disruptions),
                    "high_risk_events": len([d for d in disruptions if d.get('disruption_score', 0) > 0.7]),
                    "affected_regions": list(set([d.get('geographic_scope', 'unknown') for d in disruptions])),
                    "primary_sectors": analysis.get('primary_sectors', [])
                },
                "risk_assessment": risk_assessment,
                "pattern_analysis": analysis,
                "ai_insights": insights,
                "recommendations": recommendations,
                "disruption_details": disruptions
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating supply chain report: {e}")
            return self._generate_error_report(str(e))
    
    async def _analyze_disruption_patterns(self, disruptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in disruption data"""
        analysis = {
            "primary_sectors": [],
            "geographic_clusters": {},
            "disruption_types": {},
            "severity_distribution": {},
            "temporal_patterns": {}
        }
        
        try:
            # Analyze sectors
            sector_counts = {}
            for disruption in disruptions:
                sectors = disruption.get('affected_sectors', [])
                for sector in sectors:
                    sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            analysis["primary_sectors"] = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Analyze geographic distribution
            geo_counts = {}
            for disruption in disruptions:
                geo = disruption.get('geographic_scope', 'unknown')
                geo_counts[geo] = geo_counts.get(geo, 0) + 1
            
            analysis["geographic_clusters"] = geo_counts
            
            # Analyze disruption types
            type_counts = {}
            for disruption in disruptions:
                dtype = disruption.get('disruption_type', 'unknown')
                type_counts[dtype] = type_counts.get(dtype, 0) + 1
            
            analysis["disruption_types"] = type_counts
            
            # Severity distribution
            severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            for disruption in disruptions:
                score = disruption.get('disruption_score', 0)
                if score >= 0.8:
                    severity_counts["critical"] += 1
                elif score >= 0.6:
                    severity_counts["high"] += 1
                elif score >= 0.4:
                    severity_counts["medium"] += 1
                else:
                    severity_counts["low"] += 1
            
            analysis["severity_distribution"] = severity_counts
            
        except Exception as e:
            logger.error(f"Error analyzing disruption patterns: {e}")
        
        return analysis
    
    async def _generate_insights(self, disruptions: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights"""
        insights = []
        
        if not self.openai_client:
            return self._generate_basic_insights(disruptions, analysis)
        
        try:
            # Prepare context for AI
            context = {
                "total_disruptions": len(disruptions),
                "primary_sectors": analysis.get("primary_sectors", []),
                "geographic_distribution": analysis.get("geographic_clusters", {}),
                "disruption_types": analysis.get("disruption_types", {}),
                "severity_distribution": analysis.get("severity_distribution", {})
            }
            
            prompt = f"""
            As a supply chain expert, analyze this disruption data and provide 5-7 key insights:
            
            DISRUPTION SUMMARY:
            - Total Events: {context['total_disruptions']}
            - Primary Affected Sectors: {context['primary_sectors']}
            - Geographic Distribution: {context['geographic_distribution']}
            - Disruption Types: {context['disruption_types']}
            - Severity Distribution: {context['severity_distribution']}
            
            Provide insights in this format:
            1. [Insight about sector vulnerabilities]
            2. [Insight about geographic patterns]
            3. [Insight about disruption types]
            4. [Insight about severity trends]
            5. [Insight about potential cascading effects]
            6. [Insight about recovery implications]
            7. [Insight about strategic recommendations]
            
            Focus on actionable intelligence for supply chain managers.
            """
            
            response = await self._call_openai(prompt, max_tokens=400)
            
            # Parse insights from response
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and clean up
                    insight = line.split('.', 1)[-1].strip()
                    if insight:
                        insights.append(insight)
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            insights = self._generate_basic_insights(disruptions, analysis)
        
        return insights[:7]  # Limit to 7 insights
    
    async def _generate_recommendations(self, disruptions: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        if not self.openai_client:
            return self._generate_basic_recommendations(disruptions, analysis)
        
        try:
            # Get top disruptions for context
            top_disruptions = sorted(disruptions, key=lambda x: x.get('disruption_score', 0), reverse=True)[:3]
            
            disruption_summaries = []
            for d in top_disruptions:
                source = d.get('source_data', {})
                ai_analysis = d.get('ai_analysis', {})
                summary = f"Event: {source.get('title', 'Unknown')} | Location: {source.get('location', 'Unknown')} | Type: {ai_analysis.get('disruption_type', 'unknown')} | Severity: {ai_analysis.get('impact_severity', 'unknown')}"
                disruption_summaries.append(summary)
            
            prompt = f"""
            As a supply chain risk management expert, provide specific actionable recommendations based on these disruptions:
            
            TOP DISRUPTIONS:
            {chr(10).join(disruption_summaries)}
            
            ANALYSIS SUMMARY:
            - Primary Sectors: {[s[0] for s in analysis.get('primary_sectors', [])[:3]]}
            - Geographic Hotspots: {list(analysis.get('geographic_clusters', {}).keys())[:3]}
            - Main Disruption Types: {list(analysis.get('disruption_types', {}).keys())[:3]}
            
            Provide 5-6 specific recommendations in JSON format:
            [
                {{
                    "priority": "high|medium|low",
                    "category": "immediate|short_term|long_term",
                    "title": "Brief recommendation title",
                    "description": "Detailed actionable recommendation",
                    "estimated_impact": "Expected positive impact",
                    "implementation_time": "Time to implement"
                }}
            ]
            """
            
            response = await self._call_openai(prompt, max_tokens=600)
            
            try:
                recommendations = json.loads(response)
                if not isinstance(recommendations, list):
                    recommendations = []
            except json.JSONDecodeError:
                logger.error("Failed to parse AI recommendations as JSON")
                recommendations = self._generate_basic_recommendations(disruptions, analysis)
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            recommendations = self._generate_basic_recommendations(disruptions, analysis)
        
        return recommendations
    
    async def _assess_overall_risk(self, disruptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall supply chain risk level"""
        if not disruptions:
            return {
                "level": "low",
                "score": 0.1,
                "factors": [],
                "outlook": "stable"
            }
        
        # Calculate risk factors
        avg_score = sum(d.get('disruption_score', 0) for d in disruptions) / len(disruptions)
        high_risk_count = len([d for d in disruptions if d.get('disruption_score', 0) > 0.7])
        critical_locations = len([d for d in disruptions if 'global' in d.get('geographic_scope', '')])
        
        # Determine risk level
        risk_score = (avg_score * 0.4) + (high_risk_count / len(disruptions) * 0.4) + (critical_locations / len(disruptions) * 0.2)
        
        if risk_score >= 0.8:
            level = "critical"
            outlook = "deteriorating"
        elif risk_score >= 0.6:
            level = "high"
            outlook = "concerning"
        elif risk_score >= 0.4:
            level = "medium"
            outlook = "monitoring"
        else:
            level = "low"
            outlook = "stable"
        
        factors = []
        if high_risk_count > 0:
            factors.append(f"{high_risk_count} high-severity disruptions detected")
        if critical_locations > 0:
            factors.append(f"{critical_locations} events affecting critical global infrastructure")
        if avg_score > 0.6:
            factors.append("Above-average disruption severity across events")
        
        return {
            "level": level,
            "score": round(risk_score, 2),
            "factors": factors,
            "outlook": outlook
        }
    
    async def get_event_prediction(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI prediction for a specific event"""
        try:
            # Get relevant context from vector store
            context = vector_store.get_context_for_event(event)
            
            # Get similar historical events
            historical_events = vector_store.get_similar_historical_events(event)
            
            if not self.openai_client:
                return self._generate_basic_prediction(event, context, historical_events)
            
            prompt = f"""
            Predict the supply chain impact of this event:
            
            EVENT:
            Title: {event.get('title', '')}
            Description: {event.get('description', '')}
            Location: {event.get('location', '')}
            Type: {event.get('event_type', '')}
            
            RELEVANT CONTEXT:
            {json.dumps(context, indent=2)}
            
            SIMILAR HISTORICAL EVENTS:
            {json.dumps([h['metadata'] for h in historical_events], indent=2)}
            
            Provide prediction in JSON format:
            {{
                "impact_timeline": {{
                    "immediate_hours": "0-24 hour impact description",
                    "short_term_days": "1-7 day impact description", 
                    "medium_term_weeks": "1-4 week impact description",
                    "long_term_months": "1-6 month impact description"
                }},
                "affected_supply_chains": ["list of specific supply chains"],
                "mitigation_strategies": ["list of specific mitigation actions"],
                "recovery_estimate": "estimated recovery time",
                "confidence_level": 0.0-1.0
            }}
            """
            
            response = await self._call_openai(prompt, max_tokens=500)
            
            try:
                prediction = json.loads(response)
                return prediction
            except json.JSONDecodeError:
                logger.error("Failed to parse AI prediction as JSON")
                return self._generate_basic_prediction(event, context, historical_events)
            
        except Exception as e:
            logger.error(f"Error generating event prediction: {e}")
            return self._generate_basic_prediction(event, {}, [])
    
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
    
    def _generate_basic_insights(self, disruptions: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
        """Generate basic insights without AI"""
        insights = []
        
        if analysis.get("primary_sectors"):
            top_sector = analysis["primary_sectors"][0][0]
            insights.append(f"The {top_sector} sector shows highest vulnerability with multiple disruption events")
        
        if analysis.get("geographic_clusters"):
            top_region = max(analysis["geographic_clusters"].items(), key=lambda x: x[1])[0]
            insights.append(f"Geographic concentration of disruptions in {top_region} regions")
        
        severity = analysis.get("severity_distribution", {})
        if severity.get("critical", 0) > 0:
            insights.append(f"{severity['critical']} critical-level disruptions require immediate attention")
        
        return insights
    
    def _generate_basic_recommendations(self, disruptions: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic recommendations without AI"""
        recommendations = [
            {
                "priority": "high",
                "category": "immediate",
                "title": "Monitor High-Risk Events",
                "description": "Closely monitor all disruptions with scores above 0.7",
                "estimated_impact": "Reduced response time to critical events",
                "implementation_time": "Immediate"
            },
            {
                "priority": "medium",
                "category": "short_term",
                "title": "Diversify Supply Sources",
                "description": "Identify alternative suppliers in less affected regions",
                "estimated_impact": "Improved supply chain resilience",
                "implementation_time": "2-4 weeks"
            }
        ]
        
        return recommendations
    
    def _generate_basic_prediction(self, event: Dict[str, Any], context: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic prediction without AI"""
        return {
            "impact_timeline": {
                "immediate_hours": "Initial assessment and monitoring",
                "short_term_days": "Potential supply delays in affected region",
                "medium_term_weeks": "Possible alternative sourcing required",
                "long_term_months": "Recovery and normalization of operations"
            },
            "affected_supply_chains": ["regional logistics", "local manufacturing"],
            "mitigation_strategies": ["Monitor situation", "Activate contingency plans"],
            "recovery_estimate": "7-14 days",
            "confidence_level": 0.6
        }
    
    def _generate_empty_report(self) -> Dict[str, Any]:
        """Generate report when no disruptions are found"""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_disruptions": 0,
                "high_risk_events": 0,
                "affected_regions": [],
                "primary_sectors": []
            },
            "risk_assessment": {
                "level": "low",
                "score": 0.1,
                "factors": [],
                "outlook": "stable"
            },
            "ai_insights": ["No significant supply chain disruptions detected in current monitoring period"],
            "recommendations": [
                {
                    "priority": "low",
                    "category": "long_term",
                    "title": "Maintain Monitoring",
                    "description": "Continue monitoring for emerging supply chain risks",
                    "estimated_impact": "Early detection of future disruptions",
                    "implementation_time": "Ongoing"
                }
            ],
            "disruption_details": []
        }
    
    def _generate_error_report(self, error: str) -> Dict[str, Any]:
        """Generate error report"""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "error": f"Failed to generate report: {error}",
            "summary": {
                "total_disruptions": 0,
                "high_risk_events": 0,
                "affected_regions": [],
                "primary_sectors": []
            },
            "risk_assessment": {
                "level": "unknown",
                "score": 0.0,
                "factors": ["Analysis error occurred"],
                "outlook": "unknown"
            }
        } 