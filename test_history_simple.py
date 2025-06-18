#!/usr/bin/env python3
"""
Simple History Test
Quick test to identify the exact issue with search history loading
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

class SimpleHistoryTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_basic_functionality(self):
        """Test basic functionality step by step."""
        print("🔍 Testing Basic Functionality...")
        
        # Test 1: Server health
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("  ✅ Server is healthy")
            else:
                print(f"  ❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Server connection failed: {str(e)}")
            return False
        
        # Test 2: Dashboard page
        try:
            response = requests.get(f"{self.base_url}/dashboard.html", timeout=10)
            if response.status_code == 200:
                content = response.text
                if 'id="search-history"' in content:
                    print("  ✅ Dashboard has search-history container")
                else:
                    print("  ❌ Dashboard missing search-history container")
                    return False
            else:
                print(f"  ❌ Dashboard page failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Dashboard access failed: {str(e)}")
            return False
        
        # Test 3: JavaScript files
        js_files = [
            "/static/js/firebase-config.js",
            "/static/js/auth.js", 
            "/static/js/search-history.js",
            "/static/js/main.js"
        ]
        
        for js_file in js_files:
            try:
                response = requests.get(f"{self.base_url}{js_file}", timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ {js_file} accessible")
                else:
                    print(f"  ❌ {js_file} failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"  ❌ {js_file} access failed: {str(e)}")
                return False
        
        return True
    
    def open_application_with_instructions(self):
        """Open the application with detailed debugging instructions."""
        print("🌐 Opening Application with Debug Instructions...")
        
        try:
            webbrowser.open(f"{self.base_url}/auth.html")
            print(f"  ✅ Application opened at: {self.base_url}/auth.html")
            
            print("\n" + "="*60)
            print("🔍 STEP-BY-STEP DEBUGGING INSTRUCTIONS")
            print("="*60)
            
            print("\n📋 STEP 1: AUTHENTICATION")
            print("1. Sign in with your Google account")
            print("2. You should be redirected to the main dashboard")
            print("3. Check that you see your profile in the top-right corner")
            
            print("\n📋 STEP 2: OPEN BROWSER CONSOLE")
            print("1. Press F12 to open Developer Tools")
            print("2. Go to the 'Console' tab")
            print("3. Look for any red error messages")
            
            print("\n📋 STEP 3: TEST ROUTE SEARCH")
            print("1. Enter source: 'Kayamkulam'")
            print("2. Enter destination: 'Karunagappalli'")
            print("3. Select vehicle type: 'Car'")
            print("4. Click 'Get Route'")
            print("5. Wait for results to appear")
            print("6. Check console for save messages:")
            print("   - Look for: '💾 Saving search to history for user:'")
            print("   - Look for: '📄 Search record to save:'")
            print("   - Look for: 'Search saved successfully with ID:'")
            
            print("\n📋 STEP 4: TEST HISTORY LOADING")
            print("1. Click on the 'History' tab")
            print("2. Check console for loading messages:")
            print("   - Look for: '🔍 Loading search history for user:'")
            print("   - Look for: '📊 Firestore query:'")
            print("   - Look for: '📄 Found history document:'")
            print("   - Look for: '✅ Successfully loaded X search history items'")
            
            print("\n📋 STEP 5: IDENTIFY THE ISSUE")
            print("Check for these common problems:")
            print("❌ Authentication issues:")
            print("   - 'No user authenticated, cannot load search history'")
            print("   - User UID is null or undefined")
            print("❌ Firestore issues:")
            print("   - 'Error loading search history: [error]'")
            print("   - Permission denied errors")
            print("   - Network connection errors")
            print("❌ Data mismatch issues:")
            print("   - Query returns 0 results but data exists in Firestore")
            print("   - UID in saved data doesn't match current user UID")
            print("❌ UI issues:")
            print("   - 'Search history container not found'")
            print("   - History section not visible")
            
            print("\n📋 STEP 6: REPORT FINDINGS")
            print("Copy and paste the console messages that appear when:")
            print("1. You click the History tab")
            print("2. Any error messages in red")
            print("3. The user UID and email from authentication")
            print("4. Any Firestore query results")
            
            print("\n🔧 QUICK FIXES TO TRY:")
            print("1. Refresh the page and try again")
            print("2. Sign out and sign back in")
            print("3. Clear browser cache and cookies")
            print("4. Try in an incognito/private browser window")
            
            print("\n" + "="*60)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Could not open browser: {str(e)}")
            return False
    
    def run_simple_test(self):
        """Run simple test and provide debugging guidance."""
        print("=" * 60)
        print("🔍 SIMPLE SEARCH HISTORY DEBUG TEST")
        print("=" * 60)
        
        if self.test_basic_functionality():
            print("\n✅ All basic functionality tests passed!")
            print("🔍 The issue is likely in the frontend JavaScript or Firebase authentication.")
            print("📝 Opening application with detailed debugging instructions...")
            
            self.open_application_with_instructions()
            
            return True
        else:
            print("\n❌ Basic functionality tests failed!")
            print("🔧 Fix the server/file access issues first before debugging history.")
            return False

if __name__ == "__main__":
    tester = SimpleHistoryTester()
    success = tester.run_simple_test()
    sys.exit(0 if success else 1)
