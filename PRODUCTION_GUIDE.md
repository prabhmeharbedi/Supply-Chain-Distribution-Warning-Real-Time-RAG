# 🚀 Production Deployment Guide

## Supply Chain Disruption Predictor - Production Setup

This guide covers the complete production deployment of the Supply Chain Disruption Predictor system.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **RAM**: Minimum 8GB, Recommended 16GB+
- **CPU**: Minimum 4 cores, Recommended 8+ cores
- **Storage**: Minimum 50GB free space
- **Network**: Stable internet connection for API access

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for generating secrets)

## 🔧 Production Setup Steps

### 1. Clone and Prepare Repository

```bash
git clone <repository-url>
cd Real-Time-RAG
chmod +x scripts/deploy.sh
```

### 2. Configure API Keys

Get your API keys from:
- **OpenWeatherMap**: https://openweathermap.org/api (Free tier available)
- **NewsAPI**: https://newsapi.org/ (Free tier: 1000 requests/day)
- **FlightAware**: https://flightaware.com/commercial/flightxml/ (Optional)

### 3. Environment Configuration

Create `.env.production` file:

```bash
# Copy template and edit
cp .env.production.template .env.production
nano .env.production
```

**Required Configuration:**
```env
# API Keys (REQUIRED)
OPENWEATHER_API_KEY=your_actual_api_key_here
NEWS_API_KEY=your_actual_api_key_here

# Database (Auto-configured by Docker)
DATABASE_URL=postgresql://supplychain_user:secure_password@postgres:5432/supplychain_db

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secure-secret-key-change-this
DEBUG=False

# Application Settings
HOST=0.0.0.0
PORT=8000
ALERT_THRESHOLD=0.5
```

### 4. Deploy with Script

```bash
# Full deployment
./scripts/deploy.sh deploy

# Or step by step:
./scripts/deploy.sh stop      # Stop existing services
./scripts/deploy.sh deploy    # Deploy fresh
./scripts/deploy.sh status    # Check status
./scripts/deploy.sh health    # Health check
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   FastAPI App   │    │   PostgreSQL    │
│  (Port 80/443)  │────│   (Port 8000)   │────│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │      Redis      │    │   Prometheus    │
                       │   (Port 6379)   │    │   (Port 9090)   │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │     Grafana     │
                       │   (Port 3000)   │
                       └─────────────────┘
```

## 🔐 Security Configuration

### 1. JWT Authentication

The system uses JWT tokens for authentication:

```python
# Create admin user (run once)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@company.com",
    "password": "secure_password",
    "role": "admin"
  }'

# Login to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password"
  }'
```

### 2. SSL/TLS Setup

For production, set up SSL certificates:

```bash
# Create SSL directory
mkdir -p ssl

# Option 1: Let's Encrypt (recommended)
certbot certonly --standalone -d your-domain.com

# Option 2: Self-signed (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/private.key -out ssl/certificate.crt
```

Update `nginx.conf` for HTTPS:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    # ... rest of config
}
```

### 3. Firewall Configuration

```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# Block direct access to internal ports
sudo ufw deny 5432   # PostgreSQL
sudo ufw deny 6379   # Redis
sudo ufw deny 8000   # Direct API access
```

## 📊 Monitoring & Observability

### 1. Prometheus Metrics

Access metrics at: `http://localhost:9090`

**Key Metrics:**
- `http_requests_total` - Total HTTP requests
- `pipeline_processing_duration_seconds` - Processing time
- `disruption_alerts_total` - Alert counts
- `system_cpu_usage_percent` - CPU usage
- `system_memory_usage_percent` - Memory usage

### 2. Grafana Dashboards

Access Grafana at: `http://localhost:3000`
- **Username**: admin
- **Password**: admin123

**Pre-configured Dashboards:**
- System Overview
- API Performance
- Supply Chain Alerts
- Data Source Health

### 3. Log Management

```bash
# View real-time logs
docker-compose -f docker-compose.production.yml logs -f

# View specific service logs
docker-compose -f docker-compose.production.yml logs -f api
docker-compose -f docker-compose.production.yml logs -f postgres

# Log rotation (add to crontab)
0 2 * * * docker-compose -f /path/to/docker-compose.production.yml logs --no-color > /var/log/supply-chain.log 2>&1
```

## 🔄 Backup & Recovery

### 1. Database Backup

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U supplychain_user supplychain_db > backup_${DATE}.sql
EOF

chmod +x backup.sh

# Schedule daily backups
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

### 2. Data Recovery

```bash
# Restore from backup
docker-compose -f docker-compose.production.yml exec -T postgres psql -U supplychain_user supplychain_db < backup_20240125_020000.sql
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose -f docker-compose.production.yml exec postgres pg_isready
   
   # Reset database
   docker-compose -f docker-compose.production.yml down -v
   docker-compose -f docker-compose.production.yml up -d postgres
   ```

3. **API Keys Not Working**
   - Verify API keys in `.env.production`
   - Check API rate limits
   - Restart services: `./scripts/deploy.sh restart`

4. **High Memory Usage**
   ```bash
   # Monitor resource usage
   docker stats
   
   # Adjust memory limits in docker-compose.production.yml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

### Health Checks

```bash
# System health
./scripts/deploy.sh health

# Individual service health
curl http://localhost:8000/health
curl http://localhost:9090/-/healthy
```

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_disruption_events_created_at ON disruption_events(created_at);
CREATE INDEX idx_disruption_events_severity ON disruption_events(severity);
CREATE INDEX idx_disruption_events_location ON disruption_events(location);
```

### 2. Caching Strategy

Redis is used for:
- API response caching
- Session management
- Rate limiting
- Temporary data storage

### 3. Load Balancing

For high-traffic deployments:

```yaml
# docker-compose.production.yml
api:
  deploy:
    replicas: 3
  # ... rest of config
```

## 🔧 Maintenance

### Regular Tasks

1. **Weekly**:
   - Check system resources
   - Review error logs
   - Verify backup integrity

2. **Monthly**:
   - Update dependencies
   - Security patches
   - Performance review

3. **Quarterly**:
   - Disaster recovery test
   - Security audit
   - Capacity planning

### Update Procedure

```bash
# 1. Backup current state
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Rebuild and deploy
./scripts/deploy.sh stop
./scripts/deploy.sh deploy

# 4. Verify deployment
./scripts/deploy.sh health
```

## 📞 Support

For production support:
- Check logs: `./scripts/deploy.sh logs`
- Monitor metrics: http://localhost:9090
- Health status: `./scripts/deploy.sh health`

## 🔒 Security Checklist

- [ ] Changed default passwords
- [ ] Configured SSL/TLS
- [ ] Set up firewall rules
- [ ] Enabled log monitoring
- [ ] Configured backup procedures
- [ ] Set up monitoring alerts
- [ ] Reviewed API key permissions
- [ ] Implemented rate limiting
- [ ] Configured user authentication
- [ ] Set up network security

---

**🎉 Your Supply Chain Disruption Predictor is now production-ready!** 