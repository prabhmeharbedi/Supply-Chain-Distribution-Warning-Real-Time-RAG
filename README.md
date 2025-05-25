# Real-Time RAG Supply Chain Intelligence

A **Pathway-powered real-time RAG system** for supply chain disruption prediction and intelligence. This system demonstrates true real-time capabilities where **data updated at T+0 is immediately available for queries at T+1** - no rebuilds, no delays, just instant intelligence.

## 🎯 **Pathway Integration Highlights**

✅ **Streaming ETL**: Continuous data ingestion using Pathway framework  
✅ **Dynamic Indexing**: Real-time vector store updates with no rebuilds  
✅ **Live Retrieval**: Immediate query results reflecting latest data  
✅ **AI-Powered RAG**: OpenAI integration with real-time context retrieval

## 🚀 Features

### Core Capabilities
- **Real-time Data Processing**: Pathway-powered streaming ETL pipeline
- **Multi-source Intelligence**: Weather, news, earthquake, and transportation data
- **Intelligent Disruption Detection**: AI-powered analysis of supply chain impacts
- **Impact Assessment**: Financial impact estimation and mitigation strategies
- **Real-time Dashboard**: Interactive monitoring and alerting interface
- **REST API**: Comprehensive API for integration with existing systems

### Data Sources
- **Weather**: OpenWeatherMap API for severe weather alerts
- **News**: NewsAPI for supply chain related news and events
- **Earthquakes**: USGS earthquake data for natural disaster monitoring
- **Transportation**: Flight and shipping status monitoring

### Alert Categories
- **Critical**: Immediate action required (>70% confidence, high impact)
- **Warning**: Monitor closely (50-70% confidence, medium impact)
- **Watch**: Awareness only (<50% confidence, low-medium impact)

## 🏗️ Architecture

```
Data Sources → Pathway ETL → Processing Engine → Vector DB → API Layer → Frontend
     ↓              ↓              ↓              ↓          ↓         ↓
  Weather         Stream         Disruption    Embeddings   REST     Dashboard
  News           Processing      Detection      & Search    API      Mobile App
  Transport      Real-time       ML Models     Historical   Webhooks  Alerts
  Government     Indexing        Scoring       Context
```

### Technology Stack
- **Core Framework**: Pathway (real-time data processing)
- **Backend**: Python, FastAPI
- **Database**: PostgreSQL (structured data)
- **Frontend**: React.js, Material-UI (planned)
- **Infrastructure**: Docker, Docker Compose
- **Monitoring**: Built-in logging and health checks

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+ (optional, for caching)
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd Real-Time-RAG
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your API keys and database credentials
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb supplychain

# Set up database tables
python src/main.py --setup-db
```

5. **Run the application**
```bash
# Run API server (includes pipeline)
python src/main.py --port 8001

# Or run pipeline only
python src/main.py --mode pipeline
```

### 🎬 **Real-Time Demo**

Experience Pathway's real-time capabilities:

```bash
# Terminal 1: Start the API server
python src/main.py --port 8001

# Terminal 2: Run the real-time demo
python demo_real_time_rag.py
```

This demo **proves** that data updated at T+0 is immediately available at T+1!

### Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
OPENWEATHER_API_KEY=your_openweather_api_key_here
NEWS_API_KEY=your_news_api_key_here
FLIGHTAWARE_API_KEY=your_flightaware_api_key_here
USGS_API_KEY=your_usgs_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost/supplychain

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Application
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
HOST=0.0.0.0
PORT=8000

# Pipeline Settings
PIPELINE_REFRESH_INTERVAL=300
ALERT_THRESHOLD=0.5
CRITICAL_THRESHOLD=0.8

# External API Settings
WEATHER_REFRESH_INTERVAL=300
NEWS_REFRESH_INTERVAL=600
EARTHQUAKE_REFRESH_INTERVAL=180
```

### API Keys Setup

