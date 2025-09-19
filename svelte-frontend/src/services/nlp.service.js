// NLP service for handling natural language processing
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

// Convert natural language to SQL
export async function nlToSql(nlQuery) {
  try {
    const result = await apiRequest('/nl2sql', {
      method: 'POST',
      body: JSON.stringify({ query: nlQuery }),
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    return result;
  } catch (error) {
    throw new Error(`Failed to convert NL to SQL: ${error.message}`);
  }
}

// Chat with AI model
export async function chatWithAI(message, history = [], model) {
  try {
    const payload = { message, history };
    if (model) payload.model = model;
    
    const result = await apiRequest('/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    return result;
  } catch (error) {
    throw new Error(`Failed to chat with AI: ${error.message}`);
  }
}

// Get available models
export async function getModels() {
  try {
    const models = await apiRequest('/models');
    return models;
  } catch (error) {
    throw new Error(`Failed to get models: ${error.message}`);
  }
}

// Get auth token from store or storage
function getAuthToken() {
  // In a real implementation, you would get this from localStorage or a store
  // For now, we'll return null
  return null;
}