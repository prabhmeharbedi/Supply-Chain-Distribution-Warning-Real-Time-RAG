# Real-Time RAG Testing Framework

This directory contains comprehensive tests for the Real-Time RAG Supply Chain Disruption Predictor system. The testing framework ensures the reliability, performance, and security of the Pathway-powered streaming analytics system.

## 🧪 Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── run_tests.py               # Comprehensive test runner
├── README.md                  # This file
├── unit/                      # Unit tests
│   ├── test_pathway_rag_pipeline.py
│   ├── test_vector_store.py
│   ├── test_ai_services.py
│   └── test_models.py
├── integration/               # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_end_to_end.py
│   └── test_real_time_flow.py
└── performance/               # Performance tests
    ├── test_throughput.py
    ├── test_latency.py
    └── test_memory_usage.py
```

## 🚀 Quick Start

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Suites
```bash
# Unit tests only
python tests/run_tests.py --unit

# Integration tests only
python tests/run_tests.py --integration

# Performance tests only
python tests/run_tests.py --performance

# Quick test suite (unit + integration)
python tests/run_tests.py --quick

# Full CI test suite
python tests/run_tests.py --ci

# All tests and checks
python tests/run_tests.py --all
```

### Run Individual Test Files
```bash
# Run specific test file
pytest tests/unit/test_pathway_rag_pipeline.py -v

# Run specific test class
pytest tests/unit/test_pathway_rag_pipeline.py::TestPathwayRAGPipeline -v

# Run specific test method
pytest tests/unit/test_pathway_rag_pipeline.py::TestPathwayRAGPipeline::test_pipeline_initialization -v
```

## 📋 Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation with mocked dependencies.

**Coverage:**
- ✅ Pathway RAG Pipeline functionality
- ✅ Vector store operations
- ✅ AI service integrations
- ✅ Data models and validation
- ✅ Utility functions
- ✅ Configuration management

**Key Features:**
- Fast execution (< 30 seconds)
- No external dependencies
- High code coverage (>90%)
- Comprehensive edge case testing

### Integration Tests (`tests/integration/`)

Test component interactions and API endpoints with realistic scenarios.

**Coverage:**
- ✅ API endpoint functionality
- ✅ Database operations
- ✅ Real-time data flow
- ✅ Authentication and authorization
- ✅ WebSocket connections
- ✅ End-to-end workflows

**Key Features:**
- Realistic test scenarios
- Mock external services
- API contract validation
- Error handling verification

### Performance Tests (`tests/performance/`)

Validate system performance under various load conditions.

**Coverage:**
- ✅ Query response times
- ✅ Data processing throughput
- ✅ Memory usage patterns
- ✅ Concurrent user handling
- ✅ Real-time latency measurements

**Key Features:**
- Benchmark comparisons
- Resource usage monitoring
- Scalability validation
- Performance regression detection

## 🔧 Test Configuration

### Environment Variables

Tests use the following environment variables:

```bash
TESTING=1                           # Enable test mode
DATABASE_URL=sqlite:///./test.db    # Test database
OPENAI_API_KEY=test_key            # Mock API key
LOG_LEVEL=WARNING                   # Reduce log noise
PATHWAY_PERSISTENCE_MODE=memory     # In-memory processing
```

### Pytest Markers

Tests are organized using pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only performance tests
pytest -m performance

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

### Test Fixtures

Common fixtures available in `conftest.py`:

- `sample_alert` - Single test alert
- `sample_alerts` - Multiple test alerts
- `mock_pathway_pipeline` - Mocked Pathway pipeline
- `mock_vector_store` - Mocked vector store
- `mock_ai_service` - Mocked AI service
- `temp_data_dir` - Temporary data directory
- `auth_headers` - Authentication headers
- `performance_monitor` - Performance monitoring

## 📊 Coverage Reports

### Generate Coverage Reports

```bash
# HTML coverage report
pytest --cov=src --cov-report=html

# Terminal coverage report
pytest --cov=src --cov-report=term-missing

# XML coverage report (for CI)
pytest --cov=src --cov-report=xml
```

### Coverage Targets

- **Unit Tests**: >90% code coverage
- **Integration Tests**: >80% API coverage
- **Overall**: >85% total coverage

## 🔍 Code Quality Checks

### Linting
```bash
# Run all linting checks
python tests/run_tests.py --lint

# Individual tools
flake8 src tests --max-line-length=100
black --check src tests
isort --check-only src tests
```

### Type Checking
```bash
# Run type checking
python tests/run_tests.py --type-check

# Direct mypy
mypy src --ignore-missing-imports
```

### Security Scanning
```bash
# Run security checks
python tests/run_tests.py --security

# Direct bandit
bandit -r src -f json
```

## 🚨 Continuous Integration

### GitHub Actions Workflow

The CI pipeline runs:

1. **Code Quality**
   - Linting (flake8, black, isort)
   - Type checking (mypy)
   - Security scanning (bandit)

2. **Testing**
   - Unit tests with coverage
   - Integration tests
   - Performance benchmarks

3. **Reporting**
   - Coverage reports
   - Test results
   - Performance metrics

### Local CI Simulation

```bash
# Run the same checks as CI
python tests/run_tests.py --ci
```

## 🐛 Debugging Tests

### Verbose Output
```bash
# Detailed test output
pytest -v -s

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

### Debug Specific Issues
```bash
# Debug with pdb
pytest --pdb

# Debug on failure
pytest --pdb-trace

# Capture output
pytest --capture=no
```

## 📈 Performance Monitoring

### Benchmark Tests

Performance tests include benchmarks for:

- **Query Response Time**: < 500ms for 95th percentile
- **Data Processing**: > 100 documents/second
- **Memory Usage**: < 1GB for 10,000 documents
- **Real-time Latency**: < 2 seconds T+0 to T+1

### Performance Regression Detection

```bash
# Run performance tests with timing
pytest tests/performance/ --durations=10

# Compare with baseline
pytest tests/performance/ --benchmark-compare
```

## 🔄 Real-Time Testing

### Live System Testing

Special tests for real-time capabilities:

```bash
# Test real-time data flow
pytest tests/integration/test_real_time_flow.py

# Test T+0 to T+1 latency
pytest tests/integration/test_real_time_flow.py::test_real_time_latency

# Test concurrent processing
pytest tests/performance/test_concurrent_processing.py
```

### Demo Mode Testing

```bash
# Test demo functionality
pytest tests/integration/test_api_endpoints.py::TestPathwayRAGEndpoints::test_prove_real_time_capability
```

## 📝 Writing New Tests

### Test Naming Convention

```python
# Unit tests
def test_component_functionality():
    """Test specific component functionality."""
    pass

# Integration tests  
def test_api_endpoint_integration():
    """Test API endpoint with realistic data."""
    pass

# Performance tests
def test_query_performance():
    """Test query performance under load."""
    pass
```

### Test Structure

```python
def test_example():
    """Test description explaining what is being tested."""
    # Arrange - Set up test data and mocks
    
    # Act - Execute the functionality being tested
    
    # Assert - Verify the expected outcomes
    
    # Cleanup - Clean up resources if needed
```

### Using Fixtures

```python
def test_with_fixtures(sample_alert, mock_vector_store):
    """Test using common fixtures."""
    # Use the fixtures in your test
    assert sample_alert.severity == "critical"
    mock_vector_store.search.return_value = []
```

## 🎯 Test Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what is being tested
3. **Coverage**: Aim for high code coverage but focus on critical paths
4. **Performance**: Keep unit tests fast (< 1 second each)
5. **Reliability**: Tests should be deterministic and not flaky
6. **Maintenance**: Keep tests simple and easy to understand

## 🆘 Troubleshooting

### Common Issues

**Tests fail with import errors:**
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database connection errors:**
```bash
# Check test database configuration
echo $DATABASE_URL
```

**Mock failures:**
```bash
# Verify mock setup in conftest.py
pytest tests/conftest.py -v
```

**Performance test failures:**
```bash
# Run with increased timeouts
pytest tests/performance/ --timeout=300
```

### Getting Help

1. Check test logs in `test_results.json`
2. Run tests with verbose output: `pytest -v -s`
3. Review coverage reports in `htmlcov/`
4. Check CI logs for detailed error information

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Pathway Testing Guide](https://pathway.com/developers/documentation/testing)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

For questions or issues with the testing framework, please check the project documentation or create an issue in the repository. 