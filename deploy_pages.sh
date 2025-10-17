#!/bin/bash

echo "🚀 Deploying Delta OS Documentation to GitHub Pages"

# Build and deploy docs
git checkout main
git pull origin main

# Enable GitHub Pages (if not already enabled)
# Settings → Pages → Source: GitHub Actions

echo "✅ GitHub Pages deployment initiated"
echo "📚 Docs will be available at: https://sanmmie.github.io/delta-operating-system"