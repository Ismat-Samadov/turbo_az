# GitHub Secrets Setup - Complete Guide

## Changes Made

### GitHub Actions Workflow Updated
- ✅ Removed default values from workflow inputs
- ✅ All environment variables now read from GitHub Secrets
- ✅ Manual trigger can still override START_PAGE and END_PAGE

### Required Secrets (8 total)

All secrets must be set in GitHub repository settings:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `START_PAGE` | Starting page for scraping | `1` |
| `END_PAGE` | Ending page for scraping | `1770` |
| `BASE_URL` | Base URL for scraping | `https://turbo.az/autos` |
| `MAX_CONCURRENT` | Maximum concurrent requests | `3` |
| `DELAY` | Delay between requests (seconds) | `1` |
| `AUTO_SAVE_INTERVAL` | Auto-save interval | `50` |
| `PROXY_URL` | BrightData proxy URL | `http://username:password@host:port` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |

---

## Quick Setup (Recommended)

### Option 1: Automated Script

```bash
cd /Users/ismatsamadov/turbo_az
./documents/setup_github_secrets.sh
```

This will set all 8 secrets from your `.env` file.

---

### Option 2: One-Line Command

```bash
# From project root
grep "^START_PAGE=" .env | cut -d '=' -f2- | gh secret set START_PAGE && \
grep "^END_PAGE=" .env | cut -d '=' -f2- | gh secret set END_PAGE && \
grep "^BASE_URL=" .env | cut -d '=' -f2- | gh secret set BASE_URL && \
grep "^MAX_CONCURRENT=" .env | cut -d '=' -f2- | gh secret set MAX_CONCURRENT && \
grep "^DELAY=" .env | cut -d '=' -f2- | gh secret set DELAY && \
grep "^AUTO_SAVE_INTERVAL=" .env | cut -d '=' -f2- | gh secret set AUTO_SAVE_INTERVAL && \
grep "^PROXY_URL=" .env | cut -d '=' -f2- | gh secret set PROXY_URL && \
grep "^DATABASE_URL=" .env | cut -d '=' -f2- | gh secret set DATABASE_URL
```

---

### Option 3: Manual Setup

Set each secret individually:

```bash
# Scraping configuration
echo "1" | gh secret set START_PAGE
echo "1770" | gh secret set END_PAGE
echo "https://turbo.az/autos" | gh secret set BASE_URL
echo "3" | gh secret set MAX_CONCURRENT
echo "1" | gh secret set DELAY
echo "50" | gh secret set AUTO_SAVE_INTERVAL

# Proxy URL (replace with your actual proxy)
echo "http://brd-customer-hl_cc079cd9-zone-residential_proxy1:ja1dl6w7jyg1@brd.superproxy.io:33335" | gh secret set PROXY_URL

# Database URL (replace with your actual connection string)
echo "postgresql://myfrog_me_owner:ErAVlQSW06Ih@ep-red-dew-a22obfoo.eu-central-1.aws.neon.tech/myfrog_me?sslmode=require" | gh secret set DATABASE_URL
```

---

## Verify Setup

```bash
# List all secrets
gh secret list

# Expected output (8 secrets):
# AUTO_SAVE_INTERVAL  Updated 2025-12-31
# BASE_URL            Updated 2025-12-31
# DATABASE_URL        Updated 2025-12-31
# DELAY               Updated 2025-12-31
# END_PAGE            Updated 2025-12-31
# MAX_CONCURRENT      Updated 2025-12-31
# PROXY_URL           Updated 2025-12-31
# START_PAGE          Updated 2025-12-31
```

---

## Testing the Workflow

### Test with Default Settings (from secrets)

```bash
# Trigger workflow - uses all secrets
gh workflow run scraper.yml

# Watch the run
gh run watch

# View logs
gh run view --log
```

### Test with Custom Page Range (override)

```bash
# Override only START_PAGE and END_PAGE
gh workflow run scraper.yml -f start_page=1 -f end_page=5

# All other values (BASE_URL, MAX_CONCURRENT, etc.) come from secrets
```

---

## Update Secrets

If you need to update any secret:

```bash
# Update from .env
grep "^START_PAGE=" .env | cut -d '=' -f2- | gh secret set START_PAGE

# Or set manually
echo "2000" | gh secret set END_PAGE
```

---

## Troubleshooting

### Missing Secrets Error

If workflow fails with "secret not found":

```bash
# Check which secrets exist
gh secret list

# Set missing secrets
./documents/setup_github_secrets.sh
```

### Wrong Secret Values

```bash
# Delete and recreate
gh secret delete SECRET_NAME
echo "NEW_VALUE" | gh secret set SECRET_NAME
```

### Verify Workflow Configuration

```bash
# View workflow file
gh workflow view scraper.yml

# Check recent runs
gh run list --workflow=scraper.yml --limit 5
```

---

## Benefits of This Setup

✅ **Security**: No hardcoded values in workflow file
✅ **Flexibility**: Easy to update secrets without changing code
✅ **Override Capability**: Can still override page range for testing
✅ **Environment Consistency**: Same configuration across all runs
✅ **Easy Management**: All configuration in GitHub Secrets UI

---

## Next Steps

1. ✅ Set all 8 secrets using one of the methods above
2. ✅ Verify secrets are set with `gh secret list`
3. ✅ Test workflow with `gh workflow run scraper.yml`
4. ✅ Monitor the run with `gh run watch`
5. ✅ Check logs with `gh run view --log`

---

*Setup Guide Updated: 2025-12-31*
*GitHub Actions Workflow: `.github/workflows/scraper.yml`*