1. **OpenWeatherMap**: Get free API key at [openweathermap.org](https://openweathermap.org/api)
2. **NewsAPI**: Get free API key at [newsapi.org](https://newsapi.org/)
3. **USGS**: No API key required for earthquake data
4. **FlightAware**: Optional, for enhanced transportation monitoring

## 🚀 Usage

### Running the Application

```bash
# Check dependencies and configuration
python src/main.py --check

# Set up database tables
python src/main.py --setup-db

# Run API server (default mode)
python src/main.py

# Run with custom host/port
python src/main.py --host 127.0.0.1 --port 8080

# Run in debug mode
python src/main.py --debug

# Run pipeline only (no API server)
python src/main.py --mode pipeline
```

### API Endpoints

The API server runs on `http://localhost:8000` by default.

#### Authentication
All API endpoints require a Bearer token. For demo purposes, use `demo_token`:

```bash
curl -H "Authorization: Bearer demo_token" http://localhost:8000/api/v1/alerts
```

#### Key Endpoints

**Core API:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /api/v1/alerts` - Get supply chain alerts
- `GET /api/v1/alerts/{id}` - Get specific alert
- `GET /api/v1/dashboard/stats` - Dashboard statistics

**🔥 Pathway Real-Time RAG API:**
- `POST /api/v1/pathway-rag/query/real-time` - Real-time RAG queries
- `POST /api/v1/pathway-rag/data/add-live` - Add data with immediate availability
- `GET /api/v1/pathway-rag/demo/real-time-proof` - Prove real-time capabilities
- `GET /api/v1/pathway-rag/stats/real-time` - Real-time system statistics
- `GET /api/v1/pathway-rag/health/pathway` - Pathway component health
- `WS /api/v1/pathway-rag/ws/live-updates` - WebSocket for live updates

**AI Intelligence:**
- `POST /api/v1/ai/analyze/disruptions` - AI-powered disruption analysis
- `POST /api/v1/ai/predict/event-impact` - Event impact prediction
- `GET /api/v1/ai/insights/supply-chain` - Supply chain insights

#### Example API Calls

```bash
# Get all active alerts
curl -H "Authorization: Bearer demo_token" \
  "http://localhost:8000/api/v1/alerts?active_only=true"

# Get critical alerts only
curl -H "Authorization: Bearer demo_token" \
  "http://localhost:8000/api/v1/alerts?severity=critical"

# Get dashboard statistics
curl -H "Authorization: Bearer demo_token" \
  "http://localhost:8000/api/v1/dashboard/stats"

# Get pipeline status
curl -H "Authorization: Bearer demo_token" \
  "http://localhost:8000/api/v1/pipeline/status"
```

### Response Format

```json
{
  "id": 1,
  "event_type": "weather",
  "severity": "warning",
  "title": "Severe Weather: Thunderstorm",
  "description": "Thunderstorm conditions detected",
  "location": "Los Angeles Port",
  "latitude": 33.7361,
  "longitude": -118.2639,
  "confidence_score": 0.85,
  "impact_score": 0.65,
  "source": "weather",
  "alert_level": "warning",
  "priority_rank": 35,
  "affected_routes": ["trans_pacific"],
  "mitigation_strategies": [
    "Monitor weather forecasts for route planning",
    "Consider alternative transportation modes"
  ],
  "financial_impact": {
    "daily_impact_usd_millions": 32.5,
    "weekly_impact_usd_millions": 227.5,
    "affected_trade_volume_percent": 65.0
  },
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 🔧 Development

### Project Structure

```
Real-Time-RAG/
├── src/
│   ├── api/                 # FastAPI application
│   │   ├── core/               # Core processing logic
│   │   │   ├── pipeline/       # Pathway data pipeline
│   │   │   ├── processors/     # Data processors
│   │   │   └── detectors/      # Disruption detection
│   │   ├── models/             # Database models
│   │   ├── services/           # External service integrations
│   │   │   ├── weather/        # Weather data service
│   │   │   ├── news/          # News data service
│   │   │   └── transport/     # Transportation data service
│   │   └── utils/             # Utility functions
│   ├── config/                # Configuration files
│   ├── tests/                 # Test files
│   ├── docs/                  # Documentation
│   ├── data/                  # Data storage
│   └── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_disruption_detector.py
```

### Adding New Data Sources

1. Create a new service in `src/services/`
2. Implement data fetching and processing logic
3. Add to the pipeline in `src/core/pipeline/supply_chain_pipeline.py`
4. Update configuration in `config/settings.py`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📊 Monitoring and Observability

### Health Checks

The application provides several health check endpoints:

- `/health` - Basic health status
- `/api/v1/pipeline/status` - Detailed pipeline status

### Logging

Logs are written to stdout with structured formatting:

```
2024-01-15 10:30:00 - src.core.pipeline - INFO - Pipeline started successfully
2024-01-15 10:30:05 - src.services.weather - INFO - Fetched 3 weather alerts
2024-01-15 10:30:10 - src.core.detectors - INFO - Detected 1 potential disruptions
```

### Metrics

Key metrics tracked:
- Alerts generated per hour
- Pipeline processing latency
- Data source availability
- Prediction accuracy
- API response times

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```
   Solution: Check DATABASE_URL in .env file and ensure PostgreSQL is running
   ```

2. **API Key Errors**
   ```
   Solution: Verify API keys in .env file and check rate limits
   ```

3. **Pipeline Not Starting**
   ```
   Solution: Check logs for specific errors, verify data source connectivity
   ```

4. **High Memory Usage**
   ```
   Solution: Adjust pipeline refresh intervals in configuration
   ```

### Debug Mode

Run with debug logging:

```bash
python src/main.py --debug
```

### Checking Configuration

```bash
python src/main.py --check
```

## 📈 Performance

### Expected Performance
- **Throughput**: 1000+ events/day processing
- **Latency**: <30 seconds from data ingestion to alert
- **Accuracy**: 80%+ for 2+ day predictions
- **Uptime**: 99.9% availability target

### Scaling Considerations
- Use Redis for caching frequently accessed data
- Implement horizontal scaling with multiple pipeline instances
- Consider database read replicas for high query loads
- Use CDN for frontend assets

## 🔒 Security

### Authentication
- Bearer token authentication for API access
- Rate limiting on API endpoints
- Input validation and sanitization

### Data Protection
- No sensitive data stored in logs
- API keys stored in environment variables
- Database connections encrypted

### Production Deployment
- Use strong secret keys
- Enable HTTPS/TLS
- Implement proper firewall rules
- Regular security updates

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` directory
- Review the API documentation at `/docs` when running the server

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core pipeline implementation
- ✅ Basic disruption detection
- ✅ REST API
- ✅ Weather and earthquake data sources

### Phase 2 (Next)
- 🔄 Enhanced ML models for prediction
- 🔄 React frontend dashboard
- 🔄 Email/SMS notifications
- 🔄 Advanced analytics

### Phase 3 (Future)
- 📋 Machine learning prediction models
- 📋 Supply chain mapping
- 📋 Mobile application
- 📋 Enterprise integrations

---

**Built with ❤️ using Pathway, FastAPI, and modern Python technologies.**