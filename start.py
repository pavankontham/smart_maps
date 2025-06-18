#!/usr/bin/env python3
"""
SmartCity AI - Startup Script
Launches the FastAPI application with proper configuration
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
from backend.utils.config import config

def setup_logging():
    """Setup logging configuration."""
    log_level = logging.DEBUG if config.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('smartcity-ai.log') if not config.DEBUG else logging.NullHandler()
        ]
    )

def validate_environment():
    """Validate required environment variables and configurations."""
    logger = logging.getLogger(__name__)
    
    # Check critical API keys
    missing_keys = []
    
    if not config.GOOGLE_MAPS_API_KEY:
        missing_keys.append("GOOGLE_MAPS_API_KEY")
    
    if not config.GEMINI_API_KEY:
        missing_keys.append("GEMINI_API_KEY")
    
    if missing_keys:
        logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
        logger.warning("Some features may not work properly without these keys")
    
    # Check optional API keys
    optional_keys = {
        'WEATHERAPI_KEY': config.WEATHERAPI_KEY,
        'TOMTOM_API_KEY': config.TOMTOM_API_KEY,
        'OPENWEATHER_API_KEY': config.OPENWEATHER_API_KEY,
        'TRANSITLAND_API_KEY': config.TRANSITLAND_API_KEY
    }
    
    available_apis = [key for key, value in optional_keys.items() if value]
    logger.info(f"Available real data APIs: {', '.join(available_apis) if available_apis else 'None (using fallback data)'}")
    
    # Check file structure
    required_files = [
        'frontend/index.html',
        'frontend/auth.html',
        'frontend/static/js/firebase-config.js',
        'frontend/static/js/auth.js',
        'frontend/static/js/main.js',
        'frontend/static/css/style.css',
        'frontend/static/css/auth.css'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    logger.info("Environment validation completed successfully")
    return True

def print_startup_info():
    """Print startup information."""
    print("\n" + "="*60)
    print("🚦 SmartCity AI - Traffic Optimization System")
    print("="*60)
    print(f"🌐 Server: http://{config.HOST}:{config.PORT}")
    print(f"📚 API Docs: http://{config.HOST}:{config.PORT}/docs")
    print(f"🔧 Debug Mode: {'ON' if config.DEBUG else 'OFF'}")
    print(f"🗝️  Google Maps: {'✅' if config.GOOGLE_MAPS_API_KEY else '❌'}")
    print(f"🤖 Gemini AI: {'✅' if config.GEMINI_API_KEY else '❌'}")
    print(f"🌤️  Weather APIs: {'✅' if any([config.WEATHERAPI_KEY, config.OPENWEATHER_API_KEY]) else '❌'}")
    print(f"🚗 Traffic API: {'✅' if config.TOMTOM_API_KEY else '❌'}")
    print(f"🚌 Transit API: {'✅' if config.TRANSITLAND_API_KEY else '❌'}")
    print("="*60)
    print("📋 Available Features:")
    print("   • User Authentication (Firebase)")
    print("   • Route Planning (Google Maps)")
    print("   • AI Assistant (Gemini)")
    print("   • Search History (Firestore)")
    print("   • Real-time Data Integration")
    print("   • Eco-friendly Route Optimization")
    print("="*60)
    print("🚀 Starting server...")
    print()

def main():
    """Main startup function."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Print startup information
        print_startup_info()
        
        # Validate environment
        if not validate_environment():
            logger.error("Environment validation failed. Please check your configuration.")
            sys.exit(1)
        
        # Validate configuration
        config.validate_required_keys()
        
        logger.info("Starting SmartCity AI Traffic Optimization System")
        
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG,
            log_level="debug" if config.DEBUG else "info",
            access_log=True,
            reload_dirs=[str(project_root)] if config.DEBUG else None
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
