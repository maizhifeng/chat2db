export const environment = {
  production: true,
  // when running in Docker with nginx proxy, use relative path so browser hits nginx and nginx proxies to backend
  apiBase: '/api'
};
