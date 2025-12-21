#!/bin/bash
# XFactor Bot - GitLab Deployment
# Deploy to: https://gitlab-master.nvidia.com/cvanthin/000_trading

set -e

LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LOCAL_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      XFactor Bot - GitLab Deployment Preparation           ║"
echo "║                     Version: 1.0.9                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Build research version frontend
echo "🔨 Step 1: Building frontend..."
cd "$LOCAL_DIR/frontend"
VITE_DEMO_MODE=true npm run build
echo "✅ Frontend built"
cd "$LOCAL_DIR"
echo ""

# Step 2: Copy build to releases folder
echo "📦 Step 2: Copying build to releases/1.0.9/research-build..."
mkdir -p releases/1.0.9/research-build
rm -rf releases/1.0.9/research-build/*
cp -r frontend/dist/* releases/1.0.9/research-build/
echo "✅ Build copied"
echo ""

# Step 3: Create GitLab-specific .gitlab-ci.yml if not exists
if [ ! -f ".gitlab-ci.yml" ]; then
    echo "📝 Step 3: Creating .gitlab-ci.yml for GitLab Pages..."
    cat > .gitlab-ci.yml << 'CIFILE'
# XFactor Bot - GitLab CI/CD Configuration

stages:
  - build
  - deploy

variables:
  NODE_VERSION: "20"
  PYTHON_VERSION: "3.11"

build:
  stage: build
  image: node:${NODE_VERSION}
  script:
    - cd frontend
    - npm ci
    - VITE_DEMO_MODE=true npm run build
  artifacts:
    paths:
      - frontend/dist/
    expire_in: 1 hour

pages:
  stage: deploy
  dependencies:
    - build
  script:
    - mkdir -p public
    - cp -r frontend/dist/* public/
  artifacts:
    paths:
      - public
  only:
    - main
    - master
CIFILE
    echo "✅ .gitlab-ci.yml created"
else
    echo "ℹ️  Step 3: .gitlab-ci.yml already exists, skipping"
fi
echo ""

# Step 4: Instructions
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          📋 GitLab Deployment Instructions                 ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Option 1: Push to GitLab (uses CI/CD)                     ║"
echo "║  ─────────────────────────────────────────────────         ║"
echo "║  git remote add gitlab git@gitlab-master.nvidia.com:       ║"
echo "║                        cvanthin/000_trading.git            ║"
echo "║  git push gitlab main                                      ║"
echo "║                                                            ║"
echo "║  Option 2: Deploy to foresight.nvidia.com                  ║"
echo "║  ─────────────────────────────────────────────────         ║"
echo "║  SSH_PASS='pass' ./scripts/deploy-foresight.sh             ║"
echo "║                                                            ║"
echo "║  Option 3: Manual deployment                               ║"
echo "║  ─────────────────────────────────────────────────         ║"
echo "║  1. Copy releases/1.0.9/research-build/* to server         ║"
echo "║  2. Serve with nginx/apache at port 9876                   ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Build ready at: releases/1.0.9/research-build/"
echo ""

# Rebuild standard version for localhost
echo "🔄 Rebuilding standard version for localhost..."
cd "$LOCAL_DIR/frontend"
npm run build > /dev/null 2>&1
echo "✅ Standard version restored to frontend/dist/"
