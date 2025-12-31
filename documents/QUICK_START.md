# Quick Start - Set Up in 2 Minutes

Get your scraper running on GitHub Actions in just a few commands!

---

## Prerequisites

✅ GitHub CLI installed (you already have it)
✅ .env file with DATABASE_URL and PROXY_URL (you have it)

---

## Option 1: Automated Setup (Easiest)

Run the setup script:

```bash
./setup_github_secrets.sh
```

That's it! The script will:
1. Check GitHub CLI is installed
2. Authenticate with GitHub
3. Create/use repository
4. Set secrets from .env
5. Verify everything is configured

---

## Option 2: Quick Manual Setup

Copy and paste these commands:

```bash
# 1. Authenticate with GitHub
gh auth login

# 2. Set secrets from .env file
grep "^DATABASE_URL=" .env | cut -d '=' -f2- | gh secret set DATABASE_URL
grep "^PROXY_URL=" .env | cut -d '=' -f2- | gh secret set PROXY_URL

# 3. Verify secrets
gh secret list

# 4. Push to GitHub (if repo exists)
git add .
git commit -m "Add automated scraper"
git push origin master

# 5. Trigger first run
gh workflow run scraper.yml -f start_page=1 -f end_page=1
```

Done! ✅

---

## Option 3: One-Liner (After gh auth login)

```bash
grep "^DATABASE_URL=" .env | cut -d '=' -f2- | gh secret set DATABASE_URL && grep "^PROXY_URL=" .env | cut -d '=' -f2- | gh secret set PROXY_URL && gh secret list
```

---

## Verify Setup

```bash
# Check secrets are set
gh secret list

# Should show:
# DATABASE_URL  Updated 2025-12-31
# PROXY_URL     Updated 2025-12-31
```

---

## First Test Run

```bash
# Trigger a test run (1 page only)
gh workflow run scraper.yml -f start_page=1 -f end_page=1

# Watch it run in real-time
gh run watch

# Or view in browser
gh browse /actions
```

---

## What Happens Next?

1. **Scheduled Runs**: Scraper runs automatically every 6 hours
2. **Data Saved**: Directly to PostgreSQL (no CSV files)
3. **Logs Available**: Download as artifacts from Actions tab
4. **Manual Triggers**: Run anytime with custom page ranges

---

## Useful Commands

```bash
# List recent runs
gh run list --workflow=scraper.yml

# View latest logs
gh run view --log

# Trigger custom run
gh workflow run scraper.yml -f start_page=1 -f end_page=100

# Update secrets
echo "NEW_URL" | gh secret set DATABASE_URL
```

---

## Troubleshooting

### "gh: command not found"
```bash
brew install gh
```

### "not logged in"
```bash
gh auth login
```

### "repository not found"
```bash
# Create repository first
gh repo create turbo_az --public --source=. --remote=origin --push
```

---

## Full Documentation

- **Complete CLI Guide**: `CLI_SETUP_GUIDE.md`
- **GitHub Actions Setup**: `GITHUB_ACTIONS_SETUP.md`
- **PostgreSQL Auto-Save**: `POSTGRES_AUTO_SAVE.md`

---

**You're all set!** 🚀

The scraper will now run automatically and save data to PostgreSQL.
