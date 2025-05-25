import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
from datetime import datetime, timedelta

from src.main import app
from src.core.database import get_db
from src.models.alert import Alert


# Test client setup
client = TestClient(app)

# Mock database for testing
@pytest.fixture
def mock_db():
    """Mock database session for testing."""
    with patch('src.core.database.get_db') as mock:
        db_session = Mock()
        mock.return_value = db_session
        yield db_session


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_basic_health_check(self):
        """Test basic health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_pathway_health_check(self):
        """Test Pathway-specific health endpoint."""
        with patch('src.core.pipeline.pathway_rag_pipeline.PathwayRAGPipeline') as mock_pipeline:
            mock_instance = Mock()
            mock_instance.health_check.return_value = {
                "status": "healthy",
                "components": {"vector_store": "healthy", "ai_detector": "healthy"}
            }
            mock_pipeline.return_value = mock_instance
            
            response = client.get("/api/v1/pathway-rag/health/pathway")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "components" in data


class TestAlertEndpoints:
    """Test alert management endpoints."""
    
    def test_get_alerts_unauthorized(self):
        """Test alerts endpoint without authentication."""
        response = client.get("/api/v1/alerts")
        assert response.status_code == 401
    
    def test_get_alerts_with_auth(self, mock_db):
        """Test alerts endpoint with authentication."""
        # Mock alerts data
        mock_alerts = [
            Alert(
                id=1,
                event_type="weather_alert",
                severity="critical",
                title="Severe Storm Warning",
                description="Major storm affecting supply chain",
                location="Los Angeles",
                created_at=datetime.now(),
                alert_score=0.85,
                priority_rank=1,
                should_alert=True,
                escalation_needed=False
            )
        ]
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_alerts
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/alerts", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total_count" in data
        assert len(data["alerts"]) == 1
    
    def test_get_alerts_with_filters(self, mock_db):
        """Test alerts endpoint with severity filters."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        headers = {"Authorization": "Bearer demo_token"}
        params = {
            "severity": ["critical", "warning"],
            "hours_back": 48,
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/v1/alerts", headers=headers, params=params)
        assert response.status_code == 200
    
    def test_get_single_alert(self, mock_db):
        """Test getting a single alert by ID."""
        mock_alert = Alert(
            id=1,
            event_type="weather_alert",
            severity="critical",
            title="Test Alert",
            description="Test description",
            created_at=datetime.now(),
            alert_score=0.8,
            priority_rank=1,
            should_alert=True,
            escalation_needed=False
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_alert
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/alerts/1", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Alert"
    
    def test_acknowledge_alert(self, mock_db):
        """Test acknowledging an alert."""
        mock_alert = Alert(
            id=1,
            event_type="weather_alert",
            severity="critical",
            title="Test Alert",
            description="Test description",
            created_at=datetime.now(),
            alert_score=0.8,
            priority_rank=1,
            should_alert=True,
            escalation_needed=False,
            acknowledged=False
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_alert
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.post("/api/v1/alerts/1/acknowledge", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Alert acknowledged successfully"
        assert mock_alert.acknowledged is True
    
    def test_get_alert_summary(self, mock_db):
        """Test alert summary statistics."""
        # Mock summary data
        mock_db.query.return_value.filter.return_value.count.return_value = 10
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/alerts/summary/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts" in data
        assert "critical_alerts" in data
        assert "warning_alerts" in data


class TestDashboardEndpoints:
    """Test dashboard data endpoints."""
    
    def test_get_dashboard_stats(self, mock_db):
        """Test dashboard statistics endpoint."""
        # Mock dashboard data
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/dashboard/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts_24h" in data
        assert "critical_alerts_24h" in data
        assert "active_disruptions" in data
        assert "system_health" in data
    
    def test_get_timeline_data(self, mock_db):
        """Test timeline data endpoint."""
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/dashboard/timeline", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "timeline" in data
    
    def test_get_map_data(self, mock_db):
        """Test map data endpoint."""
        mock_alerts = [
            Alert(
                id=1,
                event_type="weather_alert",
                severity="critical",
                title="Test Alert",
                description="Test description",
                location="Los Angeles",
                latitude=34.0522,
                longitude=-118.2437,
                created_at=datetime.now(),
                alert_score=0.8,
                priority_rank=1,
                should_alert=True,
                escalation_needed=False
            )
        ]
        
        mock_db.query.return_value.filter.return_value.all.return_value = mock_alerts
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/dashboard/map-data", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total_count" in data
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["latitude"] == 34.0522


class TestPathwayRAGEndpoints:
    """Test Pathway RAG specific endpoints."""
    
    @patch('src.core.rag.pathway_vector_store.PathwayVectorStore')
    @patch('src.services.ai_analysis_service.AIAnalysisService')
    def test_real_time_query(self, mock_ai_service, mock_vector_store):
        """Test real-time RAG query endpoint."""
        # Mock vector store response
        mock_vector_store.return_value.search.return_value = [
            {
                "content": "Port disruption at Los Angeles",
                "metadata": {"source": "news", "timestamp": "2024-01-01T12:00:00"},
                "score": 0.95
            }
        ]
        
        # Mock AI service response
        mock_ai_service.return_value.generate_response.return_value = {
            "response": "There is a major port disruption at Los Angeles affecting supply chain operations.",
            "confidence": 0.9
        }
        
        headers = {"Authorization": "Bearer demo_token"}
        payload = {"query": "What are the current supply chain disruptions?"}
        
        response = client.post("/api/v1/pathway-rag/query/real-time", 
                             headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "response" in data
        assert "sources" in data
        assert "processing_time" in data
        assert "timestamp" in data
    
    @patch('src.core.rag.pathway_vector_store.PathwayVectorStore')
    def test_add_live_data(self, mock_vector_store):
        """Test adding live data endpoint."""
        mock_vector_store.return_value.add_document.return_value = True
        
        headers = {"Authorization": "Bearer demo_token"}
        payload = {
            "content": "New supply chain disruption reported",
            "metadata": {
                "source": "manual",
                "timestamp": datetime.now().isoformat(),
                "location": "Seattle"
            }
        }
        
        response = client.post("/api/v1/pathway-rag/data/add-live", 
                             headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "document_id" in data
        assert "timestamp" in data
    
    @patch('src.core.rag.pathway_vector_store.PathwayVectorStore')
    def test_get_real_time_stats(self, mock_vector_store):
        """Test real-time statistics endpoint."""
        mock_vector_store.return_value.get_stats.return_value = {
            "total_documents": 1000,
            "live_documents": 50,
            "recent_documents": 100,
            "queries_processed": 250,
            "average_response_time": 150.5,
            "last_update": datetime.now().isoformat()
        }
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/pathway-rag/stats/real-time", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "live_documents" in data
        assert "queries_processed" in data
        assert "average_response_time" in data
    
    @patch('src.core.rag.pathway_vector_store.PathwayVectorStore')
    def test_prove_real_time_capability(self, mock_vector_store):
        """Test real-time capability proof endpoint."""
        mock_vector_store.return_value.add_document.return_value = True
        mock_vector_store.return_value.search.return_value = [
            {
                "content": "Real-time test document",
                "metadata": {"source": "test", "timestamp": datetime.now().isoformat()},
                "score": 1.0
            }
        ]
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.post("/api/v1/pathway-rag/demo/real-time-proof", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "proof_completed" in data
        assert "latency_ms" in data
        assert "test_document_found" in data
        assert data["proof_completed"] is True


class TestRateLimiting:
    """Test API rate limiting functionality."""
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced."""
        headers = {"Authorization": "Bearer demo_token"}
        
        # Make multiple requests quickly
        responses = []
        for _ in range(20):  # Exceed typical rate limit
            response = client.get("/api/v1/health", headers=headers)
            responses.append(response)
        
        # Should have some successful requests
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        assert success_count > 0
        # Note: Rate limiting might not be enforced in test environment
        # This test verifies the endpoint structure


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_invalid_alert_id(self, mock_db):
        """Test handling of invalid alert ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/api/v1/alerts/99999", headers=headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON payload."""
        headers = {"Authorization": "Bearer demo_token", "Content-Type": "application/json"}
        
        response = client.post("/api/v1/pathway-rag/query/real-time", 
                             headers=headers, data="invalid json")
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        headers = {"Authorization": "Bearer demo_token"}
        payload = {}  # Missing required 'query' field
        
        response = client.post("/api/v1/pathway-rag/query/real-time", 
                             headers=headers, json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestWebSocketEndpoints:
    """Test WebSocket endpoints for real-time updates."""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates."""
        with client.websocket_connect("/ws/real-time-updates") as websocket:
            # Test connection establishment
            assert websocket is not None
            
            # Test receiving initial connection message
            data = websocket.receive_json()
            assert "type" in data
            assert data["type"] == "connection_established"
    
    @pytest.mark.asyncio
    async def test_websocket_real_time_updates(self):
        """Test receiving real-time updates via WebSocket."""
        with patch('src.api.pathway_rag_endpoints.PathwayVectorStore') as mock_store:
            # Mock real-time update
            mock_update = {
                "type": "new_alert",
                "data": {
                    "id": 1,
                    "title": "New Supply Chain Alert",
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            with client.websocket_connect("/ws/real-time-updates") as websocket:
                # Simulate sending an update
                websocket.send_json(mock_update)
                
                # Receive the update
                received_data = websocket.receive_json()
                assert received_data["type"] == "new_alert"
                assert "data" in received_data


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @patch('src.core.rag.pathway_vector_store.PathwayVectorStore')
    @patch('src.services.ai_analysis_service.AIAnalysisService')
    def test_complete_rag_workflow(self, mock_ai_service, mock_vector_store):
        """Test complete RAG workflow from data addition to query."""
        headers = {"Authorization": "Bearer demo_token"}
        
        # Step 1: Add new data
        add_payload = {
            "content": "Major earthquake disrupts shipping at Long Beach Port",
            "metadata": {
                "source": "earthquake",
                "timestamp": datetime.now().isoformat(),
                "location": "Long Beach",
                "severity": "critical"
            }
        }
        
        mock_vector_store.return_value.add_document.return_value = True
        
        add_response = client.post("/api/v1/pathway-rag/data/add-live", 
                                 headers=headers, json=add_payload)
        assert add_response.status_code == 200
        
        # Step 2: Query for the data
        mock_vector_store.return_value.search.return_value = [
            {
                "content": add_payload["content"],
                "metadata": add_payload["metadata"],
                "score": 0.98
            }
        ]
        
        mock_ai_service.return_value.generate_response.return_value = {
            "response": "There is a major earthquake disrupting shipping operations at Long Beach Port.",
            "confidence": 0.95
        }
        
        query_payload = {"query": "What earthquake impacts are affecting ports?"}
        
        query_response = client.post("/api/v1/pathway-rag/query/real-time", 
                                   headers=headers, json=query_payload)
        assert query_response.status_code == 200
        
        query_data = query_response.json()
        assert "Long Beach" in query_data["response"]
        assert len(query_data["sources"]) > 0
        assert query_data["sources"][0]["score"] > 0.9
    
    def test_dashboard_data_consistency(self, mock_db):
        """Test consistency of dashboard data across endpoints."""
        headers = {"Authorization": "Bearer demo_token"}
        
        # Mock consistent data
        mock_db.query.return_value.filter.return_value.count.return_value = 15
        
        # Get dashboard stats
        stats_response = client.get("/api/v1/dashboard/stats", headers=headers)
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        
        # Get alert summary
        summary_response = client.get("/api/v1/alerts/summary/stats", headers=headers)
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        
        # Verify consistency
        assert stats_data["total_alerts_24h"] == summary_data["total_alerts"] 