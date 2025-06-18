#!/usr/bin/env python3
"""
Firebase Firestore Configuration Deployment Script

This script helps deploy Firestore indexes and security rules.
It provides instructions and commands for setting up the required
composite indexes for the search history functionality.
"""

import json
import os
import sys
from pathlib import Path

def main():
    """Main function to guide through Firestore configuration."""
    
    print("🔥 Firebase Firestore Configuration Helper")
    print("=" * 50)
    
    # Check if Firebase CLI is available
    print("\n1. Checking Firebase CLI availability...")
    
    # Check if firebase.json exists
    firebase_json_path = Path("firebase.json")
    if not firebase_json_path.exists():
        print("❌ firebase.json not found in current directory")
        print("   Make sure you're running this from the SmartCity-AI directory")
        return False
    
    print("✅ firebase.json found")
    
    # Check firestore.indexes.json
    indexes_path = Path("firestore.indexes.json")
    if not indexes_path.exists():
        print("❌ firestore.indexes.json not found")
        return False
    
    print("✅ firestore.indexes.json found")
    
    # Display current indexes configuration
    print("\n2. Current Firestore Indexes Configuration:")
    print("-" * 40)
    
    try:
        with open(indexes_path, 'r') as f:
            indexes_config = json.load(f)
        
        for i, index in enumerate(indexes_config.get('indexes', []), 1):
            print(f"\nIndex {i}:")
            print(f"  Collection: {index['collectionGroup']}")
            print(f"  Fields:")
            for field in index['fields']:
                print(f"    - {field['fieldPath']} ({field['order']})")
    
    except Exception as e:
        print(f"❌ Error reading indexes configuration: {e}")
        return False
    
    # Provide deployment instructions
    print("\n3. Deployment Instructions:")
    print("-" * 30)
    
    print("\nOption A: Using Firebase CLI (Recommended)")
    print("1. Install Firebase CLI if not already installed:")
    print("   npm install -g firebase-tools")
    print("\n2. Login to Firebase:")
    print("   firebase login")
    print("\n3. Initialize Firebase project (if not done):")
    print("   firebase init")
    print("\n4. Deploy Firestore indexes:")
    print("   firebase deploy --only firestore:indexes")
    print("\n5. Deploy Firestore rules:")
    print("   firebase deploy --only firestore:rules")
    
    print("\nOption B: Manual Index Creation (Quick Fix)")
    print("Click this link to create the required index manually:")
    print("https://console.firebase.google.com/v1/r/project/smart-traffic-e1da5/firestore/indexes?create_composite=Cllwcm9qZWN0cy9zbWFydC10cmFmZmljLWUxZGE1L2RhdGFiYXNlcy8oZGVmYXVsdCkvY29sbGVjdGlvbkdyb3Vwcy9zZWFyY2hIaXN0b3J5L2luZGV4ZXMvXxABGgoKBnVzZXJJZBABGg0KCXRpbWVzdGFtcBACGgwKCF9fbmFtZV9fEAI")
    
    print("\n4. Testing the Fix:")
    print("-" * 20)
    print("After deploying the indexes:")
    print("1. Wait 2-5 minutes for indexes to build")
    print("2. Refresh your application")
    print("3. Try loading search history")
    print("4. Check browser console for success messages")
    
    print("\n5. Troubleshooting:")
    print("-" * 20)
    print("If you still see index errors:")
    print("- Check Firebase Console > Firestore > Indexes")
    print("- Verify index status is 'Enabled'")
    print("- Check browser network tab for 403/401 errors")
    print("- Verify Firestore security rules allow access")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    print("\n✅ Configuration check completed!")
    print("Follow the deployment instructions above to fix the index error.")
