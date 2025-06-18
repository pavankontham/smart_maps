#!/usr/bin/env python3
"""
Test Distance Calculations and Route Parsing
Tests the accuracy of distance extraction, duration parsing, and route calculations
"""

import sys
import asyncio
import requests
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.google_maps import GoogleMapsService
from backend.models.schemas import RouteRequest, RouteType

class DistanceCalculationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.google_maps_service = GoogleMapsService()
        
    def test_distance_extraction(self):
        """Test distance extraction from various text formats."""
        print("🧮 Testing Distance Extraction...")
        
        test_cases = [
            ("5.2 km", 5.2),
            ("10.7 km", 10.7),
            ("3.2 mi", 5.15),  # Should convert to km
            ("15 km", 15.0),
            ("0.8 km", 0.8),
            ("25.3 km", 25.3),
            ("invalid", 0.0)  # Should handle invalid input
        ]
        
        passed = 0
        for distance_text, expected in test_cases:
            result = self.google_maps_service._extract_distance_km(distance_text)
            if abs(result - expected) < 0.1:  # Allow small floating point differences
                print(f"  ✅ '{distance_text}' -> {result} km (expected {expected})")
                passed += 1
            else:
                print(f"  ❌ '{distance_text}' -> {result} km (expected {expected})")
        
        print(f"Distance Extraction: {passed}/{len(test_cases)} tests passed\n")
        return passed == len(test_cases)
    
    def test_duration_parsing(self):
        """Test duration parsing from various text formats."""
        print("⏱️ Testing Duration Parsing...")
        
        test_cases = [
            ("15 mins", 15),
            ("1 hour 30 mins", 90),
            ("2 hours 15 mins", 135),
            ("45 mins", 45),
            ("1 hour", 60),
            ("3 hours", 180),
            ("invalid", 0)  # Should handle invalid input
        ]
        
        passed = 0
        for duration_text, expected in test_cases:
            result = self.google_maps_service._parse_duration_minutes(duration_text)
            if result == expected:
                print(f"  ✅ '{duration_text}' -> {result} minutes (expected {expected})")
                passed += 1
            else:
                print(f"  ❌ '{duration_text}' -> {result} minutes (expected {expected})")
        
        print(f"Duration Parsing: {passed}/{len(test_cases)} tests passed\n")
        return passed == len(test_cases)
    
    def test_route_api_endpoint(self):
        """Test the route API endpoint with real requests."""
        print("🛣️ Testing Route API Endpoint...")
        
        test_routes = [
            {
                "source": "Hyderabad, India",
                "destination": "Secunderabad, India",
                "route_type": "fastest"
            },
            {
                "source": "HITEC City, Hyderabad",
                "destination": "Charminar, Hyderabad",
                "route_type": "eco_friendly"
            },
            {
                "source": "Banjara Hills, Hyderabad",
                "destination": "Gachibowli, Hyderabad", 
                "route_type": "shortest"
            }
        ]
        
        passed = 0
        for i, route_data in enumerate(test_routes, 1):
            try:
                print(f"  Testing Route {i}: {route_data['source']} -> {route_data['destination']}")
                
                response = requests.post(
                    f"{self.base_url}/api/route",
                    json=route_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("routes") and len(data["routes"]) > 0:
                        route = data["routes"][0]
                        
                        # Validate required fields
                        required_fields = ["distance", "duration", "steps"]
                        missing_fields = [field for field in required_fields if field not in route]
                        
                        if not missing_fields:
                            print(f"    ✅ Distance: {route['distance']}")
                            print(f"    ✅ Duration: {route['duration']}")
                            print(f"    ✅ Steps: {len(route['steps'])} steps")
                            
                            # Check eco metrics for eco-friendly routes
                            if route_data["route_type"] == "eco_friendly":
                                if "carbon_estimate_kg" in route and "eco_score" in route:
                                    print(f"    ✅ Carbon Estimate: {route['carbon_estimate_kg']} kg")
                                    print(f"    ✅ Eco Score: {route['eco_score']}")
                                else:
                                    print(f"    ⚠️ Missing eco metrics")
                            
                            passed += 1
                        else:
                            print(f"    ❌ Missing fields: {missing_fields}")
                    else:
                        print(f"    ❌ No routes returned")
                else:
                    print(f"    ❌ API Error: {response.status_code}")
                    print(f"    Response: {response.text}")
                    
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
            
            print()
        
        print(f"Route API Tests: {passed}/{len(test_routes)} tests passed\n")
        return passed == len(test_routes)
    
    def test_carbon_calculations(self):
        """Test carbon emission calculations for different route types."""
        print("🌱 Testing Carbon Emission Calculations...")
        
        # Test with mock route data
        from backend.models.schemas import RouteInfo, RouteStep, Coordinates
        
        mock_route = RouteInfo(
            distance="10.5 km",
            duration="25 mins",
            duration_in_traffic="30 mins",
            steps=[],
            polyline="mock_polyline",
            bounds={}
        )
        
        test_cases = [
            (RouteType.ECO_FRIENDLY, "eco-friendly"),
            (RouteType.FASTEST, "fastest"),
            (RouteType.SHORTEST, "shortest")
        ]
        
        passed = 0
        for route_type, type_name in test_cases:
            try:
                if route_type == RouteType.ECO_FRIENDLY:
                    result = self.google_maps_service._add_eco_metrics(mock_route)
                elif route_type == RouteType.FASTEST:
                    result = self.google_maps_service._add_fastest_metrics(mock_route)
                else:  # SHORTEST
                    result = self.google_maps_service._add_shortest_metrics(mock_route)
                
                if hasattr(result, 'carbon_estimate_kg') and hasattr(result, 'eco_score'):
                    carbon = result.carbon_estimate_kg
                    eco_score = result.eco_score
                    
                    # Validate reasonable ranges
                    if 0 < carbon < 50 and 0 <= eco_score <= 100:
                        print(f"  ✅ {type_name.title()} Route:")
                        print(f"    Carbon: {carbon} kg CO2")
                        print(f"    Eco Score: {eco_score}/100")
                        passed += 1
                    else:
                        print(f"  ❌ {type_name.title()} Route: Invalid values")
                        print(f"    Carbon: {carbon}, Eco Score: {eco_score}")
                else:
                    print(f"  ❌ {type_name.title()} Route: Missing carbon metrics")
                    
            except Exception as e:
                print(f"  ❌ {type_name.title()} Route: Exception - {str(e)}")
        
        print(f"Carbon Calculation Tests: {passed}/{len(test_cases)} tests passed\n")
        return passed == len(test_cases)
    
    def run_all_tests(self):
        """Run all distance calculation tests."""
        print("=" * 60)
        print("🧪 DISTANCE CALCULATION TESTS")
        print("=" * 60)
        
        results = []
        results.append(self.test_distance_extraction())
        results.append(self.test_duration_parsing())
        results.append(self.test_route_api_endpoint())
        results.append(self.test_carbon_calculations())
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("=" * 60)
        print(f"📊 DISTANCE CALCULATION TEST SUMMARY")
        print(f"Passed: {passed_tests}/{total_tests} test suites")
        
        if passed_tests == total_tests:
            print("🎉 All distance calculation tests PASSED!")
        else:
            print("⚠️ Some distance calculation tests FAILED!")
        
        print("=" * 60)
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = DistanceCalculationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
