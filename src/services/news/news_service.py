import requests
from typing import List, Dict, Any
from config.settings import settings
from src.utils.logger import setup_logger
import re

logger = setup_logger(__name__)

class NewsService:
    def __init__(self):
        self.api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
        
        # Supply chain related keywords
        self.supply_chain_keywords = [
            "supply chain disruption",
            "port closure",
            "shipping delay",
            "factory shutdown",
            "trade route",
            "logistics crisis",
            "manufacturing halt",
            "container shortage",
            "freight delay",
            "warehouse closure",
            "transportation strike",
            "border closure",
            "customs delay",
            "semiconductor shortage",
            "raw material shortage"
        ]
        
        # High impact keywords for severity assessment
        self.high_impact_keywords = [
            "shutdown", "closure", "halt", "suspended", "blocked",
            "strike", "disruption", "crisis", "shortage", "delay"
        ]
        
        # Location keywords for major trade hubs
        self.trade_hub_keywords = [
            "suez canal", "panama canal", "strait of hormuz",
            "los angeles", "long beach", "new york", "charleston",
            "shanghai", "shenzhen", "singapore", "rotterdam",
            "hamburg", "antwerp", "felixstowe", "dubai"
        ]
        
    def get_supply_chain_news(self) -> List[Dict[str, Any]]:
        """Fetch supply chain related news"""
        articles = []
        
        if not self.api_key:
            logger.warning("News API key not configured")
            return articles
            
        for keyword in self.supply_chain_keywords[:5]:  # Limit to avoid rate limits
            try:
                url = f"{self.base_url}/everything"
                params = {
                    "q": keyword,
                    "apiKey": self.api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "from": "2024-01-01"  # Recent articles only
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for article in data.get("articles", []):
                    if self._is_supply_chain_relevant(article):
                        processed_article = {
                            "source": "news",
                            "event_type": "news_alert",
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "content": article.get("content", ""),
                            "url": article.get("url", ""),
                            "published_at": article.get("publishedAt", ""),
                            "severity": self._analyze_severity(article),
                            "location": self._extract_location(article),
                            "confidence_score": self._calculate_confidence(article),
                            "raw_data": article
                        }
                        articles.append(processed_article)
                        
            except Exception as e:
                logger.error(f"Error fetching news for keyword '{keyword}': {e}")
        
        # Remove duplicates based on URL
        unique_articles = []
        seen_urls = set()
        for article in articles:
            url = article.get("url", "")
            if url not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(url)
        
        logger.info(f"Fetched {len(unique_articles)} unique supply chain news articles")
        return unique_articles
    
    def _is_supply_chain_relevant(self, article: Dict[str, Any]) -> bool:
        """Check if article is relevant to supply chain disruptions"""
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Must contain supply chain related terms
        supply_chain_terms = [
            "supply chain", "logistics", "shipping", "freight", "cargo",
            "port", "warehouse", "manufacturing", "factory", "trade",
            "import", "export", "customs", "border", "transportation"
        ]
        
        return any(term in text for term in supply_chain_terms)
    
    def _analyze_severity(self, article: Dict[str, Any]) -> str:
        """Analyze article content to determine severity level"""
        text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".lower()
        
        # Count high impact keywords
        high_impact_count = sum(1 for keyword in self.high_impact_keywords if keyword in text)
        
        # Check for trade hub mentions
        trade_hub_mentioned = any(hub in text for hub in self.trade_hub_keywords)
        
        # Determine severity based on content analysis
        if high_impact_count >= 3 or trade_hub_mentioned:
            return "critical"
        elif high_impact_count >= 2:
            return "warning"
        elif high_impact_count >= 1:
            return "watch"
        else:
            return "info"
    
    def _extract_location(self, article: Dict[str, Any]) -> str:
        """Extract location information from article"""
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Look for trade hub mentions
        for hub in self.trade_hub_keywords:
            if hub in text:
                return hub.title()
        
        # Look for country mentions (simplified)
        countries = [
            "china", "united states", "usa", "germany", "japan",
            "singapore", "netherlands", "united kingdom", "uk",
            "south korea", "taiwan", "india", "brazil", "mexico"
        ]
        
        for country in countries:
            if country in text:
                return country.title()
        
        return "Global"
    
    def _calculate_confidence(self, article: Dict[str, Any]) -> float:
        """Calculate confidence score for the article"""
        confidence = 0.5  # Base confidence
        
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Increase confidence for specific terms
        if "confirmed" in text or "official" in text:
            confidence += 0.2
        if "breaking" in text or "urgent" in text:
            confidence += 0.1
        if any(hub in text for hub in self.trade_hub_keywords):
            confidence += 0.15
        
        # Check source reliability (simplified)
        source_name = article.get("source", {}).get("name", "").lower()
        reliable_sources = [
            "reuters", "bloomberg", "wall street journal", "financial times",
            "associated press", "bbc", "cnn", "cnbc"
        ]
        
        if any(reliable in source_name for reliable in reliable_sources):
            confidence += 0.1
        
        return min(1.0, confidence) 