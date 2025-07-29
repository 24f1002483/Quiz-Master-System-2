import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth headers
api.interceptors.request.use(
  (config) => {
    // Add authorization header if token exists and is not for auth endpoints
    const token = localStorage.getItem('token');
    const isAuthEndpoint = config.url && (
      config.url.includes('/login') || 
      config.url.includes('/register') || 
      config.url.includes('/refresh') ||
      config.url.includes('/session/status')
    );
    
    if (token && !isAuthEndpoint) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // If the error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Check if we have a refresh token
        const refreshTokenValue = localStorage.getItem('refreshToken');
        if (!refreshTokenValue) {
          // No refresh token, redirect to login
          console.log('No refresh token found, redirecting to login');
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Try to refresh the token using a direct axios call to avoid circular import
        const refreshResponse = await axios.post('http://localhost:5000/refresh', {}, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (refreshResponse.data && refreshResponse.data.access_token) {
          // Store the new tokens
          localStorage.setItem('token', refreshResponse.data.access_token);
          if (refreshResponse.data.refresh_token) {
            localStorage.setItem('refreshToken', refreshResponse.data.refresh_token);
          }
          
          // Update the original request with new token
          originalRequest.headers['Authorization'] = `Bearer ${refreshResponse.data.access_token}`;
          
          // Retry the original request
          return api(originalRequest);
        } else {
          // Refresh failed, redirect to login
          console.log('Token refresh failed, redirecting to login');
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(error);
        }
      } catch (refreshError) {
        // If refresh fails, redirect to login
        console.error('Token refresh failed:', refreshError);
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api; 