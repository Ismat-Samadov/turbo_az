# CLI Setup Guide - GitHub Actions via Terminal

Complete guide to set up GitHub Actions using only the command line.

---

## Prerequisites

### 1. Install GitHub CLI

**macOS (already installed for you):**
```bash
brew install gh
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora/CentOS
sudo dnf install gh
```

**Windows:**
```bash
winget install GitHub.cli
```

### 2. Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts:
1. Select: **GitHub.com**
2. Protocol: **HTTPS**
3. Authenticate: **Login with a web browser**
4. Copy the one-time code and paste in browser

---

## Quick Setup (Automated)

### Option 1: Use the Setup Script

We've created an automated script for you:

```bash
# Make it executable (already done)
chmod +x setup_github_secrets.sh

# Run the script
./setup_github_secrets.sh
```

The script will:
- ✅ Check GitHub CLI installation
- ✅ Authenticate if needed
- ✅ Read secrets from .env file
- ✅ Set all required secrets (DATABASE_URL, PROXY_URL, START_PAGE, END_PAGE, BASE_URL, MAX_CONCURRENT, DELAY, AUTO_SAVE_INTERVAL)
- ✅ Verify secrets were set

---

## Manual Setup (Step by Step)

### Step 1: Initialize Git Repository

```bash
# If not already initialized
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Turbo.az scraper with PostgreSQL"
```

### Step 2: Create GitHub Repository

```bash
# Create new repository (replace USERNAME with your GitHub username)
gh repo create turbo_az --public --source=. --remote=origin

# Or if repo already exists, just add remote
git remote add origin https://github.com/USERNAME/turbo_az.git
```

### Step 3: Set GitHub Secrets

#### Method A: From .env file (Recommended)

```bash
# Set all scraping configuration secrets
grep "^START_PAGE=" .env | cut -d '=' -f2- | gh secret set START_PAGE
grep "^END_PAGE=" .env | cut -d '=' -f2- | gh secret set END_PAGE
grep "^BASE_URL=" .env | cut -d '=' -f2- | gh secret set BASE_URL
grep "^MAX_CONCURRENT=" .env | cut -d '=' -f2- | gh secret set MAX_CONCURRENT
grep "^DELAY=" .env | cut -d '=' -f2- | gh secret set DELAY
grep "^AUTO_SAVE_INTERVAL=" .env | cut -d '=' -f2- | gh secret set AUTO_SAVE_INTERVAL

# Set database and proxy secrets
grep "^PROXY_URL=" .env | cut -d '=' -f2- | gh secret set PROXY_URL
grep "^DATABASE_URL=" .env | cut -d '=' -f2- | gh secret set DATABASE_URL
```

#### Method B: Enter Manually

```bash
# Set scraping configuration
gh secret set START_PAGE              # Enter: 1
gh secret set END_PAGE                # Enter: 1770
gh secret set BASE_URL                # Enter: https://turbo.az/autos
gh secret set MAX_CONCURRENT          # Enter: 3
gh secret set DELAY                   # Enter: 1
gh secret set AUTO_SAVE_INTERVAL      # Enter: 50

# Set proxy URL
gh secret set PROXY_URL
# Paste when prompted:
# http://brd-customer-hl_cc079cd9-zone-residential_proxy1:ja1dl6w7jyg1@brd.superproxy.io:33335

# Set database URL
gh secret set DATABASE_URL
# Paste when prompted:
# postgresql://myfrog_me_owner:ErAVlQSW06Ih@ep-red-dew-a22obfoo.eu-central-1.aws.neon.tech/myfrog_me?sslmode=require
```

#### Method C: From Variables

```bash
# Set variables first
START_PAGE="1"
END_PAGE="1770"
BASE_URL="https://turbo.az/autos"
MAX_CONCURRENT="3"
DELAY="1"
AUTO_SAVE_INTERVAL="50"
PROXY_URL="http://brd-customer-hl_cc079cd9-zone-residential_proxy1:ja1dl6w7jyg1@brd.superproxy.io:33335"
DATABASE_URL="postgresql://myfrog_me_owner:ErAVlQSW06Ih@ep-red-dew-a22obfoo.eu-central-1.aws.neon.tech/myfrog_me?sslmode=require"

# Set all secrets
echo "$START_PAGE" | gh secret set START_PAGE
echo "$END_PAGE" | gh secret set END_PAGE
echo "$BASE_URL" | gh secret set BASE_URL
echo "$MAX_CONCURRENT" | gh secret set MAX_CONCURRENT
echo "$DELAY" | gh secret set DELAY
echo "$AUTO_SAVE_INTERVAL" | gh secret set AUTO_SAVE_INTERVAL
echo "$PROXY_URL" | gh secret set PROXY_URL
echo "$DATABASE_URL" | gh secret set DATABASE_URL
```

### Step 4: Verify Secrets

```bash
# List all secrets
gh secret list

# Expected output:
# AUTO_SAVE_INTERVAL  Updated 2025-12-31
# BASE_URL            Updated 2025-12-31
# DATABASE_URL        Updated 2025-12-31
# DELAY               Updated 2025-12-31
# END_PAGE            Updated 2025-12-31
# MAX_CONCURRENT      Updated 2025-12-31
# PROXY_URL           Updated 2025-12-31
# START_PAGE          Updated 2025-12-31
```

### Step 5: Push to GitHub

```bash
# Push code
git push -u origin master

# Or if using main branch
git branch -M main
git push -u origin main
```

---

## Working with GitHub Actions

### View Workflows

```bash
# List all workflows
gh workflow list

# Expected output:
# Turbo.az Scraper  active  12345
```

### Trigger Workflow Manually

```bash
# Trigger with default settings (1-1770 pages)
gh workflow run scraper.yml

# Trigger with custom pages
gh workflow run scraper.yml -f start_page=1 -f end_page=10

# Trigger with specific pages
gh workflow run scraper.yml -f start_page=500 -f end_page=600
```

### View Workflow Runs

```bash
# List recent runs
gh run list --workflow=scraper.yml

# Watch latest run (real-time)
gh run watch

# View specific run logs
gh run view <RUN_ID> --log

# View latest run
gh run view --log
```

### Download Artifacts

```bash
# List artifacts from latest run
gh run view --json artifacts --jq '.artifacts'

# Download scraper logs
gh run download --name scraper-log-<NUMBER>
```

---

## Managing Secrets

### Update Secrets

```bash
# Update DATABASE_URL
echo "NEW_DATABASE_URL" | gh secret set DATABASE_URL

# Update PROXY_URL
echo "NEW_PROXY_URL" | gh secret set PROXY_URL
```

### Delete Secrets

```bash
# Delete a secret
gh secret delete DATABASE_URL

# Delete with confirmation
gh secret delete PROXY_URL --confirm
```

### Set Secrets for Specific Repo

```bash
# If you're not in the repo directory
gh secret set DATABASE_URL --repo USERNAME/turbo_az

# List secrets for specific repo
gh secret list --repo USERNAME/turbo_az
```

---

## Repository Management

### View Repository

```bash
# View repo info
gh repo view

# Open repo in browser
gh repo view --web
```

### Enable/Disable Workflows

```bash
# Enable a workflow
gh workflow enable scraper.yml

# Disable a workflow
gh workflow disable scraper.yml
```

### View Actions Tab

```bash
# Open Actions tab in browser
gh browse --repo USERNAME/turbo_az /actions
```

---

## Complete Setup Commands (Copy-Paste)

Here's the complete sequence to set everything up:

```bash
# 1. Navigate to project
cd /Users/ismatsamadov/turbo_az

# 2. Authenticate with GitHub (if not already)
gh auth login

# 3. Create GitHub repository (if doesn't exist)
gh repo create turbo_az --public --source=. --remote=origin --push

# 4. Set all secrets from .env
grep "^START_PAGE=" .env | cut -d '=' -f2- | gh secret set START_PAGE
grep "^END_PAGE=" .env | cut -d '=' -f2- | gh secret set END_PAGE
grep "^BASE_URL=" .env | cut -d '=' -f2- | gh secret set BASE_URL
grep "^MAX_CONCURRENT=" .env | cut -d '=' -f2- | gh secret set MAX_CONCURRENT
grep "^DELAY=" .env | cut -d '=' -f2- | gh secret set DELAY
grep "^AUTO_SAVE_INTERVAL=" .env | cut -d '=' -f2- | gh secret set AUTO_SAVE_INTERVAL
grep "^PROXY_URL=" .env | cut -d '=' -f2- | gh secret set PROXY_URL
grep "^DATABASE_URL=" .env | cut -d '=' -f2- | gh secret set DATABASE_URL

# 5. Verify secrets
gh secret list

# 6. Push code (if using separate commands)
git add .
git commit -m "Add PostgreSQL scraper with GitHub Actions"
git push -u origin master

# 7. Trigger test run
gh workflow run scraper.yml -f start_page=1 -f end_page=1

# 8. Watch the run
gh run watch

# 9. View logs
gh run view --log
```

---

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate
gh auth logout
gh auth login

# Check auth status
gh auth status
```

### Repository Not Found

```bash
# Check current repo
gh repo view

# Set correct repo
gh repo set-default USERNAME/turbo_az
```

### Secrets Not Working

```bash
# Delete and re-create
gh secret delete DATABASE_URL
gh secret delete PROXY_URL

# Set again
./setup_github_secrets.sh
```

### Workflow Not Running

```bash
# Check workflow status
gh workflow view scraper.yml

# Enable if disabled
gh workflow enable scraper.yml

# Check recent runs
gh run list --workflow=scraper.yml --limit 5
```

---

## Advanced Commands

### Run Workflow and Wait for Result

```bash
# Trigger and wait
gh workflow run scraper.yml -f end_page=1 && sleep 5 && gh run watch
```

### Download Latest Logs Automatically

```bash
# Get latest run ID and download logs
RUN_ID=$(gh run list --workflow=scraper.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run download $RUN_ID
```

### Check Workflow Success

```bash
# Get status of latest run
gh run list --workflow=scraper.yml --limit 1 --json conclusion --jq '.[0].conclusion'

# Expected: "success", "failure", or "cancelled"
```

### View Workflow File

```bash
# View workflow YAML
gh workflow view scraper.yml
```

---

## Environment Variables

You can also set secrets using environment variables:

```bash
# Export from .env
export $(grep -v '^#' .env | xargs)

# Set secrets
echo "$DATABASE_URL" | gh secret set DATABASE_URL
echo "$PROXY_URL" | gh secret set PROXY_URL
```

---

## Quick Reference

### Essential Commands

```bash
# Setup
gh auth login                          # Authenticate
gh repo create turbo_az --public       # Create repo
gh secret set SECRET_NAME              # Add secret
gh secret list                         # List secrets

# Workflows
gh workflow list                       # List workflows
gh workflow run scraper.yml            # Trigger run
gh workflow enable scraper.yml         # Enable workflow

# Runs
gh run list                            # List runs
gh run watch                           # Watch current run
gh run view --log                      # View logs
gh run download                        # Download artifacts

# Repository
gh repo view                           # View repo info
gh browse /actions                     # Open Actions tab
```

### Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# GitHub Actions shortcuts
alias ghl='gh run list --workflow=scraper.yml --limit 10'
alias ghw='gh run watch'
alias ghlog='gh run view --log'
alias ghtrigger='gh workflow run scraper.yml'
alias ghsecrets='gh secret list'
```

---

## Support

- **GitHub CLI Docs**: https://cli.github.com/manual/
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions

---

**Setup Date**: 2025-12-31
**GitHub CLI Version**: Run `gh --version` to check
