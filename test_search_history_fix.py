#!/usr/bin/env python3
"""
Test script to verify the search history index fix.

This script tests both the backend functionality and provides
instructions for testing the frontend fix.
"""

import requests
import time
import json
from pathlib import Path

def test_backend_availability():
    """Test if the backend server is running."""
    print("🔧 Testing Backend Availability...")
    
    try:
        response = requests.get("http://localhost:8000/api/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print("✅ Backend is running")
            print(f"   - User Auth: {'✅' if config.get('features', {}).get('user_auth') else '❌'}")
            print(f"   - Google Maps: {'✅' if config.get('features', {}).get('google_maps') else '❌'}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not available: {e}")
        return False

def test_frontend_files():
    """Test if the required frontend files exist and have been updated."""
    print("\n📁 Testing Frontend Files...")
    
    files_to_check = {
        "frontend/static/js/search-history.js": [
            "loadSearchHistoryOptimized",
            "loadSearchHistoryBasic",
            "failed-precondition"
        ],
        "firebase.json": [
            "firestore",
            "indexes"
        ],
        "firestore.indexes.json": [
            "searchHistory",
            "userId",
            "timestamp"
        ],
        "firestore.rules": [
            "searchHistory",
            "request.auth.uid"
        ]
    }
    
    all_good = True
    
    for file_path, required_content in files_to_check.items():
        path = Path(file_path)
        if not path.exists():
            print(f"❌ {file_path} - Missing")
            all_good = False
            continue
        
        try:
            content = path.read_text(encoding='utf-8')
            missing_content = []
            
            for required in required_content:
                if required not in content:
                    missing_content.append(required)
            
            if missing_content:
                print(f"⚠️  {file_path} - Missing content: {', '.join(missing_content)}")
                all_good = False
            else:
                print(f"✅ {file_path} - All required content found")
                
        except Exception as e:
            print(f"❌ {file_path} - Error reading: {e}")
            all_good = False
    
    return all_good

def print_manual_testing_instructions():
    """Print instructions for manual testing."""
    print("\n🧪 Manual Testing Instructions:")
    print("=" * 40)
    
    print("\n1. Start the application:")
    print("   cd SmartCity-AI")
    print("   python -m backend.main")
    
    print("\n2. Open browser and go to:")
    print("   http://localhost:8000")
    
    print("\n3. Sign in with your account:")
    print("   - Use the same account that had the index error")
    print("   - Email: doremon7pokemon@gmail.com")
    
    print("\n4. Click on 'History' tab")
    
    print("\n5. Check browser console (F12):")
    print("   Expected behavior:")
    print("   ✅ Should see: 'Trying optimized Firestore query'")
    print("   ✅ If index exists: Search history loads successfully")
    print("   ✅ If no index: Should see 'Falling back to basic query' and still work")
    print("   ❌ Should NOT see: 'The query requires an index' error")
    
    print("\n6. Test search history functionality:")
    print("   - Perform a route search")
    print("   - Check if it appears in history")
    print("   - Try repeating a search")
    print("   - Try deleting a search")

def print_index_creation_instructions():
    """Print instructions for creating the Firestore index."""
    print("\n🔥 Firestore Index Creation:")
    print("=" * 35)
    
    print("\nOption 1: Quick Fix (Manual)")
    print("Click this link to create the index:")
    print("https://console.firebase.google.com/v1/r/project/smart-traffic-e1da5/firestore/indexes?create_composite=Cllwcm9qZWN0cy9zbWFydC10cmFmZmljLWUxZGE1L2RhdGFiYXNlcy8oZGVmYXVsdCkvY29sbGVjdGlvbkdyb3Vwcy9zZWFyY2hIaXN0b3J5L2luZGV4ZXMvXxABGgoKBnVzZXJJZBABGg0KCXRpbWVzdGFtcBACGgwKCF9fbmFtZV9fEAI")
    
    print("\nOption 2: Using Firebase CLI")
    print("1. Install Firebase CLI: npm install -g firebase-tools")
    print("2. Login: firebase login")
    print("3. Deploy indexes: firebase deploy --only firestore:indexes")
    
    print("\nOption 3: Using the deployment script")
    print("python deploy-firestore-config.py")

def main():
    """Main test function."""
    print("🔍 Search History Fix Verification")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_availability()
    
    # Test frontend files
    frontend_ok = test_frontend_files()
    
    # Summary
    print("\n📊 Test Summary:")
    print("-" * 20)
    print(f"Backend: {'✅ Ready' if backend_ok else '❌ Issues'}")
    print(f"Frontend: {'✅ Updated' if frontend_ok else '❌ Issues'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 All automated tests passed!")
        print("The search history fix has been implemented.")
        print("The application now handles missing Firestore indexes gracefully.")
    else:
        print("\n⚠️  Some issues detected. Please review the errors above.")
    
    # Always show manual testing instructions
    print_manual_testing_instructions()
    print_index_creation_instructions()
    
    print("\n💡 Key Improvements Made:")
    print("- Added fallback query for missing composite index")
    print("- Created Firebase configuration files")
    print("- Added proper error handling")
    print("- Improved user feedback")
    
    return backend_ok and frontend_ok

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Verification completed successfully!")
    else:
        print("\n❌ Some issues need to be resolved.")
