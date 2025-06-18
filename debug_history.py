#!/usr/bin/env python3
"""
Debug Search History Issues
Comprehensive debugging to identify why search history is not showing in the frontend
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

class HistoryDebugger:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_server_status(self):
        """Test that the server is running and accessible."""
        print("🔍 Testing Server Status...")
        
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
    
    def test_frontend_files(self):
        """Test that all required frontend files are accessible."""
        print("📁 Testing Frontend Files...")
        
        files_to_check = [
            ("/", "Main Page"),
            ("/auth.html", "Authentication Page"),
            ("/static/js/firebase-config.js", "Firebase Config"),
            ("/static/js/auth.js", "Authentication Script"),
            ("/static/js/search-history.js", "Search History Script"),
            ("/static/js/main.js", "Main Application Script"),
            ("/static/css/style.css", "Stylesheet")
        ]
        
        passed = 0
        for path, name in files_to_check:
            try:
                response = requests.get(f"{self.base_url}{path}", timeout=10)
                
                if response.status_code == 200:
                    print(f"  ✅ {name}: Accessible")
                    passed += 1
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {name}: Exception - {str(e)}")
        
        print(f"Frontend Files: {passed}/{len(files_to_check)} accessible\n")
        return passed == len(files_to_check)
    
    def test_html_structure(self):
        """Test that the HTML has the correct structure for history."""
        print("🏗️ Testing HTML Structure...")
        
        try:
            response = requests.get(f"{self.base_url}/dashboard.html", timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Check for required elements
                required_elements = [
                    'id="history-section"',
                    'id="search-history"',
                    'data-section="history"',
                    'search-history.js',
                    'auth.js',
                    'firebase-config.js'
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in html_content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    print("  ✅ All required HTML elements found")
                    return True
                else:
                    print(f"  ❌ Missing HTML elements: {missing_elements}")
                    return False
            else:
                print(f"  ❌ Could not fetch dashboard page: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_javascript_modules(self):
        """Test that JavaScript modules are properly structured."""
        print("📜 Testing JavaScript Modules...")
        
        try:
            # Test search-history.js
            response = requests.get(f"{self.base_url}/static/js/search-history.js", timeout=10)
            
            if response.status_code == 200:
                js_content = response.text
                
                # Check for key components
                required_components = [
                    'class SearchHistoryManager',
                    'loadSearchHistory',
                    'displaySearchHistory',
                    'saveSearch',
                    'getElementById(\'search-history\')',
                    'export default searchHistoryManager'
                ]
                
                missing_components = []
                for component in required_components:
                    if component not in js_content:
                        missing_components.append(component)
                
                if not missing_components:
                    print("  ✅ Search history JavaScript structure is correct")
                    
                    # Check for potential issues
                    issues = []
                    if 'console.log' not in js_content:
                        issues.append("No debug logging found")
                    if 'getElementById(\'search-history\')' not in js_content:
                        issues.append("Missing search-history element reference")
                    
                    if issues:
                        print(f"  ⚠️ Potential issues: {issues}")
                    
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
    
    def test_route_search_and_save(self):
        """Test that route searches work and can be saved."""
        print("🛣️ Testing Route Search and Save...")
        
        test_route = {
            "source": "Hyderabad Railway Station",
            "destination": "Charminar, Hyderabad",
            "route_type": "fastest"
        }
        
        try:
            print("  🔍 Performing test route search...")
            response = requests.post(
                f"{self.base_url}/api/route",
                json=test_route,
                timeout=30
            )
            
            if response.status_code == 200:
                route_data = response.json()
                print(f"    ✅ Route search successful")
                
                if route_data.get("routes") and len(route_data["routes"]) > 0:
                    route = route_data["routes"][0]
                    print(f"    📍 Route: {test_route['source']} → {test_route['destination']}")
                    print(f"    📏 Distance: {route.get('distance', 'N/A')}")
                    print(f"    ⏱️ Duration: {route.get('duration', 'N/A')}")
                    
                    # Check if route has all required fields for history saving
                    required_fields = ['distance', 'duration']
                    missing_fields = [field for field in required_fields if not route.get(field)]
                    
                    if not missing_fields:
                        print(f"    ✅ Route has all required fields for history saving")
                        return True
                    else:
                        print(f"    ❌ Missing required fields: {missing_fields}")
                        return False
                else:
                    print(f"    ❌ No routes returned")
                    return False
            else:
                print(f"    ❌ Route search failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def open_browser_with_debug_console(self):
        """Open the application in browser with instructions for debugging."""
        print("🌐 Opening Application for Manual Debugging...")
        
        try:
            webbrowser.open(f"{self.base_url}/auth.html")
            print(f"  ✅ Application opened at: {self.base_url}/auth.html")
            print("\n  🔍 DEBUGGING CHECKLIST:")
            print("     1. Open Browser Developer Tools (F12)")
            print("     2. Go to Console tab")
            print("     3. Sign in with your Google account")
            print("     4. Look for any JavaScript errors in console")
            print("     5. Perform a route search")
            print("     6. Check console for history-related messages:")
            print("        - 'Search record to save:'")
            print("        - 'Search saved successfully with ID:'")
            print("        - 'Loading search history for user:'")
            print("        - 'Successfully loaded X search history items'")
            print("     7. Click on History tab")
            print("     8. Check if 'History tab clicked, loading search history' appears")
            print("     9. Look for any Firebase/Firestore errors")
            print("     10. Check Network tab for failed requests")
            
            print("\n  🚨 COMMON ISSUES TO CHECK:")
            print("     • Firebase authentication not working")
            print("     • Firestore security rules blocking reads/writes")
            print("     • JavaScript module import errors")
            print("     • Missing HTML elements (search-history div)")
            print("     • Console errors about undefined variables")
            print("     • Network errors when accessing Firebase")
            
            print("\n  📝 SPECIFIC THINGS TO VERIFY:")
            print("     • User object is not null after sign-in")
            print("     • searchHistoryManager is defined globally")
            print("     • getElementById('search-history') returns an element")
            print("     • Firebase config is loaded correctly")
            print("     • No CORS errors in network tab")
            
            return True
        except Exception as e:
            print(f"  ❌ Could not open browser: {str(e)}")
            return False
    
    def run_debug_analysis(self):
        """Run comprehensive debugging analysis."""
        print("=" * 60)
        print("🔍 SEARCH HISTORY DEBUG ANALYSIS")
        print("=" * 60)
        
        results = []
        results.append(self.test_server_status())
        results.append(self.test_frontend_files())
        results.append(self.test_html_structure())
        results.append(self.test_javascript_modules())
        results.append(self.test_route_search_and_save())
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("=" * 60)
        print(f"📊 DEBUG ANALYSIS SUMMARY")
        print(f"Passed: {passed_tests}/{total_tests} checks")
        
        if passed_tests == total_tests:
            print("✅ All backend components are working correctly!")
            print("🔍 The issue is likely in the frontend JavaScript or Firebase configuration.")
            print("📝 Recommended next steps:")
            print("   1. Check browser console for JavaScript errors")
            print("   2. Verify Firebase authentication is working")
            print("   3. Check Firestore security rules")
            print("   4. Ensure user is properly authenticated before loading history")
        else:
            print("⚠️ Some backend components have issues!")
            print("🔧 Fix the failing checks before debugging frontend issues.")
        
        print("=" * 60)
        
        # Open browser for manual debugging
        self.open_browser_with_debug_console()
        
        return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    debugger = HistoryDebugger()
    success = debugger.run_debug_analysis()
    sys.exit(0 if success else 1)
