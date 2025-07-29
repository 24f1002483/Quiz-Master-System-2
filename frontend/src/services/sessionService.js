import api from './axiosConfig.js';

class SessionService {
    constructor() {
        this.sessionTimeout = 30 * 60 * 1000; // Default 30 minutes in milliseconds
        this.activityTimer = null;
        this.sessionCheckInterval = null;
        this.lastActivity = Date.now();
        this.isLoggedIn = false;
        this.isPaused = false;
        this.lastSessionCheck = 0;
        this.sessionCheckCooldown = 2 * 60 * 1000; // 2 minutes cooldown between session checks
        
        // Bind methods
        this.resetActivityTimer = this.resetActivityTimer.bind(this);
        this.checkSessionStatus = this.checkSessionStatus.bind(this);
        this.handleLogout = this.handleLogout.bind(this);
        this.startSessionMonitoring = this.startSessionMonitoring.bind(this);
        this.stopSessionMonitoring = this.stopSessionMonitoring.bind(this);
    }

    // Initialize session monitoring
    init() {
        this.setupActivityListeners();
        this.startSessionMonitoring();
    }

    // Setup activity listeners to track user interaction
    setupActivityListeners() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, this.resetActivityTimer, true);
        });
    }

    // Reset activity timer when user is active
    resetActivityTimer() {
        this.lastActivity = Date.now();
        
        // Don't update server activity if paused or during quiz taking
        if (this.isLoggedIn && !this.isPaused && Date.now() - this.lastSessionCheck > this.sessionCheckCooldown) {
            // Check if we're on a quiz page
            const isOnQuizPage = window.location.pathname.includes('/quiz/');
            if (!isOnQuizPage) {
                this.updateServerActivity();
            }
        }
    }

    // Update activity on server
    async updateServerActivity() {
        try {
            this.lastSessionCheck = Date.now();
            const response = await api.get('/session/status');
            
            // Update session timeout from server response
            if (response.data.session_timeout) {
                this.sessionTimeout = response.data.session_timeout * 60 * 1000; // Convert to milliseconds
            }
        } catch (error) {
            console.error('Failed to update server activity:', error);
            // If we can't update server activity, check if session is expired
            if (error.response && error.response.status === 401) {
                this.handleLogout('Session expired. Please login again.');
            }
        }
    }

    // Check session status with server
    async checkSessionStatus() {
        try {
            // Add cooldown to prevent excessive API calls
            if (Date.now() - this.lastSessionCheck < this.sessionCheckCooldown) {
                return true;
            }
            
            // Don't check session status if paused or during quiz taking
            if (this.isPaused) {
                return true; // Skip session check if paused
            }
            
            const isOnQuizPage = window.location.pathname.includes('/quiz/');
            if (isOnQuizPage) {
                return true; // Skip session check during quiz
            }
            
            this.lastSessionCheck = Date.now();
            const response = await api.get('/session/status');
            
            // Update session timeout from server response
            if (response.data.session_timeout) {
                this.sessionTimeout = response.data.session_timeout * 60 * 1000; // Convert to milliseconds
            }
            
            if (response.data.is_expired) {
                this.handleLogout('Session expired due to inactivity');
                return false;
            }
            
            return true;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                this.handleLogout('Session expired. Please login again.');
                return false;
            }
            // For other errors, don't logout immediately, just return true
            console.error('Session check error:', error);
            return true;
        }
    }

    // Handle logout
    handleLogout(message = 'You have been logged out due to inactivity') {
        this.stopSessionMonitoring();
        this.isLoggedIn = false;
        
        // Clear local storage
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        
        // Show notification
        if (message) {
            alert(message);
        }
        
        // Redirect to login page
        window.location.href = '/login';
    }

    // Handle login and set session timeout
    handleLogin(sessionTimeoutMinutes) {
        this.isLoggedIn = true;
        this.sessionTimeout = sessionTimeoutMinutes * 60 * 1000; // Convert to milliseconds
        this.lastActivity = Date.now();
        this.lastSessionCheck = Date.now();
        this.startSessionMonitoring();
    }

    // Pause session monitoring during quiz taking
    pauseSessionMonitoring() {
        this.isPaused = true;
        console.log('Session monitoring paused for quiz taking');
    }

    // Resume session monitoring after quiz
    resumeSessionMonitoring() {
        this.isPaused = false;
        this.lastActivity = Date.now();
        this.lastSessionCheck = Date.now();
        console.log('Session monitoring resumed');
    }

    // Start session monitoring
    startSessionMonitoring() {
        this.isLoggedIn = true;
        
        // Check session status every 10 minutes (increased from 5 minutes)
        this.sessionCheckInterval = setInterval(async () => {
            const isActive = await this.checkSessionStatus();
            if (!isActive) {
                return;
            }
        }, 10 * 60 * 1000); // 10 minutes
        
        // Check for inactivity timeout
        this.activityTimer = setInterval(() => {
            const timeSinceLastActivity = Date.now() - this.lastActivity;
            
            if (timeSinceLastActivity >= this.sessionTimeout) {
                this.handleLogout();
            }
        }, 60000); // Check every minute
    }

    // Stop session monitoring
    stopSessionMonitoring() {
        if (this.sessionCheckInterval) {
            clearInterval(this.sessionCheckInterval);
            this.sessionCheckInterval = null;
        }
        
        if (this.activityTimer) {
            clearInterval(this.activityTimer);
            this.activityTimer = null;
        }
    }

    // Set session timeout (in minutes)
    setSessionTimeout(minutes) {
        this.sessionTimeout = minutes * 60 * 1000;
    }

    // Get remaining session time (in minutes)
    getRemainingTime() {
        const timeSinceLastActivity = Date.now() - this.lastActivity;
        const remainingTime = this.sessionTimeout - timeSinceLastActivity;
        return Math.max(0, Math.floor(remainingTime / 60000)); // Return minutes
    }

    // Cleanup on page unload
    cleanup() {
        this.stopSessionMonitoring();
        
        // Remove event listeners
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        events.forEach(event => {
            document.removeEventListener(event, this.resetActivityTimer, true);
        });
    }
}

// Create singleton instance
const sessionService = new SessionService();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    sessionService.cleanup();
});

export default sessionService; 