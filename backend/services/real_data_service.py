"""Real data service for fetching environmental and traffic data from various APIs."""

import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.utils.config import config

logger = logging.getLogger(__name__)

class RealDataService:
    """Service for fetching real environmental and traffic data from various APIs."""

    def __init__(self):
        """Initialize the real data service."""
        self.session = None

        # API Keys from config
        self.weather_api_key = config.WEATHERAPI_KEY
        self.transitland_api_key = config.TRANSITLAND_API_KEY
        self.openweather_api_key = config.OPENWEATHER_API_KEY
        self.tomtom_api_key = config.TOMTOM_API_KEY

        # API Base URLs
        self.weather_api_base = "https://api.weatherapi.com/v1"
        self.transitland_base = "https://transit.land/api/v2"
        self.openweather_base = "https://api.openweathermap.org/data/2.5"
        self.tomtom_base = "https://api.tomtom.com"
        
    async def get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_comprehensive_weather_data(self, city: str = "Hyderabad", lat: float = 17.3850, lon: float = 78.4867) -> Dict[str, Any]:
        """Get comprehensive weather data from WeatherAPI with air quality."""
        try:
            session = await self.get_session()

            if not self.weather_api_key:
                logger.warning("WeatherAPI key not configured")
                return await self._get_fallback_weather_data()

            # WeatherAPI - Current weather + Air Quality + Forecast
            url = f"{self.weather_api_base}/current.json"
            params = {
                'key': self.weather_api_key,
                'q': f"{lat},{lon}",
                'aqi': 'yes'  # Include air quality data
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data.get('current', {})
                    location = data.get('location', {})
                    air_quality = current.get('air_quality', {})

                    # Get forecast data
                    forecast_data = await self._get_weather_forecast(lat, lon)

                    return {
                        "location": {
                            "name": location.get('name', city),
                            "region": location.get('region', ''),
                            "country": location.get('country', ''),
                            "lat": location.get('lat', lat),
                            "lon": location.get('lon', lon)
                        },
                        "current_weather": {
                            "temperature_c": current.get('temp_c'),
                            "temperature_f": current.get('temp_f'),
                            "condition": current.get('condition', {}).get('text'),
                            "humidity": current.get('humidity'),
                            "wind_kph": current.get('wind_kph'),
                            "wind_dir": current.get('wind_dir'),
                            "pressure_mb": current.get('pressure_mb'),
                            "visibility_km": current.get('vis_km'),
                            "uv_index": current.get('uv'),
                            "feels_like_c": current.get('feelslike_c')
                        },
                        "air_quality": {
                            "co": air_quality.get('co', 0),
                            "no2": air_quality.get('no2', 0),
                            "o3": air_quality.get('o3', 0),
                            "so2": air_quality.get('so2', 0),
                            "pm2_5": air_quality.get('pm2_5', 0),
                            "pm10": air_quality.get('pm10', 0),
                            "us_epa_index": air_quality.get('us-epa-index', 1),
                            "gb_defra_index": air_quality.get('gb-defra-index', 1)
                        },
                        "forecast": forecast_data,
                        "traffic_impact": self._calculate_weather_traffic_impact(current),
                        "timestamp": datetime.now().isoformat(),
                        "source": "WeatherAPI"
                    }
                else:
                    logger.warning(f"Weather API returned status {response.status}")
                    return await self._get_fallback_weather_data()

        except Exception as e:
            logger.error(f"Error fetching comprehensive weather data: {e}")
            return await self._get_fallback_weather_data()

    async def _get_weather_forecast(self, lat: float, lon: float, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast data."""
        try:
            session = await self.get_session()
            url = f"{self.weather_api_base}/forecast.json"
            params = {
                'key': self.weather_api_key,
                'q': f"{lat},{lon}",
                'days': days,
                'aqi': 'no',
                'alerts': 'yes'
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    forecast_days = []

                    for day in data['forecast']['forecastday']:
                        forecast_days.append({
                            "date": day['date'],
                            "max_temp_c": day['day']['maxtemp_c'],
                            "min_temp_c": day['day']['mintemp_c'],
                            "condition": day['day']['condition']['text'],
                            "chance_of_rain": day['day']['daily_chance_of_rain'],
                            "max_wind_kph": day['day']['maxwind_kph'],
                            "avg_humidity": day['day']['avghumidity']
                        })

                    return {
                        "days": forecast_days,
                        "alerts": data.get('alerts', {}).get('alert', [])
                    }

        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return {"days": [], "alerts": []}
    
    async def get_comprehensive_traffic_data(self, lat: float, lon: float, radius: int = 5000) -> Dict[str, Any]:
        """Get comprehensive real traffic data from TomTom API."""
        try:
            session = await self.get_session()

            if not self.tomtom_api_key:
                logger.warning("TomTom API key not configured")
                return await self._get_fallback_traffic_data()

            # Get traffic flow data
            flow_data = await self._get_tomtom_traffic_flow(lat, lon)

            # Get traffic incidents
            incidents_data = await self._get_tomtom_traffic_incidents(lat, lon, radius)

            # Calculate overall traffic score
            traffic_score = self._calculate_traffic_score(flow_data, incidents_data)

            return {
                "traffic_flow": flow_data,
                "incidents": incidents_data,
                "overall_score": traffic_score,
                "recommendations": self._generate_traffic_recommendations(traffic_score, incidents_data),
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": lat, "lon": lon},
                "source": "TomTom Traffic API"
            }

        except Exception as e:
            logger.error(f"Error fetching comprehensive traffic data: {e}")
            return await self._get_fallback_traffic_data()

    async def _get_tomtom_traffic_flow(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get traffic flow data from TomTom."""
        try:
            session = await self.get_session()
            url = f"{self.tomtom_base}/traffic/services/4/flowSegmentData/absolute/10/json"
            params = {
                'point': f"{lat},{lon}",
                'key': self.tomtom_api_key
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    flow_data = data.get('flowSegmentData', {})

                    current_speed = flow_data.get('currentSpeed', 0)
                    free_flow_speed = flow_data.get('freeFlowSpeed', 50)

                    # Calculate congestion percentage
                    congestion_ratio = 1 - (current_speed / max(free_flow_speed, 1))
                    congestion_percentage = max(0, min(100, congestion_ratio * 100))

                    return {
                        'current_speed': current_speed,
                        'free_flow_speed': free_flow_speed,
                        'congestion_percentage': round(congestion_percentage, 1),
                        'confidence': flow_data.get('confidence', 0.5),
                        'road_closure': flow_data.get('roadClosure', False),
                        'coordinates': flow_data.get('coordinates', {})
                    }
                else:
                    logger.warning(f"TomTom traffic flow API returned status {response.status}")
                    return {'current_speed': 0, 'free_flow_speed': 50, 'congestion_percentage': 0}

        except Exception as e:
            logger.error(f"Error fetching TomTom traffic flow: {e}")
            return {'current_speed': 0, 'free_flow_speed': 50, 'congestion_percentage': 0}

    async def _get_tomtom_traffic_incidents(self, lat: float, lon: float, radius: int) -> Dict[str, Any]:
        """Get traffic incidents from TomTom."""
        try:
            session = await self.get_session()
            url = f"{self.tomtom_base}/traffic/services/5/incidentDetails"
            params = {
                'bbox': f"{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}",
                'fields': 'incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code,iconCategory}}}',
                'language': 'en-US',
                'key': self.tomtom_api_key
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    incidents = []

                    for incident in data.get('incidents', []):
                        properties = incident.get('properties', {})
                        geometry = incident.get('geometry', {})

                        incidents.append({
                            'id': properties.get('id'),
                            'type': incident.get('type'),
                            'category': properties.get('iconCategory'),
                            'delay_magnitude': properties.get('magnitudeOfDelay', 0),
                            'description': self._extract_incident_description(properties.get('events', [])),
                            'coordinates': geometry.get('coordinates', []),
                            'severity': self._map_tomtom_severity(properties.get('magnitudeOfDelay', 0))
                        })

                    return {
                        'incidents': incidents,
                        'total_incidents': len(incidents)
                    }
                else:
                    logger.warning(f"TomTom incidents API returned status {response.status}")
                    return {'incidents': [], 'total_incidents': 0}

        except Exception as e:
            logger.error(f"Error fetching TomTom traffic incidents: {e}")
            return {'incidents': [], 'total_incidents': 0}

    def _extract_incident_description(self, events: List[Dict]) -> str:
        """Extract description from incident events."""
        descriptions = []
        for event in events:
            if 'description' in event:
                descriptions.append(event['description'])
        return '; '.join(descriptions) if descriptions else 'Traffic incident'

    def _map_tomtom_severity(self, magnitude: int) -> str:
        """Map TomTom delay magnitude to severity level."""
        if magnitude >= 4:
            return 'high'
        elif magnitude >= 2:
            return 'medium'
        else:
            return 'low'

    def _calculate_traffic_score(self, flow_data: Dict, incidents_data: Dict) -> int:
        """Calculate overall traffic score (0-100, higher is better)."""
        base_score = 100

        # Reduce score based on congestion
        congestion = flow_data.get('congestion_percentage', 0)
        base_score -= congestion * 0.8

        # Reduce score based on incidents
        incident_count = incidents_data.get('total_incidents', 0)
        base_score -= incident_count * 10

        return max(0, min(100, int(base_score)))

    def _generate_traffic_recommendations(self, traffic_score: int, incidents_data: Dict) -> List[str]:
        """Generate traffic recommendations based on current conditions."""
        recommendations = []

        if traffic_score < 30:
            recommendations.append("Heavy traffic detected. Consider alternative routes.")
        elif traffic_score < 60:
            recommendations.append("Moderate traffic. Allow extra travel time.")
        else:
            recommendations.append("Traffic conditions are good.")

        if incidents_data.get('total_incidents', 0) > 0:
            recommendations.append("Traffic incidents reported in the area. Check for updates.")

        return recommendations

    def _calculate_weather_traffic_impact(self, weather_data: Dict) -> Dict[str, Any]:
        """Calculate how weather affects traffic."""
        condition = weather_data.get('condition', {}).get('text', '').lower()
        visibility = weather_data.get('vis_km', 10)
        wind_speed = weather_data.get('wind_kph', 0)

        impact_score = 0
        factors = []

        # Weather condition impact
        if any(word in condition for word in ['rain', 'storm', 'snow']):
            impact_score += 30
            factors.append('Precipitation')
        elif any(word in condition for word in ['fog', 'mist']):
            impact_score += 20
            factors.append('Reduced visibility')

        # Visibility impact
        if visibility < 5:
            impact_score += 25
            factors.append('Poor visibility')
        elif visibility < 10:
            impact_score += 10
            factors.append('Limited visibility')

        # Wind impact
        if wind_speed > 50:
            impact_score += 15
            factors.append('Strong winds')

        return {
            'impact_score': min(100, impact_score),
            'impact_level': 'high' if impact_score > 50 else 'medium' if impact_score > 20 else 'low',
            'factors': factors,
            'recommendation': self._get_weather_driving_recommendation(impact_score)
        }

    def _get_weather_driving_recommendation(self, impact_score: int) -> str:
        """Get driving recommendation based on weather impact."""
        if impact_score > 50:
            return "Exercise extreme caution. Consider delaying travel if possible."
        elif impact_score > 20:
            return "Drive carefully and allow extra time for your journey."
        else:
            return "Weather conditions are favorable for driving."

    async def get_real_transit_data(self, lat: float, lon: float, radius: float = 1000) -> Dict[str, Any]:
        """Get real public transit data from Transitland API."""
        try:
            if not self.transitland_api_key:
                logger.warning("Transitland API key not configured")
                return await self._get_fallback_transit_data()

            session = await self.get_session()

            # Get nearby transit stops
            stops_data = await self._get_transitland_stops(lat, lon, radius)

            # Get transit routes
            routes_data = await self._get_transitland_routes(lat, lon, radius)

            return {
                "stops": stops_data,
                "routes": routes_data,
                "coverage_area": {
                    "center": {"lat": lat, "lon": lon},
                    "radius_meters": radius
                },
                "timestamp": datetime.now().isoformat(),
                "source": "Transitland API"
            }

        except Exception as e:
            logger.error(f"Error fetching transit data: {e}")
            return await self._get_fallback_transit_data()

    async def _get_transitland_stops(self, lat: float, lon: float, radius: float) -> List[Dict]:
        """Get transit stops from Transitland API."""
        try:
            session = await self.get_session()
            url = f"{self.transitland_base}/stops"
            params = {
                'lat': lat,
                'lon': lon,
                'radius': radius,
                'apikey': self.transitland_api_key,
                'limit': 20
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    stops = []

                    for stop in data.get('stops', []):
                        geometry = stop.get('geometry', {})
                        coordinates = geometry.get('coordinates', [])

                        stops.append({
                            'id': stop.get('onestop_id'),
                            'name': stop.get('stop_name'),
                            'coordinates': {
                                'lat': coordinates[1] if len(coordinates) > 1 else lat,
                                'lon': coordinates[0] if len(coordinates) > 0 else lon
                            },
                            'routes': stop.get('served_by_route_ids', [])
                        })

                    return stops
                else:
                    logger.warning(f"Transitland stops API returned status {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching Transitland stops: {e}")
            return []

    async def _get_transitland_routes(self, lat: float, lon: float, radius: float) -> List[Dict]:
        """Get transit routes from Transitland API."""
        try:
            session = await self.get_session()
            url = f"{self.transitland_base}/routes"
            params = {
                'lat': lat,
                'lon': lon,
                'radius': radius,
                'apikey': self.transitland_api_key,
                'limit': 10
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    routes = []

                    for route in data.get('routes', []):
                        routes.append({
                            'id': route.get('onestop_id'),
                            'name': route.get('route_long_name') or route.get('route_short_name'),
                            'type': route.get('route_type'),
                            'color': route.get('route_color'),
                            'agency': route.get('operated_by_name')
                        })

                    return routes
                else:
                    logger.warning(f"Transitland routes API returned status {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching Transitland routes: {e}")
            return []

    async def get_real_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get real air quality data from OpenWeather API."""
        try:
            if not self.openweather_api_key:
                logger.warning("OpenWeather API key not configured")
                return await self._get_fallback_air_quality()

            session = await self.get_session()
            url = f"{self.openweather_base}/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_api_key
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    air_data = data.get('list', [{}])[0]
                    main = air_data.get('main', {})
                    components = air_data.get('components', {})

                    aqi_levels = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor']
                    aqi_index = main.get('aqi', 1)

                    return {
                        'aqi': aqi_index,
                        'category': aqi_levels[aqi_index - 1] if 1 <= aqi_index <= 5 else 'Unknown',
                        'pm25': components.get('pm2_5', 0),
                        'pm10': components.get('pm10', 0),
                        'no2': components.get('no2', 0),
                        'o3': components.get('o3', 0),
                        'so2': components.get('so2', 0),
                        'co': components.get('co', 0),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'OpenWeather Air Pollution API'
                    }
                else:
                    logger.warning(f"OpenWeather air quality API returned status {response.status}")
                    return await self._get_fallback_air_quality()

        except Exception as e:
            logger.error(f"Error fetching air quality data: {e}")
            return await self._get_fallback_air_quality()

    async def get_real_emissions_data(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate real emissions data based on route information with environmental factors."""
        try:
            distance_km = route_data.get('distance_km', 0)
            duration_minutes = route_data.get('duration_minutes', 0)
            vehicle_type = route_data.get('vehicle_type', 'car')
            route_type = route_data.get('route_type', 'fastest')

            # Get current traffic and weather conditions for more accurate calculations
            lat = route_data.get('lat', 17.3850)
            lon = route_data.get('lon', 78.4867)

            # Get environmental context
            traffic_data = await self.get_comprehensive_traffic_data(lat, lon)
            weather_data = await self.get_comprehensive_weather_data(lat=lat, lon=lon)

            # Base emission factors (kg CO2 per km)
            base_emission_factors = {
                'car': 0.21,
                'bus': 0.089,
                'train': 0.041,
                'bicycle': 0.0,
                'walking': 0.0,
                'electric_car': 0.05,
                'hybrid_car': 0.12,
                'motorcycle': 0.15
            }

            base_co2_per_km = base_emission_factors.get(vehicle_type, 0.21)

            # Apply environmental adjustment factors
            adjustment_factors = self._calculate_environmental_adjustment_factors(
                traffic_data, weather_data, route_type, duration_minutes, distance_km
            )

            # Calculate adjusted emissions
            adjusted_co2_per_km = base_co2_per_km * adjustment_factors['traffic_factor'] * adjustment_factors['weather_factor']
            total_co2 = distance_km * adjusted_co2_per_km

            # Additional pollutants with environmental adjustments
            nox = total_co2 * 0.15 * adjustment_factors['traffic_factor']  # NOx increases with traffic
            pm = total_co2 * 0.05 * adjustment_factors['weather_factor']   # PM affected by weather

            # Calculate advanced eco score
            eco_score = self._calculate_advanced_eco_score_with_environment(
                total_co2, vehicle_type, adjustment_factors, distance_km, duration_minutes
            )

            return {
                'co2_kg': round(total_co2, 3),
                'nox_kg': round(nox, 3),
                'pm_kg': round(pm, 3),
                'distance_km': distance_km,
                'duration_minutes': duration_minutes,
                'vehicle_type': vehicle_type,
                'route_type': route_type,
                'base_emission_factor': base_co2_per_km,
                'adjusted_emission_factor': round(adjusted_co2_per_km, 4),
                'environmental_factors': adjustment_factors,
                'eco_score': eco_score,
                'environmental_context': {
                    'traffic_level': traffic_data.get('overall_score', 50),
                    'weather_impact': weather_data.get('traffic_impact', {}).get('impact_level', 'low'),
                    'air_quality': weather_data.get('air_quality', {}).get('us_epa_index', 2)
                },
                'recommendations': self._generate_emission_recommendations(eco_score, adjustment_factors, vehicle_type),
                'timestamp': datetime.now().isoformat(),
                'source': 'real_time_environmental_calculation'
            }

        except Exception as e:
            logger.error(f"Error calculating emissions data: {e}")
            return {
                'co2_kg': 0,
                'nox_kg': 0,
                'pm_kg': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _calculate_environmental_adjustment_factors(self, traffic_data: Dict, weather_data: Dict,
                                                  route_type: str, duration_minutes: int, distance_km: float) -> Dict[str, float]:
        """Calculate environmental adjustment factors for emissions."""
        factors = {
            'traffic_factor': 1.0,
            'weather_factor': 1.0,
            'route_factor': 1.0,
            'efficiency_factor': 1.0
        }

        # Traffic impact on emissions
        traffic_score = traffic_data.get('overall_score', 50)
        if traffic_score < 30:  # Heavy traffic
            factors['traffic_factor'] = 1.4  # 40% increase in emissions
        elif traffic_score < 60:  # Moderate traffic
            factors['traffic_factor'] = 1.2  # 20% increase
        elif traffic_score > 80:  # Light traffic
            factors['traffic_factor'] = 0.9  # 10% decrease

        # Weather impact on emissions
        weather_impact = weather_data.get('traffic_impact', {})
        impact_level = weather_impact.get('impact_level', 'low')
        if impact_level == 'high':
            factors['weather_factor'] = 1.3
        elif impact_level == 'medium':
            factors['weather_factor'] = 1.15

        # Route type impact
        if route_type == 'eco_friendly':
            factors['route_factor'] = 0.85  # Eco routes designed to reduce emissions
        elif route_type == 'shortest':
            factors['route_factor'] = 0.95  # Shorter distance = less emissions

        # Speed efficiency factor
        if duration_minutes > 0 and distance_km > 0:
            avg_speed = (distance_km / duration_minutes) * 60  # km/h
            if 50 <= avg_speed <= 80:  # Optimal speed range
                factors['efficiency_factor'] = 0.9
            elif avg_speed < 20:  # Very slow, inefficient
                factors['efficiency_factor'] = 1.3
            elif avg_speed > 100:  # Very fast, inefficient
                factors['efficiency_factor'] = 1.2

        return factors

    def _calculate_advanced_eco_score_with_environment(self, co2_emissions: float, vehicle_type: str,
                                                     factors: Dict, distance_km: float, duration_minutes: int) -> int:
        """Calculate advanced eco score considering environmental factors."""
        base_score = 100

        # Emissions penalty
        base_score -= min(co2_emissions * 15, 60)

        # Vehicle type bonus/penalty
        vehicle_bonuses = {
            'bicycle': 30, 'walking': 35, 'electric_car': 25, 'hybrid_car': 15,
            'train': 20, 'bus': 10, 'motorcycle': -5, 'car': 0
        }
        base_score += vehicle_bonuses.get(vehicle_type, 0)

        # Environmental factors penalty
        traffic_penalty = (factors['traffic_factor'] - 1.0) * 25
        weather_penalty = (factors['weather_factor'] - 1.0) * 20
        base_score -= (traffic_penalty + weather_penalty)

        # Route efficiency bonus
        route_bonus = (1.0 - factors['route_factor']) * 15
        efficiency_bonus = (1.0 - factors['efficiency_factor']) * 10
        base_score += (route_bonus + efficiency_bonus)

        # Distance consideration
        if distance_km < 5:  # Short trips
            base_score += 10
        elif distance_km > 50:  # Long trips
            base_score -= 10

        return max(0, min(100, int(base_score)))

    def _generate_emission_recommendations(self, eco_score: int, factors: Dict, vehicle_type: str) -> List[str]:
        """Generate recommendations to reduce emissions."""
        recommendations = []

        if eco_score < 40:
            recommendations.append("🚨 High emissions detected. Consider alternative transportation.")

        if factors['traffic_factor'] > 1.2:
            recommendations.append("🚦 Heavy traffic increases emissions by 20-40%. Try traveling during off-peak hours.")

        if factors['weather_factor'] > 1.1:
            recommendations.append("🌧️ Weather conditions are affecting fuel efficiency. Drive more cautiously.")

        if vehicle_type == 'car':
            recommendations.append("🚌 Consider public transport, cycling, or walking for eco-friendly alternatives.")

        if eco_score > 70:
            recommendations.append("✅ Great eco-friendly choice! You're helping reduce environmental impact.")

        return recommendations

    def _calculate_eco_score(self, co2_emissions: float, vehicle_type: str) -> int:
        """Calculate eco-friendliness score (0-100, higher is better)."""
        base_score = 100

        # Reduce score based on CO2 emissions
        base_score -= min(co2_emissions * 10, 80)

        # Bonus for eco-friendly vehicles
        eco_bonuses = {
            'bicycle': 20,
            'walking': 25,
            'electric_car': 15,
            'train': 10,
            'bus': 5
        }

        base_score += eco_bonuses.get(vehicle_type, 0)

        return max(0, min(100, int(base_score)))

    # Fallback methods
    async def _get_fallback_weather_data(self) -> Dict[str, Any]:
        """Fallback weather data when APIs are unavailable."""
        return {
            'location': {'name': 'Unknown', 'lat': 0, 'lon': 0},
            'current_weather': {
                'temperature_c': 25,
                'condition': 'Clear',
                'humidity': 60,
                'wind_kph': 10
            },
            'air_quality': {
                'pm2_5': 25,
                'pm10': 45,
                'us_epa_index': 2
            },
            'forecast': {'days': [], 'alerts': []},
            'traffic_impact': {
                'impact_score': 0,
                'impact_level': 'low',
                'factors': [],
                'recommendation': 'Weather conditions are favorable for driving.'
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data',
            'note': 'Real-time weather data unavailable'
        }

    async def _get_fallback_traffic_data(self) -> Dict[str, Any]:
        """Fallback traffic data when APIs are unavailable."""
        return {
            'traffic_flow': {
                'current_speed': 50,
                'free_flow_speed': 50,
                'congestion_percentage': 0
            },
            'incidents': {'incidents': [], 'total_incidents': 0},
            'overall_score': 80,
            'recommendations': ['Traffic data unavailable. Drive safely.'],
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data',
            'note': 'Real-time traffic data unavailable'
        }

    async def _get_fallback_transit_data(self) -> Dict[str, Any]:
        """Fallback transit data when APIs are unavailable."""
        return {
            'stops': [],
            'routes': [],
            'coverage_area': {'center': {'lat': 0, 'lon': 0}, 'radius_meters': 0},
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data',
            'note': 'Real-time transit data unavailable'
        }

    async def _get_fallback_air_quality(self) -> Dict[str, Any]:
        """Fallback air quality data when APIs are unavailable."""
        return {
            'aqi': 2,
            'category': 'Fair',
            'pm25': 25,
            'pm10': 45,
            'no2': 30,
            'o3': 80,
            'so2': 10,
            'co': 200,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data',
            'note': 'Real-time air quality data unavailable'
        }

# Global service instance
real_data_service = RealDataService()
