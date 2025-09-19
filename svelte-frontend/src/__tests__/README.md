# Testing

This project uses Vitest for unit testing Svelte components.

## Running Tests

To run tests in watch mode:
```bash
npm run test
```

To run tests once:
```bash
npm run test:run
```

To run tests with UI:
```bash
npm run test:ui
```

## Test Structure

Tests are located in the `src/__tests__` directory and use:
- Vitest as the test runner
- Testing Library for Svelte components
- JSDOM as the test environment

## Writing Tests

Tests should focus on:
1. Component rendering
2. User interactions
3. State management
4. API integration (mocked)