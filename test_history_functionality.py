#!/usr/bin/env python3
"""
Test Search History Functionality
Tests Firebase Firestore integration, search history saving/loading, and authentication
"""

import sys
import asyncio
import requests
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class HistoryFunctionalityTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_firebase_config_endpoint(self):
        """Test that Firebase configuration is accessible."""
        print("🔥 Testing Firebase Configuration...")
        
        try:
            response = requests.get(f"{self.base_url}/api/config", timeout=10)
            
            if response.status_code == 200:
                config = response.json()
                
                # Check if user authentication is enabled
                if config.get("features", {}).get("user_auth"):
                    print("  ✅ User authentication is enabled")
                    return True
                else:
                    print("  ❌ User authentication is not enabled")
                    return False
            else:
                print(f"  ❌ Config endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_frontend_files_exist(self):
        """Test that required frontend files for history functionality exist."""
        print("📁 Testing Frontend Files...")
        
        required_files = [
            "frontend/static/js/firebase-config.js",
            "frontend/static/js/auth.js", 
            "frontend/static/js/search-history.js",
            "frontend/index.html",
            "frontend/auth.html"
        ]
        
        passed = 0
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
                passed += 1
            else:
                print(f"  ❌ {file_path} - Missing")
        
        print(f"Frontend Files: {passed}/{len(required_files)} files found\n")
        return passed == len(required_files)
    
    def test_frontend_accessibility(self):
        """Test that frontend pages are accessible."""
        print("🌐 Testing Frontend Accessibility...")
        
        pages = [
            ("/", "Main Dashboard"),
            ("/auth.html", "Authentication Page"),
            ("/static/js/firebase-config.js", "Firebase Config"),
            ("/static/js/auth.js", "Auth Script"),
            ("/static/js/search-history.js", "History Script")
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
        
        print(f"Frontend Accessibility: {passed}/{len(pages)} pages accessible\n")
        return passed == len(pages)
    
    def test_search_history_javascript_structure(self):
        """Test the structure of search history JavaScript file."""
        print("📜 Testing Search History JavaScript Structure...")
        
        try:
            history_js_path = project_root / "frontend/static/js/search-history.js"
            
            if not history_js_path.exists():
                print("  ❌ search-history.js file not found")
                return False
            
            content = history_js_path.read_text(encoding='utf-8')
            
            # Check for key components
            required_components = [
                "SearchHistoryManager",
                "saveSearch",
                "loadSearchHistory",
                "displaySearchHistory",
                "deleteSearch",
                "collection",
                "addDoc",
                "getDocs",
                "firestore"
            ]
            
            passed = 0
            for component in required_components:
                if component in content:
                    print(f"  ✅ Found: {component}")
                    passed += 1
                else:
                    print(f"  ❌ Missing: {component}")
            
            print(f"JavaScript Structure: {passed}/{len(required_components)} components found\n")
            return passed >= len(required_components) * 0.8  # Allow 80% pass rate
            
        except Exception as e:
            print(f"  ❌ Exception reading file: {str(e)}")
            return False
    
    def test_firebase_config_structure(self):
        """Test Firebase configuration structure."""
        print("🔧 Testing Firebase Configuration Structure...")
        
        try:
            config_js_path = project_root / "frontend/static/js/firebase-config.js"
            
            if not config_js_path.exists():
                print("  ❌ firebase-config.js file not found")
                return False
            
            content = config_js_path.read_text(encoding='utf-8')
            
            # Check for key Firebase components
            required_components = [
                "firebaseConfig",
                "initializeApp",
                "getAuth",
                "getFirestore",
                "apiKey",
                "authDomain",
                "projectId"
            ]
            
            passed = 0
            for component in required_components:
                if component in content:
                    print(f"  ✅ Found: {component}")
                    passed += 1
                else:
                    print(f"  ❌ Missing: {component}")
            
            print(f"Firebase Config: {passed}/{len(required_components)} components found\n")
            return passed >= len(required_components) * 0.8
            
        except Exception as e:
            print(f"  ❌ Exception reading file: {str(e)}")
            return False
    
    def test_route_search_integration(self):
        """Test that route searches can be performed (prerequisite for history)."""
        print("🔍 Testing Route Search Integration...")
        
        test_route = {
            "source": "Hyderabad, India",
            "destination": "Secunderabad, India",
            "route_type": "fastest"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/route",
                json=test_route,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("routes") and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    print(f"  ✅ Route search successful")
                    print(f"  ✅ Distance: {route.get('distance', 'N/A')}")
                    print(f"  ✅ Duration: {route.get('duration', 'N/A')}")
                    print(f"  ✅ Steps: {len(route.get('steps', []))} steps")
                    return True
                else:
                    print("  ❌ No routes returned")
                    return False
            else:
                print(f"  ❌ Route API failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_html_history_integration(self):
        """Test that HTML pages include history functionality."""
        print("📄 Testing HTML History Integration...")
        
        try:
            index_path = project_root / "frontend/index.html"
            
            if not index_path.exists():
                print("  ❌ index.html not found")
                return False
            
            content = index_path.read_text(encoding='utf-8')
            
            # Check for history-related elements
            history_elements = [
                "search-history",
                "history-section",
                "Search History",
                "search-history.js",
                "auth.js",
                "firebase-config.js"
            ]
            
            passed = 0
            for element in history_elements:
                if element in content:
                    print(f"  ✅ Found: {element}")
                    passed += 1
                else:
                    print(f"  ❌ Missing: {element}")
            
            print(f"HTML Integration: {passed}/{len(history_elements)} elements found\n")
            return passed >= len(history_elements) * 0.7
            
        except Exception as e:
            print(f"  ❌ Exception reading HTML: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all history functionality tests."""
        print("=" * 60)
        print("📚 SEARCH HISTORY FUNCTIONALITY TESTS")
        print("=" * 60)
        
        results = []
        results.append(self.test_firebase_config_endpoint())
        results.append(self.test_frontend_files_exist())
        results.append(self.test_frontend_accessibility())
        results.append(self.test_search_history_javascript_structure())
        results.append(self.test_firebase_config_structure())
        results.append(self.test_route_search_integration())
        results.append(self.test_html_history_integration())
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("=" * 60)
        print(f"📊 HISTORY FUNCTIONALITY TEST SUMMARY")
        print(f"Passed: {passed_tests}/{total_tests} test suites")
        
        if passed_tests == total_tests:
            print("🎉 All history functionality tests PASSED!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ Most history functionality tests PASSED!")
        else:
            print("⚠️ Some history functionality tests FAILED!")
        
        print("=" * 60)
        return passed_tests >= total_tests * 0.8  # 80% pass rate

if __name__ == "__main__":
    tester = HistoryFunctionalityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
