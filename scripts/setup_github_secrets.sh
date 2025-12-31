#!/bin/bash

# Setup GitHub Secrets via CLI
# This script sets up the required secrets for GitHub Actions

set -e

echo "=================================================="
echo "GitHub Secrets Setup for Turbo.az Scraper"
echo "=================================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    echo "Or run: brew install gh"
    exit 1
fi

echo "✅ GitHub CLI is installed"
echo ""

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "⚠️  You're not authenticated with GitHub CLI"
    echo "Running: gh auth login"
    echo ""
    gh auth login
fi

echo "✅ Authenticated with GitHub"
echo ""

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [ -z "$REPO" ]; then
    echo "⚠️  Not in a GitHub repository directory"
    echo "Please provide your repository (e.g., username/turbo_az):"
    read -r REPO
fi

echo "📦 Repository: $REPO"
echo ""

# Read DATABASE_URL from .env if exists
if [ -f .env ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" .env | cut -d '=' -f2-)
    PROXY_URL=$(grep "^PROXY_URL=" .env | cut -d '=' -f2-)
else
    echo "⚠️  .env file not found"
fi

# Set DATABASE_URL
echo "=================================================="
echo "Setting DATABASE_URL secret"
echo "=================================================="
echo ""

if [ -n "$DATABASE_URL" ]; then
    echo "Found DATABASE_URL in .env file"
    echo "Using: ${DATABASE_URL:0:50}..."
else
    echo "Enter DATABASE_URL:"
    echo "(PostgreSQL connection string)"
    read -r DATABASE_URL
fi

echo "$DATABASE_URL" | gh secret set DATABASE_URL --repo "$REPO"
echo "✅ DATABASE_URL secret set"
echo ""

# Set PROXY_URL
echo "=================================================="
echo "Setting PROXY_URL secret"
echo "=================================================="
echo ""

if [ -n "$PROXY_URL" ]; then
    echo "Found PROXY_URL in .env file"
    echo "Using: ${PROXY_URL:0:50}..."
else
    echo "Enter PROXY_URL:"
    echo "(BrightData proxy URL)"
    read -r PROXY_URL
fi

echo "$PROXY_URL" | gh secret set PROXY_URL --repo "$REPO"
echo "✅ PROXY_URL secret set"
echo ""

# Verify secrets
echo "=================================================="
echo "Verifying secrets"
echo "=================================================="
echo ""

gh secret list --repo "$REPO"

echo ""
echo "=================================================="
echo "✅ All secrets configured successfully!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add scraper with GitHub Actions'"
echo "   git push origin master"
echo ""
echo "2. Go to GitHub Actions tab to see workflows"
echo ""
echo "3. Trigger a manual run to test:"
echo "   gh workflow run scraper.yml"
echo ""
echo "=================================================="
