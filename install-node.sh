#!/bin/bash

# Script to install Node.js and npm using NodeSource repository

set -e

echo "Checking if Node.js is installed..."

if command -v node &> /dev/null; then
    echo "Node.js is already installed:"
    node --version
    npm --version
    exit 0
fi

echo "Node.js not found. Installing..."

# Check if we're on Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "Installing Node.js on Ubuntu/Debian..."
    
    # Install curl if not available
    if ! command -v curl &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y curl
    fi
    
    # Install Node.js via NodeSource
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    echo "Node.js and npm have been installed:"
    node --version
    npm --version
    exit 0
fi

# Check if we're on CentOS/RHEL/Fedora
if command -v yum &> /dev/null || command -v dnf &> /dev/null; then
    echo "Installing Node.js on CentOS/RHEL/Fedora..."
    
    # Install curl if not available
    if ! command -v curl &> /dev/null; then
        if command -v dnf &> /dev/null; then
            sudo dnf install -y curl
        else
            sudo yum install -y curl
        fi
    fi
    
    # Install Node.js via NodeSource
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    
    if command -v dnf &> /dev/null; then
        sudo dnf install -y nodejs
    else
        sudo yum install -y nodejs
    fi
    
    echo "Node.js and npm have been installed:"
    node --version
    npm --version
    exit 0
fi

echo "Unsupported operating system. Please install Node.js manually."
exit 1