"""
SmartCity AI - Main FastAPI Application
Complete traffic optimization system with real data integration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os

# Import services
from backend.services.real_data_service import real_data_service
from backend.services.eco_chatbot_service import eco_chatbot_service
from backend.services.google_maps import google_maps_service
from backend.utils.config import config
from backend.models.schemas import (
    RouteRequest, RouteResponse, ConversationalRequest, ConversationalResponse,
    GeminiQueryRequest, GeminiQueryResponse, RouteType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SmartCity AI",
    description="Intelligent Traffic Optimization System with Real-time Data",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# === HTML PAGES ===

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Redirect to authentication page."""
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SmartCity AI</title>
            <meta http-equiv="refresh" content="0; url=/auth.html">
        </head>
        <body>
            <p>Redirecting to authentication...</p>
            <script>window.location.href = '/auth.html';</script>
        </body>
        </html>
        """,
        status_code=200
    )

@app.get("/auth.html", response_class=HTMLResponse)
async def serve_auth_page():
    """Serve the authentication page."""
    try:
        with open("frontend/auth.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Authentication Page Not Found</h1>",
            status_code=404
        )

@app.get("/dashboard.html", response_class=HTMLResponse)
async def serve_dashboard_page():
    """Serve the main dashboard page with full functionality."""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Dashboard Page Not Found</h1>",
            status_code=404
        )

@app.get("/index.html", response_class=HTMLResponse)
async def serve_main_page():
    """Serve the main application page."""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Main Page Not Found</h1>",
            status_code=404
        )

@app.get("/debug_auth.html", response_class=HTMLResponse)
async def serve_debug_auth_page():
    """Serve the debug authentication page."""
    try:
        with open("frontend/debug_auth.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Debug Page Not Found</h1>",
            status_code=404
        )

# === API CONFIGURATION ===

@app.get("/api/config")
async def get_config():
    """Get frontend configuration."""
    return {
        "google_maps_api_key": config.GOOGLE_MAPS_API_KEY,
        "app_name": "SmartCity AI",
        "version": "2.0.0",
        "features": {
            "real_weather": True,
            "real_traffic": True,
            "real_transit": True,
            "eco_routes": True,
            "ai_assistant": True,
            "user_auth": True,
            "google_maps": google_maps_service.is_available(),
            "eco_chatbot": eco_chatbot_service.is_available()
        }
    }

# === ROUTE PLANNING ===

@app.post("/api/route", response_model=RouteResponse)
async def get_route(route_request: RouteRequest):
    """Get optimized route using Google Maps with enhanced eco calculations."""
    try:
        logger.info(f"Route request: {route_request.source} -> {route_request.destination} (type: {route_request.route_type})")

        # Get route from Google Maps service
        route_response = google_maps_service.get_route(route_request)

        if not route_response.routes:
            raise HTTPException(status_code=404, detail="No routes found")

        # Enhance routes with real-time environmental data for better accuracy
        for route in route_response.routes:
            if route_request.route_type == RouteType.ECO_FRIENDLY:
                # Get enhanced emissions data using real-time environmental factors
                distance_km = google_maps_service._extract_distance_km(route.distance)
                duration_minutes = google_maps_service._parse_duration_minutes(route.duration)

                enhanced_emissions = await real_data_service.get_real_emissions_data({
                    'distance_km': distance_km,
                    'duration_minutes': duration_minutes,
                    'vehicle_type': 'car',
                    'route_type': route_request.route_type.value,
                    'lat': 17.3850,  # Default coordinates, could be extracted from route
                    'lon': 78.4867
                })

                # Update route with enhanced data
                route.carbon_estimate_kg = enhanced_emissions.get('co2_kg', route.carbon_estimate_kg)
                route.eco_score = enhanced_emissions.get('eco_score', route.eco_score)

                logger.info(f"Enhanced eco route: {route.distance}, CO2: {route.carbon_estimate_kg}kg, Score: {route.eco_score}")

        return route_response

    except Exception as e:
        logger.error(f"Error getting route: {e}")
        raise HTTPException(status_code=500, detail=f"Route calculation failed: {str(e)}")

# === REAL DATA ENDPOINTS ===

@app.get("/api/weather")
async def get_weather_data(city: str = "Hyderabad", lat: float = 17.3850, lon: float = 78.4867):
    """Get comprehensive real-time weather and air quality data."""
    try:
        weather_data = await real_data_service.get_comprehensive_weather_data(city, lat, lon)
        return weather_data
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        raise HTTPException(status_code=500, detail="Weather service unavailable")

@app.get("/api/traffic")
async def get_traffic_data(lat: float = 17.3850, lon: float = 78.4867, radius: int = 5000):
    """Get comprehensive real-time traffic data."""
    try:
        traffic_data = await real_data_service.get_comprehensive_traffic_data(lat, lon, radius)
        return traffic_data
    except Exception as e:
        logger.error(f"Error getting traffic data: {e}")
        raise HTTPException(status_code=500, detail="Traffic service unavailable")

@app.get("/api/transit")
async def get_transit_data(lat: float = 17.3850, lon: float = 78.4867, radius: float = 1000):
    """Get real-time public transit data."""
    try:
        transit_data = await real_data_service.get_real_transit_data(lat, lon, radius)
        return transit_data
    except Exception as e:
        logger.error(f"Error getting transit data: {e}")
        raise HTTPException(status_code=500, detail="Transit service unavailable")

@app.get("/api/air_quality")
async def get_air_quality(lat: float = 17.3850, lon: float = 78.4867):
    """Get real-time air quality data."""
    try:
        air_quality_data = await real_data_service.get_real_air_quality(lat, lon)
        return air_quality_data
    except Exception as e:
        logger.error(f"Error getting air quality data: {e}")
        raise HTTPException(status_code=500, detail="Air quality service unavailable")

# === ECO CHATBOT ENDPOINTS ===

@app.post("/api/eco_chat")
async def eco_chat(request: ConversationalRequest):
    """Chat with the eco assistant powered by Gemini."""
    try:
        response = await eco_chatbot_service.get_chat_response(request.message, request.context)
        
        return ConversationalResponse(
            success=True,
            response=response["response"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in eco chat: {e}")
        raise HTTPException(status_code=500, detail="Chat service unavailable")

@app.get("/api/eco_tips")
async def get_eco_tips(location: str = None, commute_distance: float = None):
    """Get personalized eco tips."""
    try:
        context = {}
        if location:
            context["location"] = location
        if commute_distance:
            context["commute_distance"] = commute_distance

        tips = eco_chatbot_service.get_eco_tips(context)

        return {
            "success": True,
            "tips": tips,
            "timestamp": datetime.now().isoformat(),
            "personalized": bool(context)
        }

    except Exception as e:
        logger.error(f"Error getting eco tips: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get eco tips: {str(e)}")

# === EMISSIONS CALCULATION ===

@app.post("/api/emissions")
async def calculate_emissions(route_data: Dict[str, Any]):
    """Calculate emissions for a given route."""
    try:
        emissions_data = await real_data_service.get_real_emissions_data(route_data)
        return emissions_data
    except Exception as e:
        logger.error(f"Error calculating emissions: {e}")
        raise HTTPException(status_code=500, detail="Emissions calculation failed")

# === HEALTH CHECK ===

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "google_maps": google_maps_service.is_available(),
            "eco_chatbot": eco_chatbot_service.is_available(),
            "real_data": True  # real_data_service is always available with fallbacks
        },
        "version": "2.0.0"
    }

# === STARTUP EVENT ===

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting SmartCity AI application")
    logger.info(f"Google Maps API configured: {bool(config.GOOGLE_MAPS_API_KEY)}")
    logger.info(f"Gemini AI configured: {bool(config.GEMINI_API_KEY)}")
    logger.info(f"Weather API configured: {bool(config.WEATHERAPI_KEY)}")
    logger.info(f"TomTom API configured: {bool(config.TOMTOM_API_KEY)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down SmartCity AI application")
    await real_data_service.close_session()

if __name__ == "__main__":
    import uvicorn
    
    # Validate configuration
    config.validate_required_keys()
    
    logger.info("Starting SmartCity AI Traffic Optimization System")
    
    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="debug" if config.DEBUG else "info"
    )
