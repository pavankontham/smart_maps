// Firebase Configuration and Initialization
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getAuth, connectAuthEmulator } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { getFirestore, connectFirestoreEmulator } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';
import { getAnalytics } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBzGuJe_whjdwysLSKdjAP3l77LSjwFTF0",
  authDomain: "smart-traffic-e1da5.firebaseapp.com",
  projectId: "smart-traffic-e1da5",
  storageBucket: "smart-traffic-e1da5.firebasestorage.app",
  messagingSenderId: "193384881898",
  appId: "1:193384881898:web:92a679af0603da319a4193",
  measurementId: "G-VX8L6GVJ42"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
const auth = getAuth(app);
const db = getFirestore(app);
const analytics = getAnalytics(app);

// Export Firebase services for use in other modules
export { auth, db, analytics };

// Global Firebase app instance for backward compatibility
window.firebaseApp = app;
window.firebaseAuth = auth;
window.firebaseDb = db;

console.log('Firebase initialized successfully');
