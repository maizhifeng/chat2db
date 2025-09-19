// API client for Chat2DB backend
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

// Query natural language to SQL
export async function query(nl) {
  return apiRequest('/query', {
    method: 'POST',
    body: JSON.stringify({ query: nl }),
  });
}

// Chat with AI model
export async function chat(message, history = [], model) {
  const payload = { message, history };
  if (model) payload.model = model;
  
  return apiRequest('/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// Get available models
export async function getModels() {
  return apiRequest('/models');
}

// Encode text to embeddings
export async function encodeText(text) {
  return apiRequest('/embeddings/encode', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

// Calculate similarity between two texts
export async function calculateSimilarity(text1, text2) {
  return apiRequest('/embeddings/similarity', {
    method: 'POST',
    body: JSON.stringify({ text1, text2 }),
  });
}