/**
 * Main Application Entry Point
 * Handles dependency injection setup and application initialization
 */

class FaceRekonApp {
    constructor() {
        this.faceService = null;
        this.faceListComponent = null;
        this.isInitialized = false;
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('Initializing Face Recognition UI...');

            // Check if required globals are available
            this.validateDependencies();

            // Initialize services with dependency injection
            this.initializeServices();

            // Initialize components
            this.initializeComponents();

            // Set up global event listeners
            this.setupGlobalEventListeners();

            // Initial health check
            await this.performHealthCheck();

            // Load initial data
            await this.loadInitialData();

            this.isInitialized = true;
            console.log('Face Recognition UI initialized successfully');

        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.showInitializationError(error);
        }
    }

    /**
     * Validate that all required dependencies are available
     */
    validateDependencies() {
        const requiredGlobals = ['FaceService', 'FaceListComponent', 'FaceHelpers'];
        const missing = requiredGlobals.filter(global => !window[global]);

        if (missing.length > 0) {
            throw new Error(`Missing required dependencies: ${missing.join(', ')}`);
        }
    }

    /**
     * Initialize services with dependency injection
     */
    initializeServices() {
        // Initialize face service
        this.faceService = new window.FaceService();

        console.log('Services initialized');
    }

    /**
     * Initialize UI components
     */
    initializeComponents() {
        // Initialize face list component with dependency injection
        this.faceListComponent = new window.FaceListComponent(
            this.faceService,
            window.FaceHelpers
        );

        console.log('Components initialized');
    }

    /**
     * Set up global event listeners
     */
    setupGlobalEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.handleRefreshClick());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Handle visibility change to auto-refresh when tab becomes visible
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());

        console.log('Global event listeners set up');
    }

    /**
     * Perform initial health check
     */
    async performHealthCheck() {
        try {
            const isHealthy = await this.faceService.isHealthy();

            if (!isHealthy) {
                throw new Error('Face recognition service is not responding');
            }

            console.log('Health check passed');
            window.FaceHelpers.showNotification('Connected to face recognition service', 'success', 3000);

        } catch (error) {
            console.warn('Health check failed:', error.message);
            window.FaceHelpers.showNotification(
                'Warning: Face recognition service may not be available',
                'error',
                5000
            );
        }
    }

    /**
     * Load initial face data
     */
    async loadInitialData() {
        console.log('Loading initial face data...');
        await this.faceListComponent.refresh();
    }

    /**
     * Handle refresh button click
     */
    async handleRefreshClick() {
        console.log('Manual refresh requested');
        window.FaceHelpers.showNotification('Refreshing face list...', 'info', 2000);
        await this.faceListComponent.refresh();
    }

    /**
     * Handle keyboard shortcuts
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyboardShortcuts(e) {
        // Ctrl+R or Cmd+R for refresh (prevent default browser refresh)
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            this.handleRefreshClick();
        }

        // F5 for refresh
        if (e.key === 'F5') {
            e.preventDefault();
            this.handleRefreshClick();
        }
    }

    /**
     * Handle visibility change (when user switches tabs)
     */
    handleVisibilityChange() {
        if (!document.hidden && this.isInitialized) {
            // Tab became visible, auto-refresh if it's been a while
            const lastRefresh = this.faceListComponent.lastRefreshTime || 0;
            const now = Date.now();
            const timeSinceRefresh = now - lastRefresh;

            // Auto-refresh if more than 5 minutes have passed
            if (timeSinceRefresh > 5 * 60 * 1000) {
                console.log('Auto-refreshing due to tab visibility change');
                this.faceListComponent.refresh();
            }
        }
    }

    /**
     * Show initialization error
     * @param {Error} error - The initialization error
     */
    showInitializationError(error) {
        const errorHtml = `
            <div style="
                padding: 20px;
                margin: 20px;
                background: #fed7d7;
                border: 1px solid #fc8181;
                border-radius: 6px;
                color: #742a2a;
                text-align: center;
            ">
                <h3>Failed to Initialize Application</h3>
                <p><strong>Error:</strong> ${error.message}</p>
                <p>Please refresh the page and try again. If the problem persists, check the browser console for more details.</p>
                <button onclick="window.location.reload()" style="
                    background: #e53e3e;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 10px;
                ">Reload Page</button>
            </div>
        `;

        const container = document.querySelector('.container') || document.body;
        container.innerHTML = errorHtml;
    }

    /**
     * Get application status information
     * @returns {object} Status information
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            faceService: !!this.faceService,
            faceListComponent: !!this.faceListComponent,
            facesLoaded: this.faceListComponent ? this.faceListComponent.getFaces().length : 0
        };
    }

    /**
     * Manually trigger a refresh of all data
     */
    async refreshAll() {
        if (!this.isInitialized) {
            console.warn('Application not initialized yet');
            return;
        }

        try {
            await this.performHealthCheck();
            await this.faceListComponent.refresh();
        } catch (error) {
            console.error('Error during manual refresh:', error);
            window.FaceHelpers.showNotification(`Refresh failed: ${error.message}`, 'error');
        }
    }
}

// Application instance
let app;

/**
 * Initialize application when DOM is ready
 */
function initializeApp() {
    app = new FaceRekonApp();
    app.init().catch(error => {
        console.error('Critical application error:', error);
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // DOM is already ready
    initializeApp();
}

// Make app available globally for debugging
window.FaceRekonApp = app;

// Auto-refresh every 30 seconds if page is visible
setInterval(() => {
    if (!document.hidden && app && app.isInitialized) {
        console.log('Auto-refresh interval triggered');
        app.faceListComponent.refresh().catch(error => {
            console.warn('Auto-refresh failed:', error.message);
        });
    }
}, 30000);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FaceRekonApp;
}
