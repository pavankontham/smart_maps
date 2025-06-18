// Main Application JavaScript
import authManager from './auth.js';
import searchHistoryManager from './search-history.js';

class TrafficApp {
    constructor() {
        this.map = null;
        this.directionsService = null;
        this.directionsRenderer = null;
        this.currentRoute = null;
        this.markers = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupNavigation();
        this.loadEcoTips();
        
        // Listen for auth state changes
        authManager.addAuthStateListener((user) => {
            if (user) {
                console.log('User authenticated, loading personalized features');
                // Load search history when user signs in
                setTimeout(() => {
                    searchHistoryManager.loadSearchHistory();
                }, 1000);
            } else {
                console.log('User signed out, clearing personalized data');
            }
        });
    }
    
    setupEventListeners() {
        // Route planning
        document.getElementById('get-route-btn')?.addEventListener('click', () => this.getRoute());
        document.getElementById('save-route-btn')?.addEventListener('click', () => this.saveRoute());
        
        // Chat functionality
        document.getElementById('send-chat-btn')?.addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });
        
        // Form inputs
        document.getElementById('source')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.getRoute();
        });
        document.getElementById('destination')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.getRoute();
        });
    }
    
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('.section');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all links and sections
                navLinks.forEach(l => l.classList.remove('active'));
                sections.forEach(s => s.classList.remove('active'));
                
                // Add active class to clicked link
                link.classList.add('active');
                
                // Show corresponding section
                const sectionId = link.dataset.section + '-section';
                const section = document.getElementById(sectionId);
                if (section) {
                    section.classList.add('active');

                    // Load search history when history section is activated
                    if (link.dataset.section === 'history') {
                        console.log('History tab clicked, loading search history');
                        const user = authManager.getCurrentUser();
                        if (user) {
                            // Always reload history when tab is clicked to ensure fresh data
                            setTimeout(() => {
                                searchHistoryManager.loadSearchHistory();
                            }, 100);
                        } else {
                            console.log('User not authenticated, cannot load history');
                            searchHistoryManager.clearLocalHistory();
                        }
                    }
                }
            });
        });
    }
    
    initializeMap() {
        try {
            const defaultCenter = { lat: 17.3850, lng: 78.4867 }; // Hyderabad, India

            const mapElement = document.getElementById('map');
            if (!mapElement) {
                console.error('Map container element not found');
                return;
            }

            this.map = new google.maps.Map(mapElement, {
                zoom: 12,
                center: defaultCenter,
                mapTypeControl: true,
                streetViewControl: true,
                fullscreenControl: true,
                styles: [
                    {
                        featureType: 'poi',
                        elementType: 'labels',
                        stylers: [{ visibility: 'off' }]
                    }
                ]
            });

            this.directionsService = new google.maps.DirectionsService();
            this.directionsRenderer = new google.maps.DirectionsRenderer({
                draggable: true,
                panel: null
            });
            
            this.directionsRenderer.setMap(this.map);
            
            // Hide loading indicator
            const mapLoading = document.getElementById('map-loading');
            if (mapLoading) {
                mapLoading.style.display = 'none';
            }
            
            console.log('Google Maps initialized successfully');
            
        } catch (error) {
            console.error('Error initializing map:', error);
            this.showError('Failed to initialize map');
        }
    }
    
    async getRoute() {
        const source = document.getElementById('source')?.value.trim();
        const destination = document.getElementById('destination')?.value.trim();
        const routeType = document.getElementById('route-type')?.value || 'fastest';
        const avoidTolls = document.getElementById('avoid-tolls')?.checked || false;
        const avoidHighways = document.getElementById('avoid-highways')?.checked || false;
        
        if (!source || !destination) {
            this.showError('Please enter both starting point and destination');
            return;
        }
        
        this.showLoading(true);
        
        try {
            const routeRequest = {
                source: source,
                destination: destination,
                route_type: routeType,
                avoid_tolls: avoidTolls,
                avoid_highways: avoidHighways
            };
            
            const response = await fetch('/api/route', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(routeRequest)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const routeData = await response.json();
            
            if (routeData.routes && routeData.routes.length > 0) {
                this.displayRoute(routeData.routes[0]);
                this.showSuccess('Route calculated successfully!');

                // Automatically save to search history if user is authenticated
                const user = authManager.getCurrentUser();
                if (user) {
                    try {
                        const vehicleType = document.getElementById('vehicle-type')?.value || 'car';

                        const searchData = {
                            startingAddress: source,
                            destination: destination,
                            distance: routeData.routes[0].distance,
                            duration: routeData.routes[0].duration,
                            routeType: routeType,
                            vehicleType: vehicleType,
                            avoidTolls: avoidTolls,
                            avoidHighways: avoidHighways,
                            carbonEstimate: routeData.routes[0].carbon_estimate_kg,
                            ecoScore: routeData.routes[0].eco_score
                        };

                        await searchHistoryManager.saveSearch(searchData);
                        console.log('Route automatically saved to history');

                        // Immediately refresh history display if history section is visible
                        const historySection = document.getElementById('history-section');
                        if (historySection && historySection.classList.contains('active')) {
                            console.log('History section is active, refreshing display');
                            setTimeout(() => {
                                searchHistoryManager.loadSearchHistory();
                            }, 500); // Short delay to ensure Firestore write is complete
                        }
                    } catch (error) {
                        console.error('Error auto-saving to history:', error);
                    }
                }
            } else {
                this.showError('No routes found for the given locations');
            }
            
        } catch (error) {
            console.error('Error getting route:', error);
            this.showError('Failed to calculate route. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    displayRoute(route) {
        this.currentRoute = route;
        
        // Display route on map if Google Maps is available
        if (typeof google !== 'undefined' && google.maps && this.directionsRenderer) {
            this.displayRouteOnMap(route);
        } else {
            console.log('Google Maps not available, showing route info only');
        }
        
        // Always display route information
        this.displayRouteInfo(route);
        
        // Show route results section
        const routeResults = document.getElementById('route-results');
        if (routeResults) {
            routeResults.style.display = 'block';
        }
    }
    
    displayRouteOnMap(route) {
        if (!this.directionsService || !this.directionsRenderer) {
            console.log('Google Maps services not available');
            return;
        }
        
        try {
            const source = document.getElementById('source').value;
            const destination = document.getElementById('destination').value;
            
            const request = {
                origin: source,
                destination: destination,
                travelMode: google.maps.TravelMode.DRIVING,
                avoidTolls: document.getElementById('avoid-tolls')?.checked || false,
                avoidHighways: document.getElementById('avoid-highways')?.checked || false
            };
            
            this.directionsService.route(request, (result, status) => {
                if (status === 'OK') {
                    this.directionsRenderer.setDirections(result);
                    console.log('Route displayed on map successfully');
                } else {
                    console.error('Google Maps directions failed:', status);
                    this.showWarning('Unable to display route on map. Route information is still available below.');
                }
            });
            
        } catch (error) {
            console.error('Error displaying route on map:', error);
        }
    }
    
    displayRouteInfo(route) {
        const routeInfoDiv = document.getElementById('route-info');
        const ecoMetricsDiv = document.getElementById('eco-metrics');
        
        if (!routeInfoDiv || !ecoMetricsDiv) {
            console.error('Route info display elements not found');
            return;
        }
        
        // Display basic route information
        routeInfoDiv.innerHTML = `
            <div class="route-summary">
                <div class="summary-item">
                    <div class="summary-icon">
                        <i class="fas fa-route"></i>
                    </div>
                    <div class="summary-details">
                        <span class="summary-label">Distance</span>
                        <span class="summary-value">${route.distance}</span>
                    </div>
                </div>
                <div class="summary-item">
                    <div class="summary-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="summary-details">
                        <span class="summary-label">Duration</span>
                        <span class="summary-value">${route.duration}</span>
                    </div>
                </div>
                ${route.duration_in_traffic ? `
                    <div class="summary-item">
                        <div class="summary-icon">
                            <i class="fas fa-traffic-light"></i>
                        </div>
                        <div class="summary-details">
                            <span class="summary-label">With Traffic</span>
                            <span class="summary-value">${route.duration_in_traffic}</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Display eco metrics if available
        if (route.carbon_estimate_kg || route.eco_score) {
            ecoMetricsDiv.innerHTML = `
                <div class="eco-summary">
                    <h4><i class="fas fa-leaf"></i> Environmental Impact</h4>
                    <div class="eco-items">
                        ${route.carbon_estimate_kg ? `
                            <div class="eco-item">
                                <span class="eco-label">CO₂ Emissions</span>
                                <span class="eco-value">${route.carbon_estimate_kg} kg</span>
                            </div>
                        ` : ''}
                        ${route.eco_score ? `
                            <div class="eco-item">
                                <span class="eco-label">Eco Score</span>
                                <span class="eco-value eco-score-${this.getEcoScoreClass(route.eco_score)}">${route.eco_score}/100</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            ecoMetricsDiv.style.display = 'block';
        } else {
            ecoMetricsDiv.style.display = 'none';
        }
    }
    
    getEcoScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }
    
    async saveRoute() {
        if (!this.currentRoute) {
            this.showError('No route to save');
            return;
        }
        
        const user = authManager.getCurrentUser();
        if (!user) {
            this.showError('Please sign in to save routes');
            return;
        }
        
        try {
            const searchData = {
                startingAddress: document.getElementById('source').value,
                destination: document.getElementById('destination').value,
                distance: this.currentRoute.distance,
                duration: this.currentRoute.duration,
                routeType: document.getElementById('route-type').value,
                vehicleType: document.getElementById('vehicle-type')?.value || 'car',
                avoidTolls: document.getElementById('avoid-tolls').checked,
                avoidHighways: document.getElementById('avoid-highways').checked,
                carbonEstimate: this.currentRoute.carbon_estimate_kg,
                ecoScore: this.currentRoute.eco_score
            };
            
            await searchHistoryManager.saveSearch(searchData);
            this.showSuccess('Route saved to your history!');
            
        } catch (error) {
            console.error('Error saving route:', error);
            this.showError('Failed to save route');
        }
    }
    
    async sendChatMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput?.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addChatMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        this.addTypingIndicator();
        
        try {
            const response = await fetch('/api/eco_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    context: {
                        location: document.getElementById('source')?.value || null,
                        current_route: this.currentRoute ? {
                            from: document.getElementById('source')?.value,
                            to: document.getElementById('destination')?.value,
                            distance: this.currentRoute.distance
                        } : null
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add bot response
            this.addChatMessage(data.response, 'bot');
            
        } catch (error) {
            console.error('Error sending chat message:', error);
            this.removeTypingIndicator();
            this.addChatMessage('Sorry, I\'m having trouble responding right now. Please try again later.', 'bot');
        }
    }
    
    addChatMessage(message, sender) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const avatar = sender === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${message}</p>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    addTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    async loadEcoTips() {
        try {
            const response = await fetch('/api/eco_tips');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.displayEcoTips(data.tips || []);
            
        } catch (error) {
            console.error('Error loading eco tips:', error);
            this.displayEcoTips([
                {
                    tip: 'Use public transportation for your daily commute to reduce carbon emissions by up to 45% compared to driving alone.',
                    category: 'Public Transport',
                    impact: 'high',
                    icon: '🚌',
                    savings: 'Up to 2.3 kg CO₂ per day'
                },
                {
                    tip: 'Choose cycling or walking for trips under 5 kilometers for zero emissions and great exercise.',
                    category: 'Active Transport',
                    impact: 'high',
                    icon: '🚴',
                    savings: '100% emission reduction'
                },
                {
                    tip: 'Combine multiple errands into a single trip to reduce fuel consumption by 20-30%.',
                    category: 'Trip Planning',
                    impact: 'medium',
                    icon: '🗺️',
                    savings: '0.5-1.2 kg CO₂ per week'
                }
            ]);
        }
    }
    
    displayEcoTips(tips) {
        const container = document.getElementById('eco-tips-container');
        if (!container) return;

        container.innerHTML = tips.map(tip => `
            <div class="tip-item ${tip.impact}-impact">
                <div class="tip-header">
                    <div class="tip-icon">${tip.icon || '🌱'}</div>
                    <div class="tip-category">${tip.category || 'Eco Tip'}</div>
                    <div class="tip-impact-badge impact-${tip.impact}">
                        ${tip.impact} impact
                    </div>
                </div>
                <div class="tip-content">${tip.tip}</div>
                ${tip.savings ? `
                    <div class="tip-savings">
                        <i class="fas fa-leaf"></i>
                        <span>Potential savings: ${tip.savings}</span>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    // Utility methods
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 4000);
    }
    
    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showWarning(message) {
        this.showNotification(message, 'warning');
    }
}

// Initialize the application
const trafficApp = new TrafficApp();

// Make it globally available
window.trafficApp = trafficApp;

export default trafficApp;
