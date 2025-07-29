// Authentication Cache Clearer Script
// Run this in your browser console to clear all cached authentication data

console.log('🧹 Starting Authentication Cache Cleanup...');

function clearAuthCache() {
    console.log('📋 Clearing localStorage...');
    
    // Clear all localStorage items
    const localStorageKeys = Object.keys(localStorage);
    console.log(`Found ${localStorageKeys.length} localStorage items`);
    
    localStorageKeys.forEach(key => {
        console.log(`Removing: ${key}`);
        localStorage.removeItem(key);
    });
    
    console.log('📋 Clearing sessionStorage...');
    
    // Clear all sessionStorage items
    const sessionStorageKeys = Object.keys(sessionStorage);
    console.log(`Found ${sessionStorageKeys.length} sessionStorage items`);
    
    sessionStorageKeys.forEach(key => {
        console.log(`Removing: ${key}`);
        sessionStorage.removeItem(key);
    });
    
    console.log('📋 Clearing cookies...');
    
    // Clear all cookies
    document.cookie.split(";").forEach(function(c) { 
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
    });
    
    console.log('✅ Cache cleanup completed!');
    console.log('🔄 Please refresh the page and try logging in again.');
}

function checkAuthStatus() {
    console.log('📊 Current Authentication Status:');
    
    const token = localStorage.getItem('token');
    const refreshToken = localStorage.getItem('refreshToken');
    const user = localStorage.getItem('user');
    
    console.log(`Token: ${token ? '✅ Present' : '❌ Missing'}`);
    console.log(`Refresh Token: ${refreshToken ? '✅ Present' : '❌ Missing'}`);
    console.log(`User Data: ${user ? '✅ Present' : '❌ Missing'}`);
    
    if (token || refreshToken || user) {
        console.log('⚠️ Found cached authentication data - consider clearing cache');
    } else {
        console.log('✅ No cached authentication data found');
    }
}

// Auto-run status check
checkAuthStatus();

// Export functions for manual use
window.clearAuthCache = clearAuthCache;
window.checkAuthStatus = checkAuthStatus;

console.log('💡 Use clearAuthCache() to clear all cache');
console.log('💡 Use checkAuthStatus() to check current status'); 