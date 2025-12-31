# GitHub Actions Setup Guide

Complete guide to set up automated scraping with GitHub Actions.

## Overview

The scraper now runs automatically on GitHub Actions:
- **Schedule**: Every 6 hours (or custom schedule)
- **Manual trigger**: Can be triggered manually with custom page range
- **Database**: Saves directly to PostgreSQL (no CSV files)
- **Logs**: Uploaded as artifacts for debugging

## Prerequisites

✅ GitHub repository for the project
✅ PostgreSQL database (already set up)
✅ BrightData proxy account

---

## Setup Steps

### Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Add automated scraper with PostgreSQL support"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/turbo_az.git

# Push to GitHub
git push -u origin master
```

### Step 2: Set Up GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

#### 1. DATABASE_URL
```
postgresql://myfrog_me_owner:ErAVlQSW06Ih@ep-red-dew-a22obfoo.eu-central-1.aws.neon.tech/myfrog_me?sslmode=require
```

#### 2. PROXY_URL
```
http://brd-customer-hl_cc079cd9-zone-residential_proxy1:ja1dl6w7jyg1@brd.superproxy.io:33335
```

**How to add secrets:**
1. Click "New repository secret"
2. Name: `DATABASE_URL`
3. Value: Paste the connection string
4. Click "Add secret"
5. Repeat for `PROXY_URL`

### Step 3: Verify Workflow File

The workflow file is already created at:
```
.github/workflows/scraper.yml
```

It will:
- Run every 6 hours automatically
- Can be triggered manually
- Install dependencies
- Run the scraper
- Upload logs as artifacts

### Step 4: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Actions** tab
3. If prompted, enable GitHub Actions
4. You should see "Turbo.az Scraper" workflow

### Step 5: Test Manual Run

1. Go to **Actions** tab
2. Click **Turbo.az Scraper** workflow
3. Click **Run workflow** button
4. Set parameters:
   - Start page: `1`
   - End page: `1` (for testing)
5. Click **Run workflow**

### Step 6: Monitor Execution

1. Watch the workflow run in real-time
2. Check each step for errors
3. Download logs artifact if needed

---

## Workflow Schedule

### Current Schedule: Every 6 Hours
```yaml
cron: '0 */6 * * *'
```

### Other Schedule Examples:

**Every 3 hours:**
```yaml
cron: '0 */3 * * *'
```

**Every day at 2 AM:**
```yaml
cron: '0 2 * * *'
```

**Every Monday at 9 AM:**
```yaml
cron: '0 9 * * 1'
```

**Twice daily (9 AM and 9 PM):**
```yaml
cron: '0 9,21 * * *'
```

To change schedule, edit `.github/workflows/scraper.yml` and push changes.

---

## Manual Trigger Options

You can manually trigger the scraper with custom page ranges:

1. Go to Actions → Turbo.az Scraper
2. Click "Run workflow"
3. Set parameters:
   - **Start page**: Starting page number (default: 1)
   - **End page**: Ending page number (default: 1770)
4. Click "Run workflow"

**Examples:**

- **Test run**: Start=1, End=1
- **Small batch**: Start=1, End=10
- **Full scrape**: Start=1, End=1770
- **Resume from page 500**: Start=500, End=1770

---

## Monitoring & Logs

### View Workflow Runs
1. Go to **Actions** tab
2. See list of all runs
3. Click any run to see details

### Download Logs
1. Click on a workflow run
2. Scroll down to **Artifacts**
3. Download `scraper-log-XXX.zip`
4. Extract and view `scraper.log`

### Check Database
After a run completes, verify data in PostgreSQL:

```sql
-- Check total listings
SELECT COUNT(*) FROM scraping.turbo_az;

-- Check latest scrapes
SELECT COUNT(*), DATE(scraped_at) as date
FROM scraping.turbo_az
GROUP BY DATE(scraped_at)
ORDER BY date DESC
LIMIT 7;

-- Check phone numbers scraped today
SELECT COUNT(*)
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL
  AND DATE(scraped_at) = CURRENT_DATE;
```

---

## Troubleshooting

### Workflow Not Running

**Check:**
- GitHub Actions enabled in repository settings
- Workflow file syntax is valid (YAML)
- Secrets are set correctly

### Database Connection Failed

**Check:**
- DATABASE_URL secret is correct
- Neon database is active
- No typos in connection string

### Proxy Errors (403/429)

**Check:**
- PROXY_URL secret is correct
- BrightData account has credit
- Proxy zone is active

### Import Errors

**Check:**
- requirements.txt includes all dependencies
- Python version is 3.10 in workflow file

### Scraper Timeout

**Options:**
- Reduce END_PAGE
- Increase DELAY between requests
- Split into multiple runs

---

## Cost Management

### BrightData Costs

Based on your test:
- **1 page**: ~$0.009 (~21 listings)
- **10 pages**: ~$0.09 (~216 listings)
- **1770 pages**: ~$15.75 (~38,232 listings)

### Optimization Strategies

**1. Reduce Frequency**
```yaml
# Instead of every 6 hours, run daily
cron: '0 2 * * *'
```

**2. Incremental Scraping**
Only scrape new listings (future enhancement)

**3. Smaller Batches**
```yaml
# Run 100 pages per day instead of full scrape
END_PAGE: '100'
```

**4. Weekend Only**
```yaml
# Only run on Saturdays
cron: '0 9 * * 6'
```

---

## Database Maintenance

### Auto-Vacuum (Recommended)

PostgreSQL auto-vacuum is enabled by default on Neon.

### Manual Vacuum (if needed)

```sql
VACUUM ANALYZE scraping.turbo_az;
```

### Remove Old Listings (Optional)

```sql
-- Delete listings older than 90 days
DELETE FROM scraping.turbo_az
WHERE scraped_at < NOW() - INTERVAL '90 days';
```

### Check Database Size

```sql
SELECT pg_size_pretty(pg_total_relation_size('scraping.turbo_az'));
```

---

## Advanced Configuration

### Environment Variables in Workflow

Edit `.github/workflows/scraper.yml` to change defaults:

```yaml
- name: Create .env file
  run: |
    cat > .env << EOF
    START_PAGE=1
    END_PAGE=100          # Change this
    MAX_CONCURRENT=5      # Change this
    DELAY=1.5             # Change this
    AUTO_SAVE_INTERVAL=25 # Change this
    # ...
    EOF
```

### Multiple Workflows

Create separate workflows for different schedules:

- `scraper-daily.yml`: Full scrape once daily
- `scraper-hourly.yml`: Small batch every hour
- `scraper-weekly.yml`: Deep scrape weekly

---

## Success Criteria

After setup, you should see:

✅ Workflow runs successfully
✅ No errors in logs
✅ Data appears in PostgreSQL database
✅ Phone numbers in JSONB format
✅ Scheduled runs execute automatically
✅ Manual triggers work correctly

---

## Example: First Run Verification

After your first automated run:

```sql
-- 1. Check if data was inserted
SELECT COUNT(*) FROM scraping.turbo_az;

-- 2. Check latest scrape timestamp
SELECT MAX(scraped_at) FROM scraping.turbo_az;

-- 3. Check sample data
SELECT listing_id, title, make, model, seller_phone
FROM scraping.turbo_az
ORDER BY scraped_at DESC
LIMIT 5;

-- 4. Check phones with JSONB
SELECT listing_id, seller_phone->0 as first_phone
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL
LIMIT 5;
```

Expected results:
- Count increases after each run
- Latest timestamp matches workflow run time
- Phone numbers in JSONB array format: `["phone1", "phone2"]`

---

## Support & Resources

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Neon Database**: https://neon.tech/docs
- **BrightData**: https://brightdata.com/cp/zones
- **Cron Schedule**: https://crontab.guru/

---

## Quick Reference

### Commands

```bash
# View workflow status (GitHub CLI)
gh workflow list
gh run list --workflow=scraper.yml

# Trigger manual run (GitHub CLI)
gh workflow run scraper.yml -f start_page=1 -f end_page=10

# View logs (GitHub CLI)
gh run view --log
```

### Files

- Workflow: `.github/workflows/scraper.yml`
- Scraper: `scripts/turbo_scraper.py`
- Requirements: `requirements.txt`
- SQL Queries: `SQL_QUERIES.md`

### Secrets

- `DATABASE_URL`: PostgreSQL connection
- `PROXY_URL`: BrightData proxy

---

**Setup Date**: 2025-12-31
**Status**: Ready for Production ✅
