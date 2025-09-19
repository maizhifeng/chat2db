// Auth service for handling authentication
import { user, isAuthenticated } from '../stores.js';

const API_BASE = import.meta.env.DEV ? 'http://localhost:5001/api' : '/api';

// Helper function to make HTTP requests
async function apiRequest(url, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };
  
  const response = await fetch(`${API_BASE}${url}`, mergedOptions);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// Register a new user
export async function register(username, email, password) {
  try {
    const userData = await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
    
    user.set(userData);
    return userData;
  } catch (error) {
    throw new Error(`Registration failed: ${error.message}`);
  }
}

// Login user
export async function login(username, password) {
  try {
    const authData = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    // Assuming the response contains user data and token
    user.set(authData.user || authData);
    return authData;
  } catch (error) {
    throw new Error(`Login failed: ${error.message}`);
  }
}

// Logout user
export function logout() {
  user.set(null);
}

// Get current user
export async function getCurrentUser() {
  try {
    const userData = await apiRequest('/auth/me', {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    user.set(userData);
    return userData;
  } catch (error) {
    user.set(null);
    throw new Error(`Failed to get current user: ${error.message}`);
  }
}

// Get auth token from store or storage
function getAuthToken() {
  // In a real implementation, you would get this from localStorage or a store
  // For now, we'll return null
  return null;
}