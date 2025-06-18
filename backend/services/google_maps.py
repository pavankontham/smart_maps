"""Google Maps API integration service."""

import googlemaps
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from backend.utils.config import config
from backend.models.schemas import (
    RouteRequest, RouteResponse, RouteInfo, RouteStep, 
    Coordinates, RouteType, CongestionLevel
)

logger = logging.getLogger(__name__)

class GoogleMapsService:
    """Service for Google Maps API integration."""
    
    def __init__(self):
        """Initialize Google Maps client."""
        if not config.GOOGLE_MAPS_API_KEY or config.GOOGLE_MAPS_API_KEY == "demo_key_replace_with_actual_key":
            logger.warning("Google Maps API key not configured or using demo key")
            self.client = None
        else:
            try:
                self.client = googlemaps.Client(key=config.GOOGLE_MAPS_API_KEY)
                logger.info("Google Maps client initialized successfully")
            except ValueError as e:
                logger.error(f"Invalid Google Maps API key: {e}")
                self.client = None
    
    def get_route(self, route_request: RouteRequest) -> RouteResponse:
        """Get route information from Google Maps Directions API."""
        if not self.client:
            return self._get_mock_route(route_request)

        try:
            # Configure route options
            avoid = []
            if route_request.avoid_tolls:
                avoid.append("tolls")
            if route_request.avoid_highways:
                avoid.append("highways")

            # Determine optimization mode
            optimize_waypoints = route_request.route_type == RouteType.FASTEST

            # Call Directions API
            directions_result = self.client.directions(
                origin=route_request.source,
                destination=route_request.destination,
                mode="driving",
                avoid=avoid,
                departure_time=datetime.now(),
                traffic_model="best_guess",
                optimize_waypoints=optimize_waypoints,
                alternatives=True  # Get multiple route options
            )

            if not directions_result:
                return RouteResponse(routes=[], status="NO_ROUTES_FOUND")

            # Parse routes
            routes = []
            for route in directions_result:
                route_info = self._parse_route(route)

                # Add eco-friendly calculations if requested
                if route_request.route_type == RouteType.ECO_FRIENDLY:
                    route_info = self._add_eco_metrics(route_info)
                elif route_request.route_type == RouteType.SHORTEST:
                    route_info = self._add_shortest_metrics(route_info)
                else:  # FASTEST
                    route_info = self._add_fastest_metrics(route_info)

                routes.append(route_info)

            # Sort routes based on optimization criteria
            routes = self._sort_routes_by_type(routes, route_request.route_type)

            return RouteResponse(
                routes=routes,
                status="OK"
            )

        except Exception as e:
            logger.error(f"Error getting route: {str(e)}")
            return self._get_mock_route(route_request)
    
    def _parse_route(self, route: Dict[str, Any]) -> RouteInfo:
        """Parse Google Maps route response into RouteInfo."""
        leg = route['legs'][0]  # Assuming single leg for now

        # Parse steps
        steps = []
        for step in leg['steps']:
            route_step = RouteStep(
                instruction=step['html_instructions'],
                distance=step['distance']['text'],
                duration=step['duration']['text'],
                start_location=Coordinates(
                    latitude=step['start_location']['lat'],
                    longitude=step['start_location']['lng']
                ),
                end_location=Coordinates(
                    latitude=step['end_location']['lat'],
                    longitude=step['end_location']['lng']
                )
            )
            steps.append(route_step)

        # Get duration in traffic if available
        duration_in_traffic = None
        if 'duration_in_traffic' in leg:
            duration_in_traffic = leg['duration_in_traffic']['text']

        return RouteInfo(
            distance=leg['distance']['text'],
            duration=leg['duration']['text'],
            duration_in_traffic=duration_in_traffic,
            steps=steps,
            polyline=route['overview_polyline']['points'],
            bounds=route['bounds']
        )

    def _format_duration(self, duration_seconds: int) -> str:
        """Format duration from seconds to human readable format."""
        minutes = duration_seconds // 60
        hours = minutes // 60
        remaining_minutes = minutes % 60

        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} min{'s' if remaining_minutes != 1 else ''}"
        else:
            return f"{minutes} min{'s' if minutes != 1 else ''}"

    def _remove_duplicate_routes(self, routes: List[RouteInfo]) -> List[RouteInfo]:
        """Remove duplicate routes based on distance and duration similarity."""
        unique_routes = []

        for route in routes:
            is_duplicate = False
            route_distance = getattr(route, '_raw_distance_km', self._extract_distance_km(route.distance))
            route_duration = getattr(route, '_raw_duration_minutes', self._parse_duration_minutes(route.duration))

            for existing_route in unique_routes:
                existing_distance = getattr(existing_route, '_raw_distance_km', self._extract_distance_km(existing_route.distance))
                existing_duration = getattr(existing_route, '_raw_duration_minutes', self._parse_duration_minutes(existing_route.duration))

                # Consider routes duplicate if distance and duration are very similar (within 5%)
                distance_diff = abs(route_distance - existing_distance) / max(existing_distance, 0.1)
                duration_diff = abs(route_duration - existing_duration) / max(existing_duration, 1)

                if distance_diff < 0.05 and duration_diff < 0.05:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_routes.append(route)

        return unique_routes
    
    def _add_eco_metrics(self, route_info: RouteInfo) -> RouteInfo:
        """Add eco-friendly metrics to route."""
        # Simple carbon emission calculation
        distance_km = self._extract_distance_km(route_info.distance)

        # Average car emissions: ~0.2 kg CO2 per km
        carbon_estimate = distance_km * 0.2

        # Eco score based on distance and traffic
        base_score = max(0, 100 - (distance_km * 2))  # Shorter is better

        # Adjust for traffic (less traffic = higher eco score)
        if route_info.duration_in_traffic:
            traffic_delay = self._calculate_traffic_delay(
                route_info.duration,
                route_info.duration_in_traffic
            )
            base_score = max(0, base_score - (traffic_delay * 5))

        route_info.carbon_estimate_kg = round(carbon_estimate, 2)
        route_info.eco_score = int(base_score)

        return route_info

    def _add_shortest_metrics(self, route_info: RouteInfo) -> RouteInfo:
        """Add metrics for shortest route."""
        distance_km = self._extract_distance_km(route_info.distance)

        # Shortest routes typically have lower emissions due to less distance
        carbon_estimate = distance_km * 0.19  # Slightly lower emission factor

        # Eco score based primarily on distance
        eco_score = max(20, 100 - (distance_km * 1.5))

        route_info.carbon_estimate_kg = round(carbon_estimate, 2)
        route_info.eco_score = int(eco_score)

        return route_info

    def _add_fastest_metrics(self, route_info: RouteInfo) -> RouteInfo:
        """Add metrics for fastest route."""
        distance_km = self._extract_distance_km(route_info.distance)

        # Fastest routes often use highways (better fuel efficiency at steady speeds)
        carbon_estimate = distance_km * 0.18  # Highway driving is more efficient

        # Eco score considers both time efficiency and emissions
        duration_minutes = self._parse_duration_minutes(route_info.duration)
        time_efficiency = max(0, 100 - (duration_minutes * 0.5))
        eco_score = (time_efficiency + max(0, 100 - (distance_km * 2))) / 2

        route_info.carbon_estimate_kg = round(carbon_estimate, 2)
        route_info.eco_score = int(eco_score)

        return route_info

    def _optimize_for_eco_friendly(self, route_info: RouteInfo) -> RouteInfo:
        """Optimize route for eco-friendliness with accurate calculations."""
        distance_km = self._extract_distance_km(route_info.distance)
        duration_minutes = self._parse_duration_minutes(route_info.duration)

        # More accurate carbon emission calculation
        # Base emissions: 0.21 kg CO2/km for average car
        base_emissions = distance_km * 0.21

        # Adjust for traffic conditions (stop-and-go increases emissions by 20-40%)
        traffic_factor = 1.0
        if route_info.duration_in_traffic:
            traffic_delay = self._calculate_traffic_delay(route_info.duration, route_info.duration_in_traffic)
            if traffic_delay > 10:  # Heavy traffic
                traffic_factor = 1.35
            elif traffic_delay > 5:  # Moderate traffic
                traffic_factor = 1.20
            elif traffic_delay > 0:  # Light traffic
                traffic_factor = 1.10

        # Adjust for route type (highways vs city streets)
        # City streets with traffic lights increase emissions
        route_type_factor = 1.15  # Assume eco routes use more city streets

        # Calculate final emissions
        carbon_estimate = base_emissions * traffic_factor * route_type_factor

        # Calculate eco score (0-100, higher is better)
        eco_score = self._calculate_advanced_eco_score(distance_km, duration_minutes, traffic_factor)

        route_info.carbon_estimate_kg = round(carbon_estimate, 3)
        route_info.eco_score = int(eco_score)

        return route_info

    def _optimize_for_shortest(self, route_info: RouteInfo) -> RouteInfo:
        """Optimize route for shortest distance."""
        distance_km = self._extract_distance_km(route_info.distance)

        # Shortest routes typically have lower emissions due to less distance
        carbon_estimate = distance_km * 0.19  # Slightly lower emission factor

        # Eco score based primarily on distance
        eco_score = max(20, 100 - (distance_km * 1.5))

        route_info.carbon_estimate_kg = round(carbon_estimate, 3)
        route_info.eco_score = int(eco_score)

        return route_info

    def _optimize_for_fastest(self, route_info: RouteInfo) -> RouteInfo:
        """Optimize route for fastest time."""
        distance_km = self._extract_distance_km(route_info.distance)

        # Fastest routes often use highways (better fuel efficiency at steady speeds)
        carbon_estimate = distance_km * 0.18  # Highway driving is more efficient

        # Eco score considers both time efficiency and emissions
        duration_minutes = self._parse_duration_minutes(route_info.duration)
        time_efficiency = max(0, 100 - (duration_minutes * 0.5))
        eco_score = (time_efficiency + max(0, 100 - (distance_km * 2))) / 2

        route_info.carbon_estimate_kg = round(carbon_estimate, 3)
        route_info.eco_score = int(eco_score)

        return route_info

    def _calculate_advanced_eco_score(self, distance_km: float, duration_minutes: int, traffic_factor: float) -> float:
        """Calculate advanced eco score considering multiple factors."""
        # Base score starts at 100
        score = 100.0

        # Distance penalty (longer distances = lower score)
        score -= min(distance_km * 1.5, 50)

        # Traffic penalty (more traffic = lower score)
        traffic_penalty = (traffic_factor - 1.0) * 30
        score -= traffic_penalty

        # Efficiency bonus (good distance to time ratio)
        if duration_minutes > 0:
            speed_kmh = (distance_km / duration_minutes) * 60
            if 40 <= speed_kmh <= 60:  # Optimal speed range for fuel efficiency
                score += 10
            elif speed_kmh < 20:  # Very slow, inefficient
                score -= 15

        return max(0, min(100, score))

    def _sort_routes_by_type(self, routes: List[RouteInfo], route_type: RouteType) -> List[RouteInfo]:
        """Sort routes based on optimization criteria."""
        if route_type == RouteType.ECO_FRIENDLY:
            # Sort by eco score (highest first), then by carbon emissions (lowest first)
            return sorted(routes, key=lambda r: (-r.eco_score, r.carbon_estimate_kg or 999))
        elif route_type == RouteType.SHORTEST:
            # Sort by distance (shortest first)
            return sorted(routes, key=lambda r: self._extract_distance_km(r.distance))
        else:  # FASTEST
            # Sort by duration (fastest first)
            return sorted(routes, key=lambda r: self._parse_duration_minutes(r.duration))

    def _add_eco_metrics(self, route_info: RouteInfo) -> RouteInfo:
        """Legacy method - now calls optimize_for_eco_friendly."""
        return self._optimize_for_eco_friendly(route_info)
    
    def _extract_distance_km(self, distance_text: str) -> float:
        """Extract distance in kilometers from text."""
        try:
            # Handle both "X km" and "X mi" formats
            if "km" in distance_text:
                return float(distance_text.replace("km", "").replace(",", "").strip())
            elif "mi" in distance_text:
                miles = float(distance_text.replace("mi", "").replace(",", "").strip())
                return miles * 1.60934  # Convert to km
            else:
                return 0.0
        except:
            return 0.0
    
    def _calculate_traffic_delay(self, normal_duration: str, traffic_duration: str) -> int:
        """Calculate traffic delay in minutes."""
        try:
            # Simple parsing - in reality would need more robust parsing
            normal_mins = self._parse_duration_minutes(normal_duration)
            traffic_mins = self._parse_duration_minutes(traffic_duration)
            return max(0, traffic_mins - normal_mins)
        except:
            return 0
    
    def _parse_duration_minutes(self, duration_text: str) -> int:
        """Parse duration text to minutes."""
        try:
            # Handle formats like "25 mins", "1 hour 30 mins", "2 hours 15 mins", etc.
            total_minutes = 0
            duration_lower = duration_text.lower()

            # Handle hours
            if "hour" in duration_lower:
                # Extract hours part
                if "hours" in duration_lower:
                    hours_part = duration_lower.split("hours")[0].strip()
                else:
                    hours_part = duration_lower.split("hour")[0].strip()

                hours = int(hours_part)
                total_minutes += hours * 60

                # Get remaining part after hours
                if "hours" in duration_lower:
                    remaining = duration_lower.split("hours")[1]
                else:
                    remaining = duration_lower.split("hour")[1]

                # Extract minutes from remaining part
                if "min" in remaining:
                    minutes_part = remaining.split("min")[0].strip()
                    if minutes_part:
                        minutes = int(minutes_part)
                        total_minutes += minutes

            elif "min" in duration_lower:
                # Only minutes, no hours
                minutes_part = duration_lower.split("min")[0].strip()
                minutes = int(minutes_part)
                total_minutes = minutes

            return total_minutes
        except Exception as e:
            return 0
    
    def _get_mock_route(self, route_request: RouteRequest) -> RouteResponse:
        """Provide mock route when Google Maps API is unavailable."""
        mock_steps = [
            RouteStep(
                instruction="Head north on Main St",
                distance="1.2 km",
                duration="3 mins",
                start_location=Coordinates(latitude=17.3850, longitude=78.4867),
                end_location=Coordinates(latitude=17.3950, longitude=78.4867)
            ),
            RouteStep(
                instruction="Turn right onto Highway 1",
                distance="8.5 km",
                duration="12 mins",
                start_location=Coordinates(latitude=17.3950, longitude=78.4867),
                end_location=Coordinates(latitude=17.4065, longitude=78.4772)
            )
        ]
        
        mock_route = RouteInfo(
            distance="9.7 km",
            duration="15 mins",
            duration_in_traffic="18 mins",
            steps=mock_steps,
            polyline="mock_polyline_data",
            bounds={"northeast": {"lat": 17.4065, "lng": 78.4867}, "southwest": {"lat": 17.3850, "lng": 78.4772}},
            carbon_estimate_kg=1.94,
            eco_score=75
        )
        
        return RouteResponse(
            routes=[mock_route],
            status="OK_MOCK"
        )
    
    def get_traffic_layer_data(self, bounds: Dict[str, Coordinates]) -> Dict[str, Any]:
        """Get traffic layer data for a specific area."""
        # This would integrate with Google Maps Traffic API
        # For now, return mock data
        return {
            "traffic_level": "moderate",
            "incidents": [],
            "construction_zones": []
        }

    def is_available(self) -> bool:
        """Check if Google Maps service is available."""
        return self.client is not None

# Global service instance
google_maps_service = GoogleMapsService()
