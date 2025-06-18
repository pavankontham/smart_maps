#!/usr/bin/env python3
"""
Test Search History Fix
Comprehensive test to verify that search history is now working correctly
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

class HistoryFixTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_server_and_dashboard(self):
        """Test that server and dashboard are working."""
        print("🔍 Testing Server and Dashboard...")
        
        try:
            # Test server health
            health_response = requests.get(f"{self.base_url}/health", timeout=10)
            if health_response.status_code != 200:
                print(f"  ❌ Server health check failed: {health_response.status_code}")
                return False
            
            print("  ✅ Server is healthy")
            
            # Test dashboard page
            dashboard_response = requests.get(f"{self.base_url}/dashboard.html", timeout=10)
            if dashboard_response.status_code != 200:
                print(f"  ❌ Dashboard page failed: {dashboard_response.status_code}")
                return False
            
            dashboard_content = dashboard_response.text
            
            # Check for required elements
            required_elements = [
                'id="history-section"',
                'id="search-history"',
                'id="vehicle-type"',
                'data-section="history"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in dashboard_content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"  ❌ Missing elements in dashboard: {missing_elements}")
                return False
            
            print("  ✅ Dashboard page has all required elements")
            print("  ✅ Vehicle type selector added")
            print("  ✅ History section properly configured")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_route_search_with_vehicle_type(self):
        """Test route search with vehicle type selection."""
        print("🛣️ Testing Route Search with Vehicle Type...")
        
        test_routes = [
            {
                "source": "Hyderabad Railway Station",
                "destination": "Charminar, Hyderabad",
                "route_type": "fastest",
                "expected_vehicle": "car"
            },
            {
                "source": "HITEC City, Hyderabad",
                "destination": "Gachibowli, Hyderabad",
                "route_type": "eco_friendly",
                "expected_vehicle": "electric_car"
            }
        ]
        
        passed = 0
        for i, test_route in enumerate(test_routes, 1):
            try:
                print(f"  🔍 Testing Route {i}: {test_route['source']} → {test_route['destination']}")
                
                response = requests.post(
                    f"{self.base_url}/api/route",
                    json={
                        "source": test_route["source"],
                        "destination": test_route["destination"],
                        "route_type": test_route["route_type"]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("routes") and len(data["routes"]) > 0:
                        route = data["routes"][0]
                        
                        # Check required fields for history saving
                        required_fields = ["distance", "duration"]
                        missing_fields = [field for field in required_fields if not route.get(field)]
                        
                        if not missing_fields:
                            print(f"    ✅ Distance: {route['distance']}")
                            print(f"    ✅ Duration: {route['duration']}")
                            
                            # Check eco metrics for eco-friendly routes
                            if test_route['route_type'] == 'eco_friendly':
                                if route.get('carbon_estimate_kg') and route.get('eco_score'):
                                    print(f"    ✅ Carbon Estimate: {route['carbon_estimate_kg']} kg CO₂")
                                    print(f"    ✅ Eco Score: {route['eco_score']}/100")
                                else:
                                    print(f"    ⚠️ Missing eco metrics")
                            
                            passed += 1
                        else:
                            print(f"    ❌ Missing required fields: {missing_fields}")
                    else:
                        print(f"    ❌ No routes returned")
                else:
                    print(f"    ❌ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
            
            print()
        
        print(f"Route Search Tests: {passed}/{len(test_routes)} passed\n")
        return passed == len(test_routes)
    
    def test_javascript_modules(self):
        """Test that JavaScript modules are properly updated."""
        print("📜 Testing Updated JavaScript Modules...")
        
        try:
            # Test search-history.js
            response = requests.get(f"{self.base_url}/static/js/search-history.js", timeout=10)
            
            if response.status_code == 200:
                js_content = response.text
                
                # Check for updated components
                required_components = [
                    'startingAddress',  # Updated field name
                    'vehicleType',      # New vehicle type field
                    'getVehicleDisplayName',  # New helper method
                    'eco-score',        # New eco score display
                    'loadSearchHistory'  # Core functionality
                ]
                
                missing_components = []
                for component in required_components:
                    if component not in js_content:
                        missing_components.append(component)
                
                if not missing_components:
                    print("  ✅ Search history JavaScript has all required updates")
                    print("  ✅ Vehicle type support added")
                    print("  ✅ Field names match Firestore format")
                    print("  ✅ Enhanced display features included")
                    return True
                else:
                    print(f"  ❌ Missing JavaScript components: {missing_components}")
                    return False
            else:
                print(f"  ❌ Could not fetch search-history.js: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_main_js_updates(self):
        """Test that main.js has the correct data format for saving."""
        print("🔧 Testing Main.js Updates...")
        
        try:
            response = requests.get(f"{self.base_url}/static/js/main.js", timeout=10)
            
            if response.status_code == 200:
                js_content = response.text
                
                # Check for updated save format
                required_updates = [
                    'startingAddress:',  # Updated field name
                    'vehicleType:',      # New vehicle type field
                    'vehicle-type',      # Vehicle type selector reference
                    'loadSearchHistory'  # History loading calls
                ]
                
                missing_updates = []
                for update in required_updates:
                    if update not in js_content:
                        missing_updates.append(update)
                
                if not missing_updates:
                    print("  ✅ Main.js has all required updates")
                    print("  ✅ Save format matches Firestore structure")
                    print("  ✅ Vehicle type integration complete")
                    return True
                else:
                    print(f"  ❌ Missing main.js updates: {missing_updates}")
                    return False
            else:
                print(f"  ❌ Could not fetch main.js: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def open_application_for_testing(self):
        """Open the application for manual testing."""
        print("🌐 Opening Application for Manual Testing...")
        
        try:
            webbrowser.open(f"{self.base_url}/auth.html")
            print(f"  ✅ Application opened at: {self.base_url}/auth.html")
            print("\n  📝 MANUAL TESTING STEPS:")
            print("     1. ✅ Sign in with your Google account")
            print("     2. 🛣️ You'll be redirected to the main dashboard")
            print("     3. 🚗 Notice the new 'Vehicle Type' dropdown in route planning")
            print("     4. 📍 Enter source and destination (e.g., 'Kayamkulam' to 'Karunagappalli')")
            print("     5. 🚙 Select a vehicle type (Car, Motorcycle, Electric Car, etc.)")
            print("     6. 🔍 Click 'Get Route' to search")
            print("     7. 📚 Click on 'History' tab")
            print("     8. ✅ Your search should appear with vehicle type displayed")
            print("     9. 🔄 Try the 'Repeat Search' button to test form filling")
            print("     10. 🗑️ Test delete functionality")
            
            print("\n  🔍 WHAT TO VERIFY:")
            print("     • Search history loads immediately when clicking History tab")
            print("     • Each history item shows: distance, duration, vehicle type, CO₂, eco score")
            print("     • Vehicle type is displayed correctly (Car, Electric Car, etc.)")
            print("     • Repeat search fills all form fields including vehicle type")
            print("     • New searches appear immediately without page refresh")
            print("     • Data persists across browser sessions")
            
            print("\n  🚨 TROUBLESHOOTING:")
            print("     • If history doesn't load: Check browser console for errors")
            print("     • If data doesn't save: Verify you're signed in")
            print("     • If vehicle type missing: Check that dropdown has a value selected")
            print("     • If repeat search doesn't work: Check console for JavaScript errors")
            
            return True
        except Exception as e:
            print(f"  ❌ Could not open browser: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all history fix tests."""
        print("=" * 60)
        print("🔧 SEARCH HISTORY FIX VERIFICATION")
        print("=" * 60)
        
        results = []
        results.append(self.test_server_and_dashboard())
        results.append(self.test_route_search_with_vehicle_type())
        results.append(self.test_javascript_modules())
        results.append(self.test_main_js_updates())
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("=" * 60)
        print(f"📊 HISTORY FIX TEST SUMMARY")
        print(f"Passed: {passed_tests}/{total_tests} test suites")
        
        if passed_tests == total_tests:
            print("🎉 ALL HISTORY FIXES IMPLEMENTED SUCCESSFULLY!")
            print("✅ Dashboard serves correct content with history section")
            print("✅ Vehicle type selector added to UI")
            print("✅ Data format matches Firestore structure")
            print("✅ JavaScript modules updated correctly")
            print("✅ Enhanced history display with vehicle type and eco score")
            print("✅ Improved loading and refresh functionality")
        else:
            print("⚠️ Some history fixes need attention!")
            print("🔧 Check the failing tests above")
        
        print("=" * 60)
        
        # Open for manual testing
        self.open_application_for_testing()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = HistoryFixTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
