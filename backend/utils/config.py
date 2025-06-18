"""Configuration management for the Smart City Traffic Optimization System."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # Google Gemini AI API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Google Cloud
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # BigQuery
    BIGQUERY_DATASET_ID: str = os.getenv("BIGQUERY_DATASET_ID", "traffic_data")
    BIGQUERY_TABLE_ID: str = os.getenv("BIGQUERY_TABLE_ID", "traffic_logs")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # ML Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "data/traffic_model.pkl")
    TRAINING_DATA_PATH: str = os.getenv("TRAINING_DATA_PATH", "data/sample_traffic_data.csv")
    
    # Real Data API Keys
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    TOMTOM_API_KEY: str = os.getenv("TOMTOM_API_KEY", "")
    WEATHERAPI_KEY: str = os.getenv("WEATHERAPI_KEY", "")
    TRANSITLAND_API_KEY: str = os.getenv("TRANSITLAND_API_KEY", "")
    
    @classmethod
    def validate_required_keys(cls) -> bool:
        """Validate that required configuration keys are present."""
        valid = True
        if not cls.GOOGLE_MAPS_API_KEY:
            print("Warning: GOOGLE_MAPS_API_KEY not set. Google Maps features will not work.")
            valid = False
        if not cls.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not set. AI features will not work.")
            valid = False
        return valid

# Global config instance
config = Config()
