#!/bin/bash

# Script to validate and install Svelte frontend dependencies

set -e

echo "Validating Svelte frontend dependencies..."

# Check if we're in the right directory
if [ ! -d "svelte-frontend" ]; then
    echo "Error: svelte-frontend directory not found"
    exit 1
fi

cd svelte-frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found"
    exit 1
fi

echo "Installing dependencies..."
npm install

echo "Dependencies installed successfully!"

# Try to run a simple build to verify everything works
echo "Running a test build..."
npm run build

echo "Test build completed successfully!"

echo "Svelte frontend dependencies validation completed!"