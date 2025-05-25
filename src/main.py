#!/usr/bin/env python3
"""
Supply Chain Disruption Predictor - Main Application Entry Point

This module provides the main entry point for running the supply chain disruption
prediction system. It can run in different modes:
- API server mode (default)
- Pipeline only mode
- Development mode with auto-reload
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

def run_api_server():
    """Run the FastAPI server"""
    import uvicorn
    
    logger.info("Starting Supply Chain Disruption Predictor API Server")
    logger.info(f"Server will run on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )

def run_pipeline_only():
    """Run only the data processing pipeline"""
    from src.core.pipeline.supply_chain_pipeline import SupplyChainPipeline
    
    logger.info("Starting Supply Chain Pipeline (standalone mode)")
    
    pipeline = SupplyChainPipeline()
    
    try:
        pipeline.start()
        logger.info("Pipeline started successfully")
        
        # Keep running until interrupted
        while True:
            asyncio.sleep(60)
            status = pipeline.get_status()
            logger.info(f"Pipeline status: {status}")
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping pipeline...")
        pipeline.stop()
        logger.info("Pipeline stopped")
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        pipeline.stop()
        raise

def setup_database():
    """Set up database tables"""
    from src.core.database import engine, Base
    from src.models.disruption import DisruptionEvent
    
    logger.info("Setting up database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

def check_dependencies():
    """Check if all required dependencies are available"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        "pathway", "fastapi", "uvicorn", "sqlalchemy", 
        "requests", "pandas", "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.error("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies are available")
    return True

def check_configuration():
    """Check if configuration is valid"""
    logger.info("Checking configuration...")
    
    # Check database URL
    if not settings.database_url or settings.database_url == "postgresql://user:password@localhost/supplychain":
        logger.warning("Database URL is using default values. Please configure proper database credentials.")
    
    # Check API keys
    api_keys = {
        "OpenWeather": settings.openweather_api_key,
        "News API": settings.news_api_key,
        "FlightAware": settings.flightaware_api_key,
        "USGS": settings.usgs_api_key
    }
    
    missing_keys = [name for name, key in api_keys.items() if not key]
    
    if missing_keys:
        logger.warning(f"Missing API keys: {missing_keys}")
        logger.warning("Some data sources will not be available without proper API keys")
    else:
        logger.info("All API keys are configured")
    
    logger.info("Configuration check completed")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Supply Chain Disruption Predictor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                    # Run API server (default)
  python src/main.py --mode pipeline    # Run pipeline only
  python src/main.py --setup-db         # Set up database tables
  python src/main.py --check            # Check dependencies and configuration
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["api", "pipeline"],
        default="api",
        help="Run mode: 'api' for API server, 'pipeline' for pipeline only"
    )
    
    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Set up database tables and exit"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependencies and configuration, then exit"
    )
    
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to bind to (default: {settings.port})"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=settings.debug,
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Update settings with command line arguments
    settings.host = args.host
    settings.port = args.port
    settings.debug = args.debug
    
    logger.info("=" * 60)
    logger.info("Supply Chain Disruption Predictor")
    logger.info("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Check configuration
    check_configuration()
    
    # Handle special modes
    if args.check:
        logger.info("Dependency and configuration check completed successfully")
        sys.exit(0)
    
    if args.setup_db:
        setup_database()
        logger.info("Database setup completed successfully")
        sys.exit(0)
    
    # Run the application
    try:
        if args.mode == "api":
            run_api_server()
        elif args.mode == "pipeline":
            run_pipeline_only()
        else:
            logger.error(f"Unknown mode: {args.mode}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
