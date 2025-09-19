// Connection service for handling database connections
import { connections, currentConnection } from '../stores.js';

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

// Add a new database connection
export async function addConnection(connectionData) {
  try {
    const newConnection = await apiRequest('/connections', {
      method: 'POST',
      body: JSON.stringify(connectionData),
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    // Update the connections store
    connections.update(conns => [...conns, newConnection]);
    return newConnection;
  } catch (error) {
    throw new Error(`Failed to add connection: ${error.message}`);
  }
}

// Get all database connections
export async function getConnections() {
  try {
    const connectionsData = await apiRequest('/connections', {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    connections.set(connectionsData);
    return connectionsData;
  } catch (error) {
    throw new Error(`Failed to get connections: ${error.message}`);
  }
}

// Get a specific database connection by ID
export async function getConnection(id) {
  try {
    const connectionData = await apiRequest(`/connections/${id}`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    return connectionData;
  } catch (error) {
    throw new Error(`Failed to get connection: ${error.message}`);
  }
}

// Update a database connection
export async function updateConnection(id, connectionData) {
  try {
    const updatedConnection = await apiRequest(`/connections/${id}`, {
      method: 'PUT',
      body: JSON.stringify(connectionData),
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    // Update the connections store
    connections.update(conns => 
      conns.map(conn => conn.id === id ? updatedConnection : conn)
    );
    
    // If this is the current connection, update it too
    currentConnection.update(current => 
      current && current.id === id ? updatedConnection : current
    );
    
    return updatedConnection;
  } catch (error) {
    throw new Error(`Failed to update connection: ${error.message}`);
  }
}

// Delete a database connection
export async function deleteConnection(id) {
  try {
    await apiRequest(`/connections/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    // Remove from the connections store
    connections.update(conns => conns.filter(conn => conn.id !== id));
    
    // If this was the current connection, clear it
    currentConnection.update(current => 
      current && current.id === id ? null : current
    );
    
    return true;
  } catch (error) {
    throw new Error(`Failed to delete connection: ${error.message}`);
  }
}

// Test a database connection
export async function testConnection(id) {
  try {
    const result = await apiRequest(`/connections/${id}/test`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    
    return result;
  } catch (error) {
    throw new Error(`Failed to test connection: ${error.message}`);
  }
}

// Set current connection
export function setCurrentConnection(connection) {
  currentConnection.set(connection);
}

// Get auth token from store or storage
function getAuthToken() {
  // In a real implementation, you would get this from localStorage or a store
  // For now, we'll return null
  return null;
}