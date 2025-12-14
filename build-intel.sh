#!/bin/bash
#
# XFactor Bot - Intel Mac Build Script
# 
# This script builds the x64 DMG on an Intel Mac.
# Run this after extracting the project files.
#
# Usage: ./build-intel.sh
#

set -e  # Exit on error

echo "=============================================="
echo "  XFactor Bot - Intel Mac Build"
echo "=============================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "x86_64" ]; then
    echo "⚠️  Warning: This script is intended for Intel Macs (x86_64)"
    echo "   Current architecture: $ARCH"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Step 1: Check prerequisites
echo "🔍 Checking prerequisites..."

# Check for Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    echo "❌ Xcode Command Line Tools not found"
    echo "   Installing..."
    xcode-select --install
    echo "   Please run this script again after installation completes."
    exit 1
fi
echo "✅ Xcode Command Line Tools"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    echo "   Please install Node.js 18+ from https://nodejs.org/"
    echo "   Or run: brew install node"
    exit 1
fi
NODE_VERSION=$(node -v)
echo "✅ Node.js $NODE_VERSION"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    echo "   Please install Python 3.10+ from https://python.org/"
    echo "   Or run: brew install python@3.12"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# Check for Rust
if ! command -v cargo &> /dev/null; then
    echo "⚠️  Rust not found. Installing..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi
RUST_VERSION=$(rustc --version)
echo "✅ $RUST_VERSION"

echo ""
echo "=============================================="
echo "  Step 1: Setting up Python environment"
echo "=============================================="

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate
echo "✅ Virtual environment activated"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q
echo "✅ Python dependencies installed"

echo ""
echo "=============================================="
echo "  Step 2: Building Python backend"
echo "=============================================="

cd desktop/scripts
python3 build_backend.py --target x86_64-apple-darwin
cd ../..

# Verify backend was built
if [ -f "desktop/src-tauri/binaries/xfactor-backend-x86_64-apple-darwin" ]; then
    BACKEND_SIZE=$(du -h "desktop/src-tauri/binaries/xfactor-backend-x86_64-apple-darwin" | cut -f1)
    echo "✅ Backend built successfully ($BACKEND_SIZE)"
else
    echo "❌ Backend build failed"
    exit 1
fi

echo ""
echo "=============================================="
echo "  Step 3: Building frontend"
echo "=============================================="

cd frontend
npm install --silent
npm run build
cd ..
echo "✅ Frontend built"

echo ""
echo "=============================================="
echo "  Step 4: Building desktop app"
echo "=============================================="

cd desktop
npm install --silent

# Build the Intel DMG
echo "Building Intel DMG (this may take a few minutes)..."
npm run build:mac-intel

cd ..

echo ""
echo "=============================================="
echo "  Build Complete!"
echo "=============================================="

# Find and display the DMG
DMG_PATH=$(find desktop/src-tauri/target/x86_64-apple-darwin/release/bundle/dmg -name "*.dmg" 2>/dev/null | head -1)

if [ -n "$DMG_PATH" ]; then
    DMG_SIZE=$(du -h "$DMG_PATH" | cut -f1)
    echo ""
    echo "✅ DMG created successfully!"
    echo ""
    echo "📦 Location: $DMG_PATH"
    echo "📏 Size: $DMG_SIZE"
    echo ""
    
    # Copy to releases folder
    VERSION=$(grep '"version"' desktop/src-tauri/tauri.conf.json | head -1 | sed 's/.*: "\(.*\)".*/\1/')
    mkdir -p "releases/$VERSION"
    cp "$DMG_PATH" "releases/$VERSION/"
    echo "📁 Copied to: releases/$VERSION/"
    echo ""
    
    # Open the folder
    open "releases/$VERSION/"
else
    echo "❌ DMG not found"
    exit 1
fi

echo "Done! 🎉"

