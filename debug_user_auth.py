#!/usr/bin/env python3
"""
Debug User Authentication and History Loading
Check if there's a mismatch between user IDs when saving vs loading
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

class UserAuthDebugger:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def create_debug_page(self):
        """Create a debug page to check user authentication and history loading."""
        debug_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug User Authentication</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .debug-container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .debug-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .debug-section h3 { margin-top: 0; color: #333; }
        .debug-output { background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; }
        .btn { padding: 10px 15px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .status { padding: 5px 10px; border-radius: 3px; margin: 5px 0; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="debug-container">
        <h1>🔍 User Authentication & History Debug</h1>
        
        <div class="debug-section">
            <h3>1. Authentication Status</h3>
            <button class="btn btn-primary" onclick="checkAuthStatus()">Check Auth Status</button>
            <div id="auth-status" class="debug-output">Click button to check authentication...</div>
        </div>
        
        <div class="debug-section">
            <h3>2. User Information</h3>
            <button class="btn btn-success" onclick="getUserInfo()">Get User Info</button>
            <div id="user-info" class="debug-output">Click button to get user information...</div>
        </div>
        
        <div class="debug-section">
            <h3>3. Firestore Query Test</h3>
            <button class="btn btn-warning" onclick="testFirestoreQuery()">Test Firestore Query</button>
            <div id="firestore-test" class="debug-output">Click button to test Firestore query...</div>
        </div>
        
        <div class="debug-section">
            <h3>4. Manual History Load</h3>
            <button class="btn btn-primary" onclick="loadHistoryManually()">Load History Manually</button>
            <div id="manual-history" class="debug-output">Click button to manually load history...</div>
        </div>
        
        <div class="debug-section">
            <h3>5. Console Logs</h3>
            <div id="console-logs" class="debug-output">Console logs will appear here...</div>
        </div>
    </div>

    <!-- Firebase Scripts -->
    <script type="module">
        import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
        import { getAuth, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
        import { getFirestore, collection, query, where, orderBy, limit, getDocs } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

        // Firebase configuration (you'll need to replace with your actual config)
        const firebaseConfig = {
            apiKey: "AIzaSyBqJJQKqOqKqOqKqOqKqOqKqOqKqOqKqOq",
            authDomain: "smartcity-ai.firebaseapp.com",
            projectId: "smartcity-ai",
            storageBucket: "smartcity-ai.appspot.com",
            messagingSenderId: "123456789012",
            appId: "1:123456789012:web:abcdefghijklmnop"
        };

        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const db = getFirestore(app);

        let currentUser = null;

        // Monitor auth state
        onAuthStateChanged(auth, (user) => {
            currentUser = user;
            logToConsole(`Auth state changed: ${user ? user.email : 'No user'}`);
        });

        function logToConsole(message) {
            const consoleDiv = document.getElementById('console-logs');
            const timestamp = new Date().toLocaleTimeString();
            consoleDiv.textContent += `[${timestamp}] ${message}\\n`;
            console.log(message);
        }

        window.checkAuthStatus = function() {
            const statusDiv = document.getElementById('auth-status');
            
            if (currentUser) {
                statusDiv.innerHTML = `
                    <div class="status success">✅ User is authenticated</div>
                    <strong>Email:</strong> ${currentUser.email}<br>
                    <strong>UID:</strong> ${currentUser.uid}<br>
                    <strong>Display Name:</strong> ${currentUser.displayName || 'Not set'}<br>
                    <strong>Email Verified:</strong> ${currentUser.emailVerified}
                `;
                logToConsole(`Auth check: User authenticated as ${currentUser.email}`);
            } else {
                statusDiv.innerHTML = `<div class="status error">❌ No user authenticated</div>`;
                logToConsole('Auth check: No user authenticated');
            }
        };

        window.getUserInfo = function() {
            const userDiv = document.getElementById('user-info');
            
            if (currentUser) {
                const userInfo = {
                    uid: currentUser.uid,
                    email: currentUser.email,
                    displayName: currentUser.displayName,
                    emailVerified: currentUser.emailVerified,
                    photoURL: currentUser.photoURL,
                    providerData: currentUser.providerData
                };
                
                userDiv.innerHTML = `
                    <div class="status success">✅ User data retrieved</div>
                    <pre>${JSON.stringify(userInfo, null, 2)}</pre>
                `;
                logToConsole(`User info retrieved for ${currentUser.email}`);
            } else {
                userDiv.innerHTML = `<div class="status error">❌ No user to get info from</div>`;
                logToConsole('User info: No user authenticated');
            }
        };

        window.testFirestoreQuery = function() {
            const testDiv = document.getElementById('firestore-test');
            
            if (!currentUser) {
                testDiv.innerHTML = `<div class="status error">❌ No user authenticated for Firestore test</div>`;
                return;
            }

            testDiv.innerHTML = `<div class="status info">🔄 Testing Firestore query...</div>`;
            logToConsole(`Testing Firestore query for user: ${currentUser.uid}`);

            try {
                const q = query(
                    collection(db, 'searchHistory'),
                    where('userId', '==', currentUser.uid),
                    orderBy('timestamp', 'desc'),
                    limit(50)
                );

                getDocs(q).then((querySnapshot) => {
                    const results = [];
                    querySnapshot.forEach((doc) => {
                        const data = doc.data();
                        results.push({
                            id: doc.id,
                            userId: data.userId,
                            userEmail: data.userEmail,
                            startingAddress: data.startingAddress,
                            destination: data.destination,
                            timestamp: data.timestamp
                        });
                    });

                    testDiv.innerHTML = `
                        <div class="status success">✅ Firestore query successful</div>
                        <strong>Query:</strong> collection('searchHistory').where('userId', '==', '${currentUser.uid}')<br>
                        <strong>Results found:</strong> ${results.length}<br>
                        <pre>${JSON.stringify(results, null, 2)}</pre>
                    `;
                    logToConsole(`Firestore query returned ${results.length} results`);
                }).catch((error) => {
                    testDiv.innerHTML = `
                        <div class="status error">❌ Firestore query failed</div>
                        <strong>Error:</strong> ${error.message}<br>
                        <pre>${JSON.stringify(error, null, 2)}</pre>
                    `;
                    logToConsole(`Firestore query error: ${error.message}`);
                });
            } catch (error) {
                testDiv.innerHTML = `
                    <div class="status error">❌ Firestore query setup failed</div>
                    <strong>Error:</strong> ${error.message}
                `;
                logToConsole(`Firestore setup error: ${error.message}`);
            }
        };

        window.loadHistoryManually = function() {
            const historyDiv = document.getElementById('manual-history');
            
            if (!currentUser) {
                historyDiv.innerHTML = `<div class="status error">❌ No user authenticated for history load</div>`;
                return;
            }

            historyDiv.innerHTML = `<div class="status info">🔄 Loading search history manually...</div>`;
            logToConsole(`Manual history load for user: ${currentUser.email} (${currentUser.uid})`);

            // Try to use the global searchHistoryManager if available
            if (window.searchHistoryManager) {
                window.searchHistoryManager.loadSearchHistory().then((history) => {
                    historyDiv.innerHTML = `
                        <div class="status success">✅ History loaded via searchHistoryManager</div>
                        <strong>Items found:</strong> ${history.length}<br>
                        <pre>${JSON.stringify(history, null, 2)}</pre>
                    `;
                    logToConsole(`Manual history load returned ${history.length} items`);
                }).catch((error) => {
                    historyDiv.innerHTML = `
                        <div class="status error">❌ History load failed</div>
                        <strong>Error:</strong> ${error.message}
                    `;
                    logToConsole(`Manual history load error: ${error.message}`);
                });
            } else {
                historyDiv.innerHTML = `<div class="status error">❌ searchHistoryManager not available</div>`;
                logToConsole('Manual history load: searchHistoryManager not found');
            }
        };

        // Auto-check auth status on load
        setTimeout(() => {
            checkAuthStatus();
        }, 1000);
    </script>
</body>
</html>
        """
        
        debug_file = project_root / "frontend" / "debug_auth.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(debug_html)
        
        return debug_file

    def run_debug_session(self):
        """Run a comprehensive debug session."""
        print("=" * 60)
        print("🔍 USER AUTHENTICATION & HISTORY DEBUG")
        print("=" * 60)
        
        # Create debug page
        debug_file = self.create_debug_page()
        print(f"✅ Created debug page: {debug_file}")
        
        # Open debug page
        try:
            debug_url = f"{self.base_url}/debug_auth.html"
            webbrowser.open(debug_url)
            print(f"🌐 Debug page opened: {debug_url}")
            
            print("\n📝 DEBUG INSTRUCTIONS:")
            print("1. ✅ The debug page should open in your browser")
            print("2. 🔐 Sign in to your account first (if not already signed in)")
            print("3. 🔍 Click each button in order:")
            print("   - Check Auth Status")
            print("   - Get User Info") 
            print("   - Test Firestore Query")
            print("   - Load History Manually")
            print("4. 📊 Check the results in each section")
            print("5. 🐛 Look for any error messages or mismatches")
            
            print("\n🔍 WHAT TO LOOK FOR:")
            print("• User UID should be consistent across all sections")
            print("• Firestore query should return your existing data")
            print("• Check if userId in Firestore matches current user UID")
            print("• Verify that searchHistoryManager is available")
            print("• Look for any authentication or permission errors")
            
            print("\n🚨 COMMON ISSUES:")
            print("• User not authenticated when trying to load history")
            print("• UID mismatch between saved data and current user")
            print("• Firestore security rules blocking read access")
            print("• searchHistoryManager not properly initialized")
            print("• Firebase configuration issues")
            
            return True
            
        except Exception as e:
            print(f"❌ Error opening debug page: {str(e)}")
            return False

if __name__ == "__main__":
    debugger = UserAuthDebugger()
    success = debugger.run_debug_session()
    sys.exit(0 if success else 1)
