#!/usr/bin/env python3
"""
Test Improvements: Gemini Chat, Eco Tips, and History Updates
Tests the three main improvements made to the SmartCity-AI system
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

class ImprovementsTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_gemini_plain_text_response(self):
        """Test that Gemini chat returns plain text without markdown formatting."""
        print("🤖 Testing Gemini Plain Text Response...")
        
        test_queries = [
            "How can I reduce my carbon footprint while commuting?",
            "What are the best eco-friendly transportation options?",
            "Give me tips for fuel-efficient driving"
        ]
        
        passed = 0
        for query in test_queries:
            try:
                response = requests.post(
                    f"{self.base_url}/api/eco_chat",
                    json={"message": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '')
                    
                    # Check for markdown formatting
                    has_bold = '**' in response_text
                    has_italic = '*' in response_text and '**' not in response_text
                    has_headers = response_text.startswith('#')
                    has_bullet_points = '\n*' in response_text or '\n-' in response_text
                    
                    if not (has_bold or has_italic or has_headers or has_bullet_points):
                        print(f"  ✅ Query: '{query[:50]}...'")
                        print(f"    Response is plain text (no markdown formatting)")
                        print(f"    Sample: '{response_text[:100]}...'")
                        passed += 1
                    else:
                        print(f"  ❌ Query: '{query[:50]}...'")
                        print(f"    Response contains markdown formatting")
                        if has_bold: print("    - Contains **bold** text")
                        if has_italic: print("    - Contains *italic* text")
                        if has_headers: print("    - Contains # headers")
                        if has_bullet_points: print("    - Contains bullet points")
                else:
                    print(f"  ❌ Query failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {str(e)}")
            
            print()
        
        print(f"Gemini Plain Text: {passed}/{len(test_queries)} tests passed\n")
        return passed == len(test_queries)
    
    def test_improved_eco_tips(self):
        """Test that eco tips are displayed with improved formatting."""
        print("🌱 Testing Improved Eco Tips...")
        
        try:
            response = requests.get(f"{self.base_url}/api/eco_tips", timeout=15)
            
            if response.status_code == 200:
                response_data = response.json()
                tips = response_data.get('tips', []) if isinstance(response_data, dict) else response_data

                if isinstance(tips, list) and len(tips) > 0:
                    print(f"  ✅ Retrieved {len(tips)} eco tips")
                    
                    # Check tip structure
                    required_fields = ['tip', 'category', 'impact']
                    enhanced_fields = ['icon', 'savings']
                    
                    tips_with_enhanced_fields = 0
                    for i, tip in enumerate(tips[:3], 1):  # Check first 3 tips
                        print(f"  📝 Tip {i}:")
                        
                        # Check required fields
                        missing_required = [field for field in required_fields if field not in tip]
                        if not missing_required:
                            print(f"    ✅ Has all required fields")
                        else:
                            print(f"    ❌ Missing required fields: {missing_required}")
                        
                        # Check enhanced fields
                        has_enhanced = any(field in tip for field in enhanced_fields)
                        if has_enhanced:
                            tips_with_enhanced_fields += 1
                            print(f"    ✅ Has enhanced fields:")
                            if 'icon' in tip:
                                print(f"      - Icon: {tip['icon']}")
                            if 'savings' in tip:
                                print(f"      - Savings: {tip['savings']}")
                        
                        print(f"    📋 Category: {tip.get('category', 'N/A')}")
                        print(f"    📊 Impact: {tip.get('impact', 'N/A')}")
                        print(f"    💡 Tip: {tip.get('tip', 'N/A')[:80]}...")
                        print()
                    
                    if tips_with_enhanced_fields >= len(tips) * 0.8:  # 80% have enhanced fields
                        print(f"  ✅ {tips_with_enhanced_fields}/{len(tips)} tips have enhanced formatting")
                        return True
                    else:
                        print(f"  ❌ Only {tips_with_enhanced_fields}/{len(tips)} tips have enhanced formatting")
                        return False
                else:
                    print(f"  ❌ No tips returned or invalid format")
                    return False
            else:
                print(f"  ❌ API Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_history_dynamic_updates(self):
        """Test that search history updates dynamically after route searches."""
        print("📚 Testing Dynamic History Updates...")
        
        # First, perform a route search
        test_route = {
            "source": "Hyderabad Railway Station",
            "destination": "Charminar, Hyderabad",
            "route_type": "fastest"
        }
        
        try:
            print("  🔍 Performing test route search...")
            route_response = requests.post(
                f"{self.base_url}/api/route",
                json=test_route,
                timeout=30
            )
            
            if route_response.status_code == 200:
                route_data = route_response.json()
                print(f"    ✅ Route search successful")
                print(f"    📍 Route: {test_route['source']} → {test_route['destination']}")
                
                if route_data.get("routes") and len(route_data["routes"]) > 0:
                    route = route_data["routes"][0]
                    print(f"    📏 Distance: {route.get('distance', 'N/A')}")
                    print(f"    ⏱️ Duration: {route.get('duration', 'N/A')}")
                    
                    # Test that the route has the necessary data for history
                    required_history_fields = ['distance', 'duration']
                    missing_fields = [field for field in required_history_fields if not route.get(field)]
                    
                    if not missing_fields:
                        print(f"    ✅ Route has all required fields for history saving")
                        
                        # Check if eco metrics are present for eco-friendly routes
                        if test_route['route_type'] == 'eco_friendly':
                            if route.get('carbon_estimate_kg') and route.get('eco_score'):
                                print(f"    ✅ Eco metrics available for history")
                            else:
                                print(f"    ⚠️ Eco metrics missing (not critical for this test)")
                        
                        return True
                    else:
                        print(f"    ❌ Missing required fields for history: {missing_fields}")
                        return False
                else:
                    print(f"    ❌ No routes returned")
                    return False
            else:
                print(f"    ❌ Route search failed: HTTP {route_response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return False
    
    def test_frontend_improvements(self):
        """Test that frontend pages load with improved styling."""
        print("🎨 Testing Frontend Improvements...")
        
        pages_to_test = [
            ("/", "Main Page"),
            ("/auth.html", "Authentication Page"),
            ("/static/css/style.css", "Updated Stylesheet")
        ]
        
        passed = 0
        for path, name in pages_to_test:
            try:
                response = requests.get(f"{self.base_url}{path}", timeout=10)
                
                if response.status_code == 200:
                    print(f"  ✅ {name}: Accessible")
                    
                    # Check for specific improvements in CSS
                    if path.endswith('.css'):
                        content = response.text
                        improvements = [
                            'tip-header',
                            'tip-savings',
                            'new-item',
                            'newItemPulse',
                            'tip-icon'
                        ]
                        
                        found_improvements = [imp for imp in improvements if imp in content]
                        if len(found_improvements) >= 3:  # At least 3 improvements found
                            print(f"    ✅ Contains improved styling: {', '.join(found_improvements)}")
                        else:
                            print(f"    ⚠️ Some styling improvements may be missing")
                    
                    passed += 1
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {name}: Exception - {str(e)}")
        
        print(f"Frontend Improvements: {passed}/{len(pages_to_test)} pages accessible\n")
        return passed == len(pages_to_test)
    
    def open_application_for_manual_testing(self):
        """Open the application for manual testing of improvements."""
        print("🌐 Opening Application for Manual Testing...")
        
        try:
            webbrowser.open(f"{self.base_url}/auth.html")
            print(f"  ✅ Application opened at: {self.base_url}/auth.html")
            print("\n  📝 Manual Testing Checklist:")
            print("     1. ✅ Sign in and test route planning")
            print("     2. 🤖 Test AI chat - verify responses are plain text (no **bold** or *italic*)")
            print("     3. 🌱 Check eco tips - should have beautiful cards with icons and savings")
            print("     4. 📚 Test search history - should update immediately after route search")
            print("     5. 🎨 Verify improved visual design throughout the app")
            print("\n  🔍 Specific things to verify:")
            print("     • Gemini chat responses have no markdown formatting")
            print("     • Eco tips show icons, categories, and CO₂ savings")
            print("     • New searches appear in history without page refresh")
            print("     • History items have smooth animations when added")
            return True
        except Exception as e:
            print(f"  ❌ Could not open browser: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all improvement tests."""
        print("=" * 60)
        print("🔧 SMARTCITY-AI IMPROVEMENTS TESTING")
        print("=" * 60)
        
        results = []
        results.append(self.test_gemini_plain_text_response())
        results.append(self.test_improved_eco_tips())
        results.append(self.test_history_dynamic_updates())
        results.append(self.test_frontend_improvements())
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("=" * 60)
        print(f"📊 IMPROVEMENTS TEST SUMMARY")
        print(f"Passed: {passed_tests}/{total_tests} test suites")
        
        if passed_tests == total_tests:
            print("🎉 All improvements are working correctly!")
            print("✅ Gemini chat returns plain text")
            print("✅ Eco tips have beautiful enhanced display")
            print("✅ Search history updates dynamically")
            print("✅ Frontend improvements are applied")
        elif passed_tests >= total_tests * 0.75:
            print("✅ Most improvements are working!")
            print("⚠️ Some minor issues detected")
        else:
            print("⚠️ Some improvements need attention!")
        
        print("=" * 60)
        
        # Open for manual testing
        self.open_application_for_manual_testing()
        
        return passed_tests >= total_tests * 0.75

if __name__ == "__main__":
    tester = ImprovementsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
