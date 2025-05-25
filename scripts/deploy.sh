#!/bin/bash

# =============================================================================
# Supply Chain Disruption Predictor - Production Deployment Script
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="supply-chain-predictor"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root is not recommended for production deployments."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_success "Prerequisites check passed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs data ssl
    
    # Check if environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning "Environment file $ENV_FILE not found."
        log_info "Creating template environment file..."
        
        cat > "$ENV_FILE" << EOF
# Production Environment Configuration
OPENWEATHER_API_KEY=your_openweather_api_key_here
NEWS_API_KEY=your_news_api_key_here
FLIGHTAWARE_API_KEY=your_flightaware_api_key_here
USGS_API_KEY=not_required

DATABASE_URL=postgresql://supplychain_user:secure_password@postgres:5432/supplychain_db
REDIS_URL=redis://redis:6379/0

DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
HOST=0.0.0.0
PORT=8000

RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_REQUESTS_PER_HOUR=2000

PIPELINE_REFRESH_INTERVAL=300
ALERT_THRESHOLD=0.5
CRITICAL_THRESHOLD=0.8

WEATHER_REFRESH_INTERVAL=300
NEWS_REFRESH_INTERVAL=600
EARTHQUAKE_REFRESH_INTERVAL=180

LOG_LEVEL=INFO
ENABLE_METRICS=True
METRICS_PORT=9090
EOF
        
        log_warning "Please edit $ENV_FILE with your actual configuration before proceeding."
        read -p "Press Enter when ready to continue..."
    fi
    
    log_success "Environment setup completed"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build the application image
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    log_success "Docker images built successfully"
}

initialize_database() {
    log_info "Initializing database..."
    
    # Start only the database service
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d postgres redis
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Run database migrations
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec postgres psql -U supplychain_user -d supplychain_db -c "SELECT 1;" || {
        log_error "Database connection failed"
        exit 1
    }
    
    log_success "Database initialized successfully"
}

deploy_services() {
    log_info "Deploying services..."
    
    # Deploy all services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    # Wait for services to start
    log_info "Waiting for services to start..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Services deployed successfully"
}

check_service_health() {
    log_info "Checking service health..."
    
    # Check API health
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "API service is healthy"
    else
        log_error "API service health check failed"
        return 1
    fi
    
    # Check database
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec postgres pg_isready -U supplychain_user &> /dev/null; then
        log_success "Database service is healthy"
    else
        log_error "Database service health check failed"
        return 1
    fi
    
    # Check Redis
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec redis redis-cli ping | grep -q PONG; then
        log_success "Redis service is healthy"
    else
        log_error "Redis service health check failed"
        return 1
    fi
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create Prometheus configuration
    cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'supply-chain-api'
    static_configs:
      - targets: ['api:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF
    
    # Create Nginx configuration
    cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://api;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /metrics {
            proxy_pass http://api/metrics;
        }
    }
}
EOF
    
    log_success "Monitoring setup completed"
}

show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo
    echo "=== Service URLs ==="
    echo "API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Prometheus: http://localhost:9090"
    echo "Grafana: http://localhost:3000 (admin/admin123)"
    echo "Nginx: http://localhost:80"
    echo
    echo "=== Useful Commands ==="
    echo "View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "Stop services: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo "Restart services: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    echo "Check status: docker-compose -f $DOCKER_COMPOSE_FILE ps"
    echo
    echo "=== Next Steps ==="
    echo "1. Configure your API keys in $ENV_FILE"
    echo "2. Set up SSL certificates in the ssl/ directory"
    echo "3. Configure monitoring dashboards in Grafana"
    echo "4. Set up backup procedures for the database"
}

# Main deployment flow
main() {
    log_info "Starting production deployment of $PROJECT_NAME"
    
    check_prerequisites
    setup_environment
    setup_monitoring
    build_images
    initialize_database
    deploy_services
    show_deployment_info
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" restart
        log_success "Services restarted"
        ;;
    "logs")
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
        ;;
    "status")
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
        ;;
    "health")
        check_service_health
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|health}"
        exit 1
        ;;
esac 