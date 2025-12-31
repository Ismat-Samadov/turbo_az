#!/bin/bash

# GitHub Secrets Setup Script for Turbo.az Scraper
# This script reads environment variables from .env file and sets them as GitHub repository secrets

set -e  # Exit on error

echo "=================================="
echo "GitHub Secrets Setup"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file in the project root directory"
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo ""
    echo "Install GitHub CLI:"
    echo "  macOS: brew install gh"
    echo "  Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo "  Windows: https://github.com/cli/cli/releases"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub"
    echo ""
    echo "Please authenticate first:"
    echo "  gh auth login -h github.com --web"
    exit 1
fi

echo "✓ Found .env file"
echo "✓ GitHub CLI is installed"
echo "✓ Authenticated with GitHub"
echo ""

# Extract repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo "❌ Error: Not in a git repository or no remote configured"
    exit 1
fi

echo "Repository: $REPO"
echo ""

# Function to set a secret from .env file
set_secret_from_env() {
    local key=$1
    local value=$(grep "^${key}=" .env | cut -d '=' -f2-)

    if [ -z "$value" ]; then
        echo "⚠️  Warning: $key not found in .env file, skipping"
        return 1
    fi

    echo "Setting secret: $key"
    echo -n "$value" | gh secret set "$key"

    if [ $? -eq 0 ]; then
        echo "✓ Successfully set $key"
        return 0
    else
        echo "❌ Failed to set $key"
        return 1
    fi
}

echo "Setting GitHub repository secrets..."
echo ""

# Set scraping configuration secrets
set_secret_from_env "START_PAGE"
echo ""

set_secret_from_env "END_PAGE"
echo ""

set_secret_from_env "BASE_URL"
echo ""

set_secret_from_env "MAX_CONCURRENT"
echo ""

set_secret_from_env "DELAY"
echo ""

set_secret_from_env "AUTO_SAVE_INTERVAL"
echo ""

# Set proxy secret
set_secret_from_env "PROXY_URL"
echo ""

# Set database secret
set_secret_from_env "DATABASE_URL"
echo ""

echo "=================================="
echo "Secrets Setup Complete"
echo "=================================="
echo ""
echo "Verify secrets were set:"
echo "  gh secret list"
echo ""
echo "Next steps:"
echo "1. Push code to GitHub: git push origin master"
echo "2. Verify workflow: gh workflow view scraper.yml"
echo "3. Trigger manual run: gh workflow run scraper.yml"
echo "4. Check run status: gh run list --workflow=scraper.yml"
echo ""
