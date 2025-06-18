"""Pydantic models for API request/response schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class CongestionLevel(str, Enum):
    """Traffic congestion levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RouteType(str, Enum):
    """Route optimization types."""
    FASTEST = "fastest"
    SHORTEST = "shortest"
    ECO_FRIENDLY = "eco_friendly"

class Coordinates(BaseModel):
    """Geographic coordinates."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")

class RouteRequest(BaseModel):
    """Request model for route planning."""
    source: str = Field(..., description="Source location (address or coordinates)")
    destination: str = Field(..., description="Destination location (address or coordinates)")
    route_type: RouteType = Field(default=RouteType.FASTEST, description="Type of route optimization")
    avoid_tolls: bool = Field(default=False, description="Avoid toll roads")
    avoid_highways: bool = Field(default=False, description="Avoid highways")

class TrafficPredictionRequest(BaseModel):
    """Request model for traffic prediction."""
    coordinates: Coordinates
    timestamp: Optional[datetime] = Field(default=None, description="Prediction timestamp (defaults to now)")
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6, description="Day of week (0=Monday)")
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23, description="Hour of day")

class TrafficPredictionResponse(BaseModel):
    """Response model for traffic prediction."""
    coordinates: Coordinates
    congestion_level: CongestionLevel
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    predicted_delay_minutes: int = Field(..., ge=0, description="Expected delay in minutes")
    timestamp: datetime

class RouteStep(BaseModel):
    """Individual step in a route."""
    instruction: str
    distance: str
    duration: str
    start_location: Coordinates
    end_location: Coordinates

class RouteInfo(BaseModel):
    """Route information."""
    distance: str
    duration: str
    duration_in_traffic: Optional[str] = None
    steps: List[RouteStep]
    polyline: str
    bounds: Dict[str, Any]
    carbon_estimate_kg: Optional[float] = Field(default=None, description="Estimated CO2 emissions in kg")
    eco_score: Optional[int] = Field(default=None, ge=0, le=100, description="Eco-friendliness score (0-100)")

class RouteResponse(BaseModel):
    """Response model for route requests."""
    routes: List[RouteInfo]
    status: str
    carbon_estimate_kg: Optional[float] = Field(default=None, description="Estimated CO2 emissions in kg")
    eco_score: Optional[int] = Field(default=None, ge=0, le=100, description="Eco-friendliness score (0-100)")

class TrafficStatsRequest(BaseModel):
    """Request model for traffic statistics."""
    area_bounds: Optional[Dict[str, Coordinates]] = Field(default=None, description="Geographic bounds for stats")
    start_date: Optional[datetime] = Field(default=None, description="Start date for historical data")
    end_date: Optional[datetime] = Field(default=None, description="End date for historical data")
    aggregation: str = Field(default="hourly", description="Data aggregation level")

class TrafficStatsResponse(BaseModel):
    """Response model for traffic statistics."""
    average_congestion: CongestionLevel
    peak_hours: List[int]
    congestion_by_hour: Dict[int, CongestionLevel]
    total_data_points: int
    date_range: Dict[str, datetime]

class EcoRouteRequest(BaseModel):
    """Request model for eco-friendly routing."""
    source: str
    destination: str
    vehicle_type: str = Field(default="car", description="Vehicle type for emission calculation")
    fuel_efficiency: Optional[float] = Field(default=None, description="Vehicle fuel efficiency (mpg or l/100km)")
    prioritize_emissions: bool = Field(default=True, description="Prioritize low emissions over time")

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Gemini AI Models
class GeminiQueryRequest(BaseModel):
    """Request model for Gemini AI natural language queries."""
    query: str = Field(..., description="Natural language query about traffic or routes")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the query")

class GeminiQueryResponse(BaseModel):
    """Response model for Gemini AI queries."""
    success: bool
    query: str
    parsed: Optional[Dict[str, Any]] = None
    response: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime

class ConversationalRequest(BaseModel):
    """Request model for conversational AI."""
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Conversation context")

class ConversationalResponse(BaseModel):
    """Response model for conversational AI."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime
