#!/bin/bash

# Script to validate the Svelte frontend setup

set -e

echo "Validating Svelte frontend setup..."

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

# Check if required files exist
required_files=(
    "vite.config.js"
    "src/main.js"
    "src/App.svelte"
    "src/Query.svelte"
    "src/api.js"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file not found"
        exit 1
    fi
done

echo "All required files are present."

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "Warning: Dockerfile not found"
else
    echo "Dockerfile found."
fi

echo "Svelte frontend setup validation completed successfully!"