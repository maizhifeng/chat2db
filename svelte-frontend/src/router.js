import { writable } from 'svelte/store';

// Current route store
export const currentRoute = writable('/');

// Navigation function
export function navigateTo(path) {
  currentRoute.set(path);
  // Update browser history
  window.history.pushState({}, '', path);
}

// Route definitions
export const routes = {
  DASHBOARD: '/',
  QUERY: '/query',
  AI_ASSISTANT: '/ai-assistant',
  SQL_EDITOR: '/sql-editor',
  DATA_BROWSER: '/data-browser',
  CONNECTIONS: '/connections',
  TABLES: '/tables',
  LOGIN: '/login',
  REGISTER: '/register'
};