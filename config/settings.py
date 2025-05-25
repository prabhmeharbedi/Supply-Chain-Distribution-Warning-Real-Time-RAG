from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    # API Keys
    openweather_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    flightaware_api_key: Optional[str] = None
    usgs_api_key: Optional[str] = None
    
    # AI/ML API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # Database
    database_url: str = "postgresql://user:password@localhost/supplychain"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Application
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_requests_per_hour: int = 2000
    
    # Pipeline Settings
    pipeline_refresh_interval: int = 300  # 5 minutes
    alert_threshold: float = 0.5
    critical_threshold: float = 0.8
    
    # External API Settings
    weather_refresh_interval: int = 300  # 5 minutes
    news_refresh_interval: int = 600     # 10 minutes
    earthquake_refresh_interval: int = 180  # 3 minutes
    
    # Pathway-specific settings
    pathway_monitoring_port: int = 8080
    pathway_cache_size: int = 10000
    pathway_batch_size: int = 100
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/supply_chain.log"
    
    # Monitoring and Metrics
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 60
    
    # AI/RAG Specific Settings
    vector_store_dimension: int = 384
    vector_store_index_type: str = "faiss"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # AI Analysis Settings
    ai_temperature: float = 0.3
    ai_max_tokens: int = 500
    ai_model: str = "gpt-3.5-turbo"
    
    # RAG Settings
    rag_search_k: int = 5
    rag_similarity_threshold: float = 0.3
    rag_context_window: int = 3000
    
    # Real-time Processing Settings
    real_time_update_interval: int = 30
    vector_store_update_batch_size: int = 10
    streaming_buffer_size: int = 1000
    
    # WebSocket Settings
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    # Production Deployment Settings
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    cors_origins: Optional[str] = None
    cors_allow_credentials: bool = True
    
    # Database Connection Pool
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    
    # Backup and Recovery
    backup_enabled: bool = False
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    backup_s3_bucket: Optional[str] = None
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",  # Ignore extra fields instead of raising errors
        case_sensitive=False
    )

settings = Settings() 