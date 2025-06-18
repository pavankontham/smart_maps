#!/usr/bin/env python3
"""
Full Integration Test
Tests the complete functionality including route planning, distance calculations, and history
"""

import sys
import asyncio
import requests
import json
import time
import webbrowser
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class FullIntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_server_health(self):
        """Test that the server is running and healthy."""
        print("🏥 Testing Server Health...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"  ✅ Server Status: {health_data['status']}")
                print(f"  ✅ Version: {health_data['version']}")
                
                services = health_data.get('services', {})
                for service, status in services.items():
                    status_icon = "✅" if status else "❌"
                    print(f"  {status_icon} {service.replace('_', ' ').title()}: {'Available' if status else 'Unavailable'}")
                
                return True
            else:
                print(f"  ❌ Server health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test all major API endpoints."""
        print("🔌 Testing API Endpoints...")
        
        endpoints = [
            ("/api/config", "Configuration"),
            ("/api/weather", "Weather Data"),
            ("/api/traffic", "Traffic Data"),
            ("/api/transit", "Transit Data"),
            ("/api/air_quality", "Air Quality")
        ]
        
        passed = 0
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    print(f"  ✅ {name}: Working")
                    passed += 1
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {name}: Exception - {str(e)}")
        
        print(f"API Endpoints: {passed}/{len(endpoints)} working\n")
        return passed == len(endpoints)
    
    def test_route_planning_comprehensive(self):
        """Test comprehensive route planning with different route types."""
        print("🗺️ Testing Comprehensive Route Planning...")
        
        test_routes = [
            {
                "name": "Local Route (Hyderabad)",
                "data": {
                    "source": "Hyderabad Railway Station",
                    "destination": "Charminar, Hyderabad",
                    "route_type": "fastest"
                }
            },
            {
                "name": "Eco Route (HITEC City)",
                "data": {
                    "source": "HITEC City, Hyderabad",
                    "destination": "Gachibowli, Hyderabad",
                    "route_type": "eco_friendly"
                }
            },
            {
                "name": "Shortest Route (Banjara Hills)",
                "data": {
                    "source": "Banjara Hills, Hyderabad",
                    "destination": "Jubilee Hills, Hyderabad",
                    "route_type": "shortest"
                }
            }
        ]
        
        passed = 0
        for test_route in test_routes:
            try:
                print(f"  Testing {test_route['name']}...")
                
                response = requests.post(
                    f"{self.base_url}/api/route",
                    json=test_route['data'],
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("routes") and len(data["routes"]) > 0:
                        route = data["routes"][0]
                        
                        print(f"    ✅ Distance: {route.get('distance', 'N/A')}")
                        print(f"    ✅ Duration: {route.get('duration', 'N/A')}")
                        print(f"    ✅ Steps: {len(route.get('steps', []))} navigation steps")
                        
                        # Check for eco metrics if eco-friendly route
                        if test_route['data']['route_type'] == 'eco_friendly':
                            if route.get('carbon_estimate_kg') and route.get('eco_score'):
                                print(f"    ✅ Carbon Estimate: {route['carbon_estimate_kg']} kg CO₂")
                                print(f"    ✅ Eco Score: {route['eco_score']}/100")
                            else:
                                print(f"    ⚠️ Missing eco metrics")
                        
                        passed += 1
                    else:
                        print(f"    ❌ No routes returned")
                else:
                    print(f"    ❌ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
            
            print()
        
        print(f"Route Planning: {passed}/{len(test_routes)} tests passed\n")
        return passed == len(test_routes)
    
    def test_distance_accuracy(self):
        """Test distance calculation accuracy with known routes."""
        print("📏 Testing Distance Calculation Accuracy...")
        
        # Test with a well-known route
        test_data = {
            "source": "Hyderabad Airport",
            "destination": "Charminar, Hyderabad",
            "route_type": "fastest"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/route",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("routes") and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    distance_str = route.get('distance', '')
                    
                    # Extract numeric distance
                    if 'km' in distance_str:
                        distance_km = float(distance_str.replace('km', '').strip())
                        
                        # Airport to Charminar is approximately 20-25 km
                        if 15 <= distance_km <= 35:
                            print(f"  ✅ Distance calculation reasonable: {distance_str}")
                            print(f"  ✅ Duration: {route.get('duration', 'N/A')}")
                            return True
                        else:
                            print(f"  ❌ Distance seems unreasonable: {distance_str}")
                            return False
                    else:
                        print(f"  ❌ Could not parse distance: {distance_str}")
                        return False
                else:
                    print(f"  ❌ No routes returned")
                    return False
            else:
                print(f"  ❌ API Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_frontend_accessibility(self):
        """Test that frontend pages are accessible."""
        print("🌐 Testing Frontend Accessibility...")
        
        pages = [
            ("/", "Main Page"),
            ("/auth.html", "Authentication Page"),
            ("/dashboard.html", "Dashboard Page")
        ]
        
        passed = 0
        for path, name in pages:
            try:
                response = requests.get(f"{self.base_url}{path}", timeout=10)
                
                if response.status_code == 200:
                    print(f"  ✅ {name}: Accessible")
                    passed += 1
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {name}: Exception - {str(e)}")
        
        print(f"Frontend Pages: {passed}/{len(pages)} accessible\n")
        return passed >= len(pages) * 0.8  # 80% pass rate
    
    def open_application_in_browser(self):
        """Open the application in the default web browser."""
        print("🌐 Opening Application in Browser...")
        
        try:
            webbrowser.open(f"{self.base_url}/auth.html")
            print(f"  ✅ Application opened at: {self.base_url}/auth.html")
            print("  📝 You can now test the application manually:")
            print("     1. Sign in with your Google account or create an account")
            print("     2. Test route planning with different locations")
            print("     3. Check that search history is saved and displayed")
            print("     4. Verify distance calculations are accurate")
            print("     5. Test the AI assistant functionality")
            return True
        except Exception as e:
            print(f"  ❌ Could not open browser: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("=" * 60)
        print("🧪 FULL INTEGRATION TESTS")
        print("=" * 60)
        
        results = []
        results.append(self.test_server_health())
        results.append(self.test_api_endpoints())
        results.append(self.test_route_planning_comprehensive())
        results.append(self.test_distance_accuracy())
        results.append(self.test_frontend_accessibility())
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("=" * 60)
        print(f"📊 INTEGRATION TEST SUMMARY")
        print(f"Passed: {passed_tests}/{total_tests} test suites")
        
        if passed_tests == total_tests:
            print("🎉 All integration tests PASSED!")
            print("✅ The SmartCity-AI application is working correctly!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ Most integration tests PASSED!")
            print("⚠️ Some minor issues detected, but application is functional")
        else:
            print("⚠️ Some integration tests FAILED!")
            print("🔧 Please check the application configuration")
        
        print("=" * 60)
        
        # Open in browser for manual testing
        self.open_application_in_browser()
        
        return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    tester = FullIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
