// Search History Management with Firestore
import { 
    collection, 
    addDoc, 
    query, 
    where, 
    orderBy, 
    limit, 
    getDocs,
    deleteDoc,
    doc,
    serverTimestamp
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

import { db } from './firebase-config.js';
import authManager from './auth.js';

class SearchHistoryManager {
    constructor() {
        this.collectionName = 'searchHistory';
        this.maxHistoryItems = 50; // Limit history to last 50 searches
        
        // Listen for auth state changes
        authManager.addAuthStateListener((user) => {
            if (user) {
                this.loadSearchHistory();
            } else {
                this.clearLocalHistory();
            }
        });
    }
    
    // Save a route search to Firestore
    async saveSearch(searchData) {
        const user = authManager.getCurrentUser();
        if (!user) {
            console.log('User not authenticated, search not saved');
            return;
        }

        console.log('💾 Saving search to history for user:', user.email, 'UID:', user.uid);
        console.log('📝 Search data received:', searchData);

        try {
            const searchRecord = {
                userId: user.uid,
                userEmail: user.email,
                startingAddress: searchData.source || searchData.startingAddress,
                destination: searchData.destination,
                distance: searchData.distance || 'Unknown',
                duration: searchData.duration || 'Unknown',
                routeType: searchData.routeType || 'fastest',
                timestamp: serverTimestamp(),
                searchDate: new Date().toISOString(),
                searchTime: new Date().toLocaleTimeString(),
                // Additional metadata
                avoidTolls: searchData.avoidTolls || false,
                avoidHighways: searchData.avoidHighways || false,
                vehicleType: searchData.vehicleType || 'car',
                carbonEstimate: searchData.carbonEstimate || null,
                ecoScore: searchData.ecoScore || null
            };

            console.log('📄 Search record to save:', searchRecord);

            const docRef = await addDoc(collection(db, this.collectionName), searchRecord);
            console.log('Search saved successfully with ID:', docRef.id);

            // Add the new search to local display immediately for instant feedback
            this.addSearchToLocalDisplay({
                id: docRef.id,
                ...searchRecord
            });

            // Also refresh from server to ensure consistency
            setTimeout(() => {
                console.log('Refreshing search history from server');
                this.loadSearchHistory();
            }, 500); // Reduced delay for faster UI updates

            return docRef.id;
        } catch (error) {
            console.error('Error saving search:', error);
            throw error;
        }
    }

    // Add a search item to local display immediately for instant feedback
    addSearchToLocalDisplay(searchItem) {
        const historyContainer = document.getElementById('search-history');
        if (!historyContainer) return;

        // Check if history is currently empty
        const noHistory = historyContainer.querySelector('.no-history');
        if (noHistory) {
            // Replace empty state with new item
            this.displaySearchHistory([searchItem]);
            return;
        }

        // Add to existing history list
        const historyList = historyContainer.querySelector('.history-list');
        if (historyList) {
            const date = searchItem.searchDate ? new Date(searchItem.searchDate).toLocaleDateString() : 'Just now';
            const time = searchItem.searchTime || new Date().toLocaleTimeString();

            const newItemHTML = `
                <div class="history-item new-item" data-id="${searchItem.id}">
                    <div class="history-main">
                        <div class="history-route">
                            <div class="route-points">
                                <div class="route-point start">
                                    <i class="fas fa-circle"></i>
                                    <span>${searchItem.startingAddress}</span>
                                </div>
                                <div class="route-arrow">
                                    <i class="fas fa-arrow-down"></i>
                                </div>
                                <div class="route-point end">
                                    <i class="fas fa-map-marker-alt"></i>
                                    <span>${searchItem.destination}</span>
                                </div>
                            </div>
                        </div>
                        <div class="history-details">
                            <div class="detail-item">
                                <i class="fas fa-route"></i>
                                <span>${searchItem.distance}</span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-clock"></i>
                                <span>${searchItem.duration}</span>
                            </div>
                            ${searchItem.carbonEstimate ? `
                                <div class="detail-item eco">
                                    <i class="fas fa-leaf"></i>
                                    <span>${searchItem.carbonEstimate} kg CO₂</span>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="history-meta">
                        <div class="history-timestamp">
                            <i class="fas fa-calendar"></i>
                            <span>${date} at ${time}</span>
                        </div>
                        <div class="history-actions">
                            <button class="btn-icon repeat-search" title="Repeat this search" data-id="${searchItem.id}">
                                <i class="fas fa-redo"></i>
                            </button>
                            <button class="btn-icon delete-search" title="Delete from history" data-id="${searchItem.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;

            historyList.insertAdjacentHTML('afterbegin', newItemHTML);

            // Add event listeners to the new item
            this.attachHistoryEventListeners();

            // Add visual feedback for new item
            setTimeout(() => {
                const newItem = historyList.querySelector('.new-item');
                if (newItem) {
                    newItem.classList.remove('new-item');
                }
            }, 2000);
        }
    }

    // Load user's search history from Firestore
    async loadSearchHistory(filters = {}) {
        const user = authManager.getCurrentUser();
        if (!user) {
            console.log('❌ No user authenticated, cannot load search history');
            this.clearLocalHistory();
            return [];
        }

        console.log('🔍 Loading search history for user:', user.email, 'UID:', user.uid);
        if (Object.keys(filters).length > 0) {
            console.log('🔍 Applied filters:', filters);
        }

        try {
            // Try the optimized query first (requires composite index)
            let history = await this.loadSearchHistoryOptimized(user.uid, filters);

            // If optimized query fails due to missing index, fall back to basic query
            if (history === null) {
                console.log('📋 Falling back to basic query (no composite index)');
                history = await this.loadSearchHistoryBasic(user.uid, filters);
            }

            console.log(`✅ Successfully loaded ${history.length} search history items`);

            if (history.length === 0) {
                console.log('⚠️ No history items found. Possible reasons:');
                console.log('   - User has no saved searches');
                console.log('   - Applied filters are too restrictive');
                console.log('   - UID mismatch between saved data and current user');
                console.log('   - Firestore security rules blocking access');
                console.log('   - Data saved with different field names');
            }

            this.displaySearchHistory(history);
            return history;

        } catch (error) {
            console.error('❌ Error loading search history:', error);
            console.error('Error details:', {
                code: error.code,
                message: error.message,
                stack: error.stack
            });
            this.displaySearchHistory([]);
            return [];
        }
    }

    // Optimized query with composite index (userId + timestamp or userId + vehicleType + timestamp)
    async loadSearchHistoryOptimized(userId, filters = {}) {
        try {
            // Build query based on available filters
            // Note: Firestore allows only one inequality filter per query
            // We use equality filters + orderBy which requires composite index

            let q;
            const queryConstraints = [
                collection(db, this.collectionName),
                where('userId', '==', userId)  // Always filter by userId (equality)
            ];

            // Add additional equality filters if provided
            // Important: Only equality filters can be combined with orderBy on different field
            if (filters.vehicleType) {
                queryConstraints.push(where('vehicleType', '==', filters.vehicleType));
                console.log('🚗 Adding vehicle type filter:', filters.vehicleType);
            }

            if (filters.routeType) {
                queryConstraints.push(where('routeType', '==', filters.routeType));
                console.log('🛣️ Adding route type filter:', filters.routeType);
            }

            // Add orderBy and limit
            queryConstraints.push(
                orderBy('timestamp', 'desc'),
                limit(this.maxHistoryItems)
            );

            q = query(...queryConstraints);

            console.log('📊 Trying optimized Firestore query:', {
                collection: this.collectionName,
                where: `userId == ${userId}`,
                additionalFilters: Object.keys(filters).length > 0 ? filters : 'none',
                orderBy: 'timestamp desc',
                limit: this.maxHistoryItems,
                note: 'Requires composite index for userId + [filters] + timestamp'
            });

            const querySnapshot = await getDocs(q);
            const history = [];

            querySnapshot.forEach((doc) => {
                const data = doc.data();
                console.log('📄 Found history document:', {
                    id: doc.id,
                    userId: data.userId,
                    userEmail: data.userEmail,
                    startingAddress: data.startingAddress,
                    destination: data.destination,
                    vehicleType: data.vehicleType,
                    timestamp: data.timestamp
                });

                history.push({
                    id: doc.id,
                    ...data
                });
            });

            return history;

        } catch (error) {
            // Check if this is an index-related error
            if (error.code === 'failed-precondition' && error.message.includes('index')) {
                console.log('⚠️ Composite index not available for this query, will try basic query');
                return null; // Signal to try fallback
            }
            throw error; // Re-throw other errors
        }
    }

    // Basic query without composite index (less efficient but works)
    async loadSearchHistoryBasic(userId, filters = {}) {
        try {
            // Query only by userId (equality filter), then filter and sort in memory
            // This approach works without any composite indexes
            const q = query(
                collection(db, this.collectionName),
                where('userId', '==', userId)
            );

            console.log('📊 Using basic Firestore query:', {
                collection: this.collectionName,
                where: `userId == ${userId}`,
                filters: Object.keys(filters).length > 0 ? filters : 'none',
                note: 'Will filter and sort in memory (no index required)'
            });

            const querySnapshot = await getDocs(q);
            let history = [];

            querySnapshot.forEach((doc) => {
                const data = doc.data();
                history.push({
                    id: doc.id,
                    ...data
                });
            });

            // Apply filters in memory
            if (Object.keys(filters).length > 0) {
                history = history.filter(item => {
                    // Apply vehicle type filter
                    if (filters.vehicleType && item.vehicleType !== filters.vehicleType) {
                        return false;
                    }

                    // Apply route type filter
                    if (filters.routeType && item.routeType !== filters.routeType) {
                        return false;
                    }

                    return true;
                });

                console.log(`🔍 Applied filters in memory, ${history.length} items match`);
            }

            // Sort by timestamp in memory (most recent first)
            history.sort((a, b) => {
                const timestampA = a.timestamp?.toDate?.() || new Date(a.searchDate || 0);
                const timestampB = b.timestamp?.toDate?.() || new Date(b.searchDate || 0);
                return timestampB - timestampA;
            });

            // Limit to maxHistoryItems
            return history.slice(0, this.maxHistoryItems);

        } catch (error) {
            console.error('❌ Basic query also failed:', error);
            throw error;
        }
    }
    
    // Display search history in the UI
    displaySearchHistory(history) {
        const historyContainer = document.getElementById('search-history');
        if (!historyContainer) {
            console.log('Search history container not found');
            return;
        }

        console.log('Displaying search history:', history.length, 'items');

        if (history.length === 0) {
            historyContainer.innerHTML = `
                <div class="no-history">
                    <i class="fas fa-history"></i>
                    <p>No search history yet</p>
                    <small>Your route searches will appear here</small>
                </div>
            `;
            return;
        }
        
        const historyHTML = history.map(item => {
            const date = item.searchDate ? new Date(item.searchDate).toLocaleDateString() : 'Unknown date';
            const time = item.searchTime || 'Unknown time';
            
            return `
                <div class="history-item" data-id="${item.id}">
                    <div class="history-main">
                        <div class="history-route">
                            <div class="route-points">
                                <div class="route-point start">
                                    <i class="fas fa-circle"></i>
                                    <span>${item.startingAddress}</span>
                                </div>
                                <div class="route-arrow">
                                    <i class="fas fa-arrow-down"></i>
                                </div>
                                <div class="route-point end">
                                    <i class="fas fa-map-marker-alt"></i>
                                    <span>${item.destination}</span>
                                </div>
                            </div>
                        </div>
                        <div class="history-details">
                            <div class="detail-item">
                                <i class="fas fa-route"></i>
                                <span>${item.distance}</span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-clock"></i>
                                <span>${item.duration}</span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-car"></i>
                                <span>${this.getVehicleDisplayName(item.vehicleType || 'car')}</span>
                            </div>
                            ${item.carbonEstimate ? `
                                <div class="detail-item eco">
                                    <i class="fas fa-leaf"></i>
                                    <span>${item.carbonEstimate} kg CO₂</span>
                                </div>
                            ` : ''}
                            ${item.ecoScore ? `
                                <div class="detail-item eco-score">
                                    <i class="fas fa-star"></i>
                                    <span>Eco Score: ${item.ecoScore}/100</span>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="history-meta">
                        <div class="history-timestamp">
                            <i class="fas fa-calendar"></i>
                            <span>${date} at ${time}</span>
                        </div>
                        <div class="history-actions">
                            <button class="btn-icon repeat-search" title="Repeat this search" data-id="${item.id}">
                                <i class="fas fa-redo"></i>
                            </button>
                            <button class="btn-icon delete-search" title="Delete from history" data-id="${item.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        historyContainer.innerHTML = `
            <div class="history-header">
                <h3><i class="fas fa-history"></i> Search History</h3>
                <div class="history-controls">
                    <div class="history-filters">
                        <select id="history-vehicle-filter" class="filter-select">
                            <option value="">All Vehicles</option>
                            <option value="car">Car</option>
                            <option value="motorcycle">Motorcycle</option>
                            <option value="bicycle">Bicycle</option>
                            <option value="electric_car">Electric Car</option>
                            <option value="hybrid">Hybrid Car</option>
                        </select>
                        <select id="history-route-filter" class="filter-select">
                            <option value="">All Routes</option>
                            <option value="fastest">Fastest</option>
                            <option value="shortest">Shortest</option>
                            <option value="eco">Eco-Friendly</option>
                        </select>
                        <button id="clear-filters" class="btn btn-outline btn-sm">
                            <i class="fas fa-filter"></i> Clear Filters
                        </button>
                    </div>
                    <button id="clear-all-history" class="btn btn-outline btn-sm">
                        <i class="fas fa-trash-alt"></i> Clear All
                    </button>
                </div>
            </div>
            <div class="history-list">
                ${historyHTML}
            </div>
        `;
        
        // Add event listeners
        this.attachHistoryEventListeners();
    }
    
    // Attach event listeners to history items
    attachHistoryEventListeners() {
        // Repeat search buttons
        document.querySelectorAll('.repeat-search').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemId = e.target.closest('.repeat-search').dataset.id;
                this.repeatSearch(itemId);
            });
        });
        
        // Delete search buttons
        document.querySelectorAll('.delete-search').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemId = e.target.closest('.delete-search').dataset.id;
                this.deleteSearch(itemId);
            });
        });
        
        // Clear all history button
        const clearAllBtn = document.getElementById('clear-all-history');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => this.clearAllHistory());
        }

        // Filter controls
        const vehicleFilter = document.getElementById('history-vehicle-filter');
        const routeFilter = document.getElementById('history-route-filter');
        const clearFiltersBtn = document.getElementById('clear-filters');

        if (vehicleFilter) {
            vehicleFilter.addEventListener('change', () => this.applyFilters());
        }

        if (routeFilter) {
            routeFilter.addEventListener('change', () => this.applyFilters());
        }

        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }
    }
    
    // Repeat a previous search
    async repeatSearch(itemId) {
        try {
            const history = await this.loadSearchHistory();
            const searchItem = history.find(item => item.id === itemId);
            
            if (searchItem) {
                // Fill in the search form
                const sourceInput = document.getElementById('source');
                const destinationInput = document.getElementById('destination');
                const routeTypeSelect = document.getElementById('route-type');
                const vehicleTypeSelect = document.getElementById('vehicle-type');
                const avoidTollsCheckbox = document.getElementById('avoid-tolls');
                const avoidHighwaysCheckbox = document.getElementById('avoid-highways');

                if (sourceInput) sourceInput.value = searchItem.startingAddress;
                if (destinationInput) destinationInput.value = searchItem.destination;
                if (routeTypeSelect) routeTypeSelect.value = searchItem.routeType || 'fastest';
                if (vehicleTypeSelect) vehicleTypeSelect.value = searchItem.vehicleType || 'car';
                if (avoidTollsCheckbox) avoidTollsCheckbox.checked = searchItem.avoidTolls || false;
                if (avoidHighwaysCheckbox) avoidHighwaysCheckbox.checked = searchItem.avoidHighways || false;

                // Switch to route planning section
                const routeTab = document.querySelector('[data-section="route"]');
                if (routeTab) {
                    routeTab.click();
                }

                // Trigger route calculation if the main app is available
                if (window.trafficApp && window.trafficApp.getRoute) {
                    setTimeout(() => {
                        window.trafficApp.getRoute();
                    }, 100);
                }

                console.log('Repeated search:', searchItem);
            }
        } catch (error) {
            console.error('Error repeating search:', error);
        }
    }
    
    // Delete a single search from history
    async deleteSearch(itemId) {
        try {
            await deleteDoc(doc(db, this.collectionName, itemId));
            console.log('Search deleted:', itemId);
            
            // Reload history
            this.loadSearchHistory();
        } catch (error) {
            console.error('Error deleting search:', error);
        }
    }
    
    // Clear all search history for current user
    async clearAllHistory() {
        const user = authManager.getCurrentUser();
        if (!user) return;
        
        if (!confirm('Are you sure you want to clear all search history? This action cannot be undone.')) {
            return;
        }
        
        try {
            const q = query(
                collection(db, this.collectionName),
                where('userId', '==', user.uid)
            );
            
            const querySnapshot = await getDocs(q);
            const deletePromises = [];
            
            querySnapshot.forEach((document) => {
                deletePromises.push(deleteDoc(doc(db, this.collectionName, document.id)));
            });
            
            await Promise.all(deletePromises);
            console.log('All search history cleared');
            
            // Reload history (will show empty state)
            this.loadSearchHistory();
        } catch (error) {
            console.error('Error clearing search history:', error);
        }
    }

    // Get display name for vehicle type
    getVehicleDisplayName(vehicleType) {
        const vehicleNames = {
            'car': 'Car',
            'motorcycle': 'Motorcycle',
            'bicycle': 'Bicycle',
            'electric_car': 'Electric Car',
            'hybrid': 'Hybrid Car'
        };
        return vehicleNames[vehicleType] || 'Car';
    }

    // Apply current filters to search history
    async applyFilters() {
        const vehicleFilter = document.getElementById('history-vehicle-filter');
        const routeFilter = document.getElementById('history-route-filter');

        const filters = {};

        if (vehicleFilter && vehicleFilter.value) {
            filters.vehicleType = vehicleFilter.value;
        }

        if (routeFilter && routeFilter.value) {
            filters.routeType = routeFilter.value;
        }

        console.log('🔍 Applying filters:', filters);
        await this.loadSearchHistory(filters);
    }

    // Clear all filters
    async clearFilters() {
        const vehicleFilter = document.getElementById('history-vehicle-filter');
        const routeFilter = document.getElementById('history-route-filter');

        if (vehicleFilter) vehicleFilter.value = '';
        if (routeFilter) routeFilter.value = '';

        console.log('🔍 Clearing all filters');
        await this.loadSearchHistory();
    }

    // Clear local history display
    clearLocalHistory() {
        const historyContainer = document.getElementById('search-history');
        if (historyContainer) {
            historyContainer.innerHTML = `
                <div class="no-history">
                    <i class="fas fa-sign-in-alt"></i>
                    <p>Sign in to view your search history</p>
                    <small>Your route searches will be saved and synced across devices</small>
                </div>
            `;
        }
    }
}

// Create global search history manager instance
const searchHistoryManager = new SearchHistoryManager();

// Export for use in other modules
export default searchHistoryManager;

// Make available globally for backward compatibility
window.searchHistoryManager = searchHistoryManager;
