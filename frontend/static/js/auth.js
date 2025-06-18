// Authentication Management
import { 
    signInWithEmailAndPassword, 
    createUserWithEmailAndPassword, 
    signInWithPopup, 
    GoogleAuthProvider, 
    signOut, 
    onAuthStateChanged,
    updateProfile
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

import { auth } from './firebase-config.js';

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.authStateListeners = [];
        this.googleProvider = new GoogleAuthProvider();
        
        // Configure Google provider
        this.googleProvider.addScope('profile');
        this.googleProvider.addScope('email');
        
        this.init();
    }
    
    init() {
        // Listen for authentication state changes
        onAuthStateChanged(auth, (user) => {
            this.currentUser = user;
            this.updateUI(user);
            this.notifyAuthStateListeners(user);
            
            if (user) {
                console.log('User signed in:', user.email);
                this.showWelcomeMessage(user);
            } else {
                console.log('User signed out');
            }
        });
    }
    
    // Sign up with email and password
    async signUp(email, password, displayName = '') {
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;
            
            // Update display name if provided
            if (displayName) {
                await updateProfile(user, { displayName: displayName });
            }
            
            this.showSuccess('Account created successfully! Welcome to SmartCity AI!');
            return user;
        } catch (error) {
            this.handleAuthError(error);
            throw error;
        }
    }
    
    // Sign in with email and password
    async signIn(email, password) {
        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            this.showSuccess('Welcome back to SmartCity AI!');
            return userCredential.user;
        } catch (error) {
            this.handleAuthError(error);
            throw error;
        }
    }
    
    // Sign in with Google
    async signInWithGoogle() {
        try {
            const result = await signInWithPopup(auth, this.googleProvider);
            const user = result.user;
            this.showSuccess(`Welcome ${user.displayName || user.email}!`);
            return user;
        } catch (error) {
            this.handleAuthError(error);
            throw error;
        }
    }
    
    // Sign out
    async signOutUser() {
        try {
            await signOut(auth);
            this.showSuccess('Signed out successfully');
            // Redirect to auth page after sign out
            setTimeout(() => {
                window.location.href = '/auth.html';
            }, 1000);
        } catch (error) {
            console.error('Sign out error:', error);
            this.showError('Error signing out');
        }
    }
    
    // Check if user is authenticated
    isAuthenticated() {
        return this.currentUser !== null;
    }
    
    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }
    
    // Add auth state listener
    addAuthStateListener(callback) {
        this.authStateListeners.push(callback);
    }
    
    // Notify all auth state listeners
    notifyAuthStateListeners(user) {
        this.authStateListeners.forEach(callback => callback(user));
    }
    
    // Update UI based on authentication state
    updateUI(user) {
        const authButtons = document.getElementById('auth-buttons');
        const userInfo = document.getElementById('user-info');
        const authModal = document.getElementById('auth-modal');
        
        if (user) {
            // User is signed in
            if (authButtons) authButtons.style.display = 'none';
            if (userInfo) {
                userInfo.style.display = 'flex';

                // Get profile photo - use Google photo if available, otherwise default
                const profilePhoto = user.photoURL || this.generateDefaultAvatar(user.displayName || user.email);

                userInfo.innerHTML = `
                    <div class="user-avatar">
                        <img src="${profilePhoto}"
                             alt="User Avatar"
                             onerror="this.src='${this.generateDefaultAvatar(user.displayName || user.email)}'">
                    </div>
                    <div class="user-details">
                        <span class="user-name">${user.displayName || user.email.split('@')[0]}</span>
                        <span class="user-email">${user.email}</span>
                    </div>
                    <button id="sign-out-btn" class="btn btn-outline btn-sm">
                        <i class="fas fa-sign-out-alt"></i> Sign Out
                    </button>
                `;
                
                // Add sign out event listener
                const signOutBtn = document.getElementById('sign-out-btn');
                if (signOutBtn) {
                    signOutBtn.addEventListener('click', () => this.signOutUser());
                }
            }
            
            // Close auth modal if open
            if (authModal) authModal.style.display = 'none';
            
        } else {
            // User is signed out
            if (authButtons) authButtons.style.display = 'flex';
            if (userInfo) userInfo.style.display = 'none';
        }
    }
    
    // Show welcome message
    showWelcomeMessage(user) {
        const welcomeMsg = document.createElement('div');
        welcomeMsg.className = 'welcome-notification';
        welcomeMsg.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-user-check"></i>
                <span>Welcome back, ${user.displayName || user.email.split('@')[0]}!</span>
            </div>
        `;
        
        document.body.appendChild(welcomeMsg);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (welcomeMsg.parentNode) {
                welcomeMsg.parentNode.removeChild(welcomeMsg);
            }
        }, 3000);
    }
    
    // Handle authentication errors
    handleAuthError(error) {
        let message = 'Authentication error occurred';
        
        switch (error.code) {
            case 'auth/user-not-found':
                message = 'No account found with this email address';
                break;
            case 'auth/wrong-password':
                message = 'Incorrect password';
                break;
            case 'auth/email-already-in-use':
                message = 'An account with this email already exists';
                break;
            case 'auth/weak-password':
                message = 'Password should be at least 6 characters';
                break;
            case 'auth/invalid-email':
                message = 'Invalid email address';
                break;
            case 'auth/popup-closed-by-user':
                message = 'Sign-in popup was closed';
                break;
            case 'auth/cancelled-popup-request':
                message = 'Sign-in was cancelled';
                break;
            default:
                message = error.message || 'Authentication failed';
        }
        
        this.showError(message);
        console.error('Auth error:', error);
    }
    
    // Show success message
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    // Show error message
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    // Generate default avatar using initials
    generateDefaultAvatar(name) {
        const initials = this.getInitials(name);
        const colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
            '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3'
        ];

        // Use email/name hash to consistently pick a color
        const colorIndex = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
        const backgroundColor = colors[colorIndex];

        // Create SVG avatar
        const svg = `
            <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                <circle cx="16" cy="16" r="16" fill="${backgroundColor}"/>
                <text x="16" y="20" text-anchor="middle" fill="white" font-family="Inter, sans-serif" font-size="12" font-weight="600">${initials}</text>
            </svg>
        `;

        return `data:image/svg+xml;base64,${btoa(svg)}`;
    }

    // Get initials from name
    getInitials(name) {
        if (!name) return 'U';

        const words = name.trim().split(' ');
        if (words.length === 1) {
            return words[0].charAt(0).toUpperCase();
        }

        return (words[0].charAt(0) + words[words.length - 1].charAt(0)).toUpperCase();
    }

    // Show notification
    showNotification(message, type = 'info') {
        // Try to use existing notification system
        if (window.trafficApp && window.trafficApp.showNotification) {
            window.trafficApp.showNotification(message, type);
            return;
        }

        // Fallback notification system
        const notification = document.createElement('div');
        notification.className = `auth-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 4000);
    }
}

// Create global auth manager instance
const authManager = new AuthManager();

// Export for use in other modules
export default authManager;

// Make available globally for backward compatibility
window.authManager = authManager;
