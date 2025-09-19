// Table service for handling table operations
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

// Get table schema
export async function getTableSchema(connectionId, tableName) {
  try {
    const schema = await apiRequest(`/connections/${connectionId}/tables/${tableName}`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    return schema;
  } catch (error) {
    throw new Error(`Failed to get table schema: ${error.message}`);
  }
}

// Query table data
export async function queryTableData(connectionId, tableName, options = {}) {
  try {
    const data = await apiRequest(`/connections/${connectionId}/tables/${tableName}/query`, {
      method: 'POST',
      body: JSON.stringify(options),
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    return data;
  } catch (error) {
    throw new Error(`Failed to query table data: ${error.message}`);
  }
}

// Get auth token from store or storage
function getAuthToken() {
  // In a real implementation, you would get this from localStorage or a store
  // For now, we'll return null
  return null;
}