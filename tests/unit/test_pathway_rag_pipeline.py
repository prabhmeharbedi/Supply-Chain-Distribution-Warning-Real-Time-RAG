import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import numpy as np

from src.core.pipeline.pathway_rag_pipeline import PathwayRAGPipeline
from src.core.rag.pathway_vector_store import PathwayVectorStore


class TestPathwayRAGPipeline:
    """Test suite for Pathway RAG Pipeline functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.pipeline = PathwayRAGPipeline()
        self.sample_data = {
            "content": "Major supply chain disruption at Los Angeles Port",
            "metadata": {
                "source": "news",
                "timestamp": datetime.now().isoformat(),
                "location": "Los Angeles",
                "severity": "critical"
            }
        }
    
    def test_pipeline_initialization(self):
        """Test that pipeline initializes correctly."""
        assert self.pipeline is not None
        assert hasattr(self.pipeline, 'vector_store')
        assert hasattr(self.pipeline, 'ai_detector')
        assert hasattr(self.pipeline, 'ai_analyzer')
    
    @patch('src.core.pipeline.pathway_rag_pipeline.pathway')
    def test_create_data_streams(self, mock_pathway):
        """Test creation of data input streams."""
        mock_pathway.io.fs.read.return_value = Mock()
        
        streams = self.pipeline._create_data_streams()
        
        assert 'weather' in streams
        assert 'news' in streams
        assert 'earthquakes' in streams
        assert 'manual_updates' in streams
        
        # Verify pathway.io.fs.read was called for each stream
        assert mock_pathway.io.fs.read.call_count >= 4
    
    def test_process_document_valid_data(self):
        """Test document processing with valid data."""
        result = self.pipeline._process_document(self.sample_data)
        
        assert result is not None
        assert 'content' in result
        assert 'metadata' in result
        assert 'embedding' in result
        assert 'relevance_score' in result
        assert 'confidence_score' in result
        assert 'disruption_score' in result
        
        # Check that scores are within valid ranges
        assert 0 <= result['relevance_score'] <= 1
        assert 0 <= result['confidence_score'] <= 1
        assert 0 <= result['disruption_score'] <= 1
    
    def test_process_document_empty_data(self):
        """Test document processing with empty data."""
        empty_data = {}
        result = self.pipeline._process_document(empty_data)
        
        # Should handle empty data gracefully
        assert result is not None
        assert result['relevance_score'] < 0.5
        assert result['confidence_score'] < 0.5
    
    def test_process_document_missing_content(self):
        """Test document processing with missing content."""
        invalid_data = {"metadata": {"source": "test"}}
        result = self.pipeline._process_document(invalid_data)
        
        # Should handle missing content
        assert result is not None
        assert result['content'] == ""
        assert result['relevance_score'] < 0.3
    
    @patch('src.core.pipeline.pathway_rag_pipeline.SentenceTransformer')
    def test_create_embedding(self, mock_transformer):
        """Test embedding creation."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        mock_transformer.return_value = mock_model
        
        # Reinitialize pipeline to use mocked transformer
        pipeline = PathwayRAGPipeline()
        
        embedding = pipeline._create_embedding("test content")
        
        assert embedding is not None
        assert len(embedding) == 3
        assert isinstance(embedding, np.ndarray)
        mock_model.encode.assert_called_once_with("test content")
    
    def test_assess_relevance_high_relevance(self):
        """Test relevance assessment for highly relevant content."""
        relevant_data = {
            "content": "Port shutdown affects supply chain operations",
            "metadata": {
                "source": "news",
                "location": "Los Angeles Port"
            }
        }
        
        relevance = self.pipeline._assess_relevance(relevant_data)
        assert relevance > 0.7
    
    def test_assess_relevance_low_relevance(self):
        """Test relevance assessment for low relevance content."""
        irrelevant_data = {
            "content": "Celebrity gossip and entertainment news",
            "metadata": {
                "source": "news",
                "location": "Hollywood"
            }
        }
        
        relevance = self.pipeline._assess_relevance(irrelevant_data)
        assert relevance < 0.3
    
    def test_calculate_disruption_score_critical(self):
        """Test disruption score calculation for critical events."""
        critical_data = {
            "content": "Major earthquake disrupts shipping routes",
            "metadata": {
                "source": "earthquake",
                "severity": "critical",
                "location": "Los Angeles"
            },
            "relevance_score": 0.9,
            "confidence_score": 0.8
        }
        
        score = self.pipeline._calculate_disruption_score(critical_data)
        assert score > 0.7
    
    def test_calculate_disruption_score_low_impact(self):
        """Test disruption score calculation for low impact events."""
        low_impact_data = {
            "content": "Minor weather update",
            "metadata": {
                "source": "weather",
                "severity": "info",
                "location": "Small Town"
            },
            "relevance_score": 0.3,
            "confidence_score": 0.4
        }
        
        score = self.pipeline._calculate_disruption_score(low_impact_data)
        assert score < 0.5
    
    def test_should_generate_alert_true(self):
        """Test alert generation decision for high-impact events."""
        high_impact_data = {
            "disruption_score": 0.8,
            "confidence_score": 0.7,
            "metadata": {
                "severity": "critical",
                "source": "earthquake"
            }
        }
        
        should_alert = self.pipeline._should_generate_alert(high_impact_data)
        assert should_alert is True
    
    def test_should_generate_alert_false(self):
        """Test alert generation decision for low-impact events."""
        low_impact_data = {
            "disruption_score": 0.3,
            "confidence_score": 0.4,
            "metadata": {
                "severity": "info",
                "source": "news"
            }
        }
        
        should_alert = self.pipeline._should_generate_alert(low_impact_data)
        assert should_alert is False
    
    @patch('src.core.pipeline.pathway_rag_pipeline.pathway')
    def test_create_output_streams(self, mock_pathway):
        """Test creation of output streams."""
        mock_pathway.io.fs.write.return_value = Mock()
        
        # Mock processed data
        processed_data = Mock()
        
        self.pipeline._create_output_streams(processed_data)
        
        # Verify output streams are created
        assert mock_pathway.io.fs.write.call_count >= 4  # alerts, events, vector_updates, rag_responses
    
    def test_get_source_weight(self):
        """Test source weight calculation."""
        assert self.pipeline._get_source_weight("earthquake") > 0.9
        assert self.pipeline._get_source_weight("weather") > 0.8
        assert self.pipeline._get_source_weight("news") < 0.8
        assert self.pipeline._get_source_weight("unknown") == 0.5
    
    def test_get_severity_weight(self):
        """Test severity weight calculation."""
        assert self.pipeline._get_severity_weight("critical") > 0.9
        assert self.pipeline._get_severity_weight("warning") > 0.7
        assert self.pipeline._get_severity_weight("info") < 0.5
        assert self.pipeline._get_severity_weight("unknown") == 0.5
    
    def test_get_location_weight(self):
        """Test location weight calculation."""
        major_hubs = ["Los Angeles", "Long Beach", "New York", "Seattle"]
        
        for hub in major_hubs:
            weight = self.pipeline._get_location_weight(hub)
            assert weight == 1.0
        
        # Test minor location
        minor_weight = self.pipeline._get_location_weight("Small Town")
        assert minor_weight < 1.0
    
    @patch('src.core.pipeline.pathway_rag_pipeline.pathway.run')
    def test_run_pipeline(self, mock_run):
        """Test pipeline execution."""
        self.pipeline.run()
        mock_run.assert_called_once()
    
    def test_pipeline_configuration(self):
        """Test pipeline configuration settings."""
        config = self.pipeline.get_configuration()
        
        assert 'embedding_model' in config
        assert 'vector_store_config' in config
        assert 'processing_config' in config
        assert 'output_config' in config
    
    def test_pipeline_health_check(self):
        """Test pipeline health check."""
        health = self.pipeline.health_check()
        
        assert 'status' in health
        assert 'components' in health
        assert 'last_processed' in health
        assert 'processing_rate' in health


class TestPathwayRAGPipelineIntegration:
    """Integration tests for Pathway RAG Pipeline."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.pipeline = PathwayRAGPipeline()
    
    @pytest.mark.integration
    def test_end_to_end_processing(self):
        """Test complete data flow from input to output."""
        # This would require actual Pathway runtime
        # For now, test the processing logic
        
        sample_documents = [
            {
                "content": "Major port disruption at Los Angeles",
                "metadata": {
                    "source": "news",
                    "timestamp": datetime.now().isoformat(),
                    "location": "Los Angeles",
                    "severity": "critical"
                }
            },
            {
                "content": "Weather update: Clear skies",
                "metadata": {
                    "source": "weather",
                    "timestamp": datetime.now().isoformat(),
                    "location": "San Francisco",
                    "severity": "info"
                }
            }
        ]
        
        results = []
        for doc in sample_documents:
            result = self.pipeline._process_document(doc)
            results.append(result)
        
        # Verify processing results
        assert len(results) == 2
        
        # First document should have high disruption score
        assert results[0]['disruption_score'] > results[1]['disruption_score']
        
        # First document should trigger alert
        assert self.pipeline._should_generate_alert(results[0])
        assert not self.pipeline._should_generate_alert(results[1])
    
    @pytest.mark.performance
    def test_processing_performance(self):
        """Test processing performance with multiple documents."""
        import time
        
        # Generate test documents
        documents = []
        for i in range(100):
            documents.append({
                "content": f"Supply chain event {i}",
                "metadata": {
                    "source": "test",
                    "timestamp": datetime.now().isoformat(),
                    "location": "Test Location",
                    "severity": "info"
                }
            })
        
        start_time = time.time()
        
        results = []
        for doc in documents:
            result = self.pipeline._process_document(doc)
            results.append(result)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertions
        assert len(results) == 100
        assert processing_time < 10.0  # Should process 100 docs in under 10 seconds
        
        avg_time_per_doc = processing_time / 100
        assert avg_time_per_doc < 0.1  # Less than 100ms per document
    
    @pytest.mark.slow
    def test_memory_usage(self):
        """Test memory usage during processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process many documents
        for i in range(1000):
            doc = {
                "content": f"Large content document {i} " * 100,  # Larger content
                "metadata": {
                    "source": "test",
                    "timestamp": datetime.now().isoformat(),
                    "location": "Test Location",
                    "severity": "info"
                }
            }
            self.pipeline._process_document(doc)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024 