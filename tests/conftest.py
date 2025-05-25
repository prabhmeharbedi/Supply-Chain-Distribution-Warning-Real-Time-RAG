import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Generator

# Set test environment
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from src.core.database import Base, engine
from src.models.alert import Alert


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db():
    """Create test database."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_alert():
    """Create a sample alert for testing."""
    return Alert(
        id=1,
        event_type="weather_alert",
        severity="critical",
        title="Severe Storm Warning",
        description="Major storm affecting supply chain operations",
        location="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
        confidence_score=0.85,
        impact_score=0.9,
        created_at=datetime.now(),
        alert_score=0.87,
        priority_rank=1,
        should_alert=True,
        escalation_needed=False,
        acknowledged=False
    )


@pytest.fixture
def sample_alerts():
    """Create multiple sample alerts for testing."""
    return [
        Alert(
            id=1,
            event_type="weather_alert",
            severity="critical",
            title="Severe Storm Warning",
            description="Major storm affecting supply chain",
            location="Los Angeles",
            created_at=datetime.now(),
            alert_score=0.9,
            priority_rank=1,
            should_alert=True,
            escalation_needed=False
        ),
        Alert(
            id=2,
            event_type="earthquake_alert",
            severity="warning",
            title="Earthquake Detected",
            description="Moderate earthquake near shipping routes",
            location="San Francisco",
            created_at=datetime.now(),
            alert_score=0.7,
            priority_rank=2,
            should_alert=True,
            escalation_needed=False
        ),
        Alert(
            id=3,
            event_type="news_alert",
            severity="info",
            title="Port Update",
            description="Regular port operations update",
            location="Seattle",
            created_at=datetime.now(),
            alert_score=0.3,
            priority_rank=3,
            should_alert=False,
            escalation_needed=False
        )
    ]


@pytest.fixture
def mock_pathway_pipeline():
    """Mock Pathway RAG pipeline for testing."""
    with patch('src.core.pipeline.pathway_rag_pipeline.PathwayRAGPipeline') as mock:
        pipeline_instance = Mock()
        pipeline_instance.health_check.return_value = {
            "status": "healthy",
            "components": {
                "vector_store": "healthy",
                "ai_detector": "healthy",
                "ai_analyzer": "healthy"
            },
            "last_processed": datetime.now().isoformat(),
            "processing_rate": 150.5
        }
        pipeline_instance.get_configuration.return_value = {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "vector_store_config": {"dimension": 384},
            "processing_config": {"batch_size": 100},
            "output_config": {"format": "json"}
        }
        mock.return_value = pipeline_instance
        yield pipeline_instance


@pytest.fixture
def mock_vector_store():
    """Mock Pathway vector store for testing."""
    with patch('src.core.rag.pathway_vector_store.PathwayVectorStore') as mock:
        store_instance = Mock()
        store_instance.add_document.return_value = True
        store_instance.search.return_value = [
            {
                "content": "Sample supply chain disruption",
                "metadata": {
                    "source": "news",
                    "timestamp": datetime.now().isoformat(),
                    "location": "Los Angeles"
                },
                "score": 0.95
            }
        ]
        store_instance.get_stats.return_value = {
            "total_documents": 1000,
            "live_documents": 50,
            "recent_documents": 100,
            "queries_processed": 250,
            "average_response_time": 150.5,
            "last_update": datetime.now().isoformat()
        }
        mock.return_value = store_instance
        yield store_instance


@pytest.fixture
def mock_ai_service():
    """Mock AI analysis service for testing."""
    with patch('src.services.ai_analysis_service.AIAnalysisService') as mock:
        service_instance = Mock()
        service_instance.generate_response.return_value = {
            "response": "Based on the current data, there are supply chain disruptions affecting major ports.",
            "confidence": 0.9,
            "sources_used": 3
        }
        service_instance.analyze_disruption.return_value = {
            "disruption_score": 0.8,
            "impact_assessment": "High impact on logistics operations",
            "recommendations": ["Monitor situation closely", "Consider alternative routes"]
        }
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories
        os.makedirs(os.path.join(temp_dir, "weather"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "news"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "earthquakes"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "manual_updates"), exist_ok=True)
        yield temp_dir


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create output subdirectories
        os.makedirs(os.path.join(temp_dir, "alerts"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "events"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "vector_updates"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "rag_responses"), exist_ok=True)
        yield temp_dir


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        {
            "content": "Major port disruption at Los Angeles due to equipment failure",
            "metadata": {
                "source": "news",
                "timestamp": datetime.now().isoformat(),
                "location": "Los Angeles",
                "severity": "critical"
            }
        },
        {
            "content": "Weather alert: Heavy storms expected in shipping lanes",
            "metadata": {
                "source": "weather",
                "timestamp": datetime.now().isoformat(),
                "location": "Pacific Ocean",
                "severity": "warning"
            }
        },
        {
            "content": "Earthquake magnitude 4.2 detected near San Francisco Bay",
            "metadata": {
                "source": "earthquake",
                "timestamp": datetime.now().isoformat(),
                "location": "San Francisco",
                "severity": "warning"
            }
        }
    ]


@pytest.fixture
def auth_headers():
    """Provide authentication headers for API testing."""
    return {"Authorization": "Bearer demo_token"}


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Add slow marker for tests that might take longer
        if "test_memory_usage" in item.name or "test_processing_performance" in item.name:
            item.add_marker(pytest.mark.slow)


# Custom pytest fixtures for specific test scenarios
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing AI functionality."""
    with patch('openai.OpenAI') as mock:
        client_instance = Mock()
        client_instance.chat.completions.create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="This is a test response from the AI service."
                    )
                )
            ]
        )
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer for testing embeddings."""
    with patch('sentence_transformers.SentenceTransformer') as mock:
        transformer_instance = Mock()
        transformer_instance.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock.return_value = transformer_instance
        yield transformer_instance


@pytest.fixture
def mock_faiss_index():
    """Mock FAISS index for testing vector operations."""
    with patch('faiss.IndexFlatIP') as mock:
        index_instance = Mock()
        index_instance.add.return_value = None
        index_instance.search.return_value = ([0.95, 0.85], [[0, 1]])
        index_instance.ntotal = 100
        mock.return_value = index_instance
        yield index_instance


# Performance testing utilities
@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    import time
    import psutil
    import os
    
    class PerformanceMonitor:
        def __init__(self):
            self.process = psutil.Process(os.getpid())
            self.start_time = None
            self.start_memory = None
        
        def start(self):
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss
        
        def stop(self):
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            
            return {
                "execution_time": end_time - self.start_time,
                "memory_used": end_memory - self.start_memory,
                "peak_memory": self.process.memory_info().rss
            }
    
    return PerformanceMonitor()


# Database testing utilities
@pytest.fixture
def clean_database():
    """Ensure clean database state for each test."""
    # This would typically clean up test data
    # For now, we'll use the mock database approach
    yield
    # Cleanup would happen here 