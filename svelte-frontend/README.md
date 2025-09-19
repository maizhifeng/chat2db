# Chat2DB Svelte Frontend

This is the Svelte implementation of the Chat2DB frontend, replacing the previous Angular implementation.

## Features

- Natural language to SQL conversion
- Database query execution
- Model selection for AI-powered queries
- Responsive UI with Svelte components

## Development Setup

### Prerequisites

- Node.js (version 16 or higher)
- npm (version 8 or higher)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Project Structure

- `src/` - Main source code
  - `App.svelte` - Main application component
  - `Query.svelte` - Query interface component
  - `api.js` - API client for backend communication
  - `app.css` - Global styles
  - `main.js` - Application entry point
- `src/environments/` - Environment configuration files
- `vite.config.js` - Vite configuration
- `package.json` - Project dependencies and scripts
- `Dockerfile` - Docker configuration for deployment
- `nginx.conf` - Nginx configuration for production

## API Integration

The frontend communicates with the backend API through the following endpoints:

- `/api/query` - Natural language query endpoint
- `/api/chat` - AI chat endpoint
- `/api/models` - Model listing endpoint
- `/api/embeddings/encode` - Text encoding endpoint
- `/api/embeddings/similarity` - Text similarity endpoint

## Docker Deployment

To build and run the application with Docker:

```bash
docker build -t chat2db-svelte-frontend .
docker run -p 3000:80 chat2db-svelte-frontend
```

## Testing

To run tests:

```bash
npm run test
```

The project uses Vitest with jsdom environment for unit testing Svelte components.
