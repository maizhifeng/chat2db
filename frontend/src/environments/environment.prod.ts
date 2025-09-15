export const environment = {
  production: true,
  // when running inside Docker Compose the backend service is reachable at 'backend:5001'
  apiBase: 'http://backend:5001/api'
};
