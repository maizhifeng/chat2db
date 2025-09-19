import { writable, derived } from 'svelte/store';

// User authentication state
export const user = writable(null);
export const isAuthenticated = derived(user, $user => !!$user);

// Database connections
export const connections = writable([]);
export const currentConnection = writable(null);

// Database tables
export const tables = writable([]);
export const currentTable = writable(null);

// AI models
export const models = writable([]);
export const currentModel = writable(null);

// Loading states
export const loading = writable(false);
export const loadingMessage = writable('');

// Error handling
export const error = writable(null);

// Utility function to reset all stores
export function resetStores() {
  user.set(null);
  connections.set([]);
  currentConnection.set(null);
  tables.set([]);
  currentTable.set(null);
  models.set([]);
  currentModel.set(null);
  loading.set(false);
  loadingMessage.set('');
  error.set(null);
}