import api from './axiosConfig.js';
import sessionService from './sessionService.js';

const API_URL = ''; // No prefix - routes are at /login, /register, etc.

export const loginAdmin = async (username, password) => {
  try {
    const response = await api.post(
      `${API_URL}/login`,
      { username, password },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    // Handle login and session monitoring after successful login
    if (response.data.access_token) {
      // Store tokens in localStorage
      localStorage.setItem('token', response.data.access_token);
      if (response.data.refresh_token) {
        localStorage.setItem('refreshToken', response.data.refresh_token);
      }
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      const sessionTimeout = response.data.session_timeout || 30; // Default to 30 minutes
      sessionService.handleLogin(sessionTimeout);
    }
    
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      throw error.response.data;
    }
  }
};

export const registerUser = async (userData) => {
  try {
    const response = await api.post(`${API_URL}/register`, userData);
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      throw error.response.data;
    } else {
      throw { message: "Network error or server not reachable" };
    }
  }
};

export const refreshToken = async () => {
  try {
    const response = await api.post(
      `${API_URL}/refresh`,
      {},
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    // Update session timeout if provided by server
    if (response.data.session_timeout) {
      sessionService.setSessionTimeout(response.data.session_timeout);
    }
    
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      throw error.response.data;
    }
  }
};

export const logoutUser = async () => {
  try {
    await api.post(`${API_URL}/logout`, {});
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Stop session monitoring on logout
    sessionService.stopSessionMonitoring();
    
    // Clear localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }
};

export const checkAuth = async () => {
  try {
    const response = await api.get(`${API_URL}/me`);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};