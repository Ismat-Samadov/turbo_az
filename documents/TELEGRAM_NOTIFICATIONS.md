# Telegram Notifications - Implementation Guide

## Overview

Implemented comprehensive Telegram reporting that sends detailed statistics to specified Telegram chats at the end of each scraping session.

---

## Features

### Notification Triggers

1. **Successful Completion**: Sends detailed stats when scraping completes normally
2. **User Interruption**: Sends partial stats when user presses Ctrl+C
3. **Error/Crash**: Sends error message with basic stats when fatal error occurs

### Statistics Included

#### Timing Information
- **Duration**: Total time in hours, minutes, and seconds
- **Average Time/Listing**: Performance metric per listing

#### Scraping Statistics
- **Pages Processed**: Number of pages scraped
- **Successful Scrapes**: Number of successfully scraped listings
- **Failed Scrapes**: Number of failed scrape attempts
- **Total Scraped**: Total listings scraped in this session

#### Database Statistics
- **Inserted**: New listings added to database
- **Duplicates Skipped**: Listings skipped due to duplicate detection
- **Total in DB**: Current total number of listings in database

#### Network Statistics
- **Total Requests**: Total HTTP requests made (pages + listings + phone numbers)
- **Estimated Cost**: Rough cost estimate based on proxy usage ($5/GB for BrightData)

#### Performance Metrics
- **Average Time/Listing**: Scraping speed per listing
- **Success Rate**: Percentage of successful scrapes

---

## Configuration

### Environment Variables (.env)

```bash
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=8202323082:AAGRimO8iScakpFKTHbkwhhbmMbPANX8e3g

# Telegram Chat IDs (comma-separated for multiple chats)
TELEGRAM_CHAT_ID=6192509415,-4879313859
```

### Multiple Chat Support

The implementation supports sending notifications to multiple Telegram chats:

- Comma-separated chat IDs in `.env` file
- Notifications sent to all specified chats
- Both user IDs and group IDs supported (groups use negative IDs)

---

## Implementation Details

### Files Modified

#### 1. `/Users/ismatsamadov/turbo_az/scripts/turbo_scraper.py`

**Added Telegram function** (lines 40-79):
```python
def send_telegram_message(bot_token: str, chat_ids: str, message: str):
    """Send message to Telegram using bot API"""
    # Parses comma-separated chat IDs
    # Sends HTML-formatted message to each chat
    # Logs success/failure for each delivery
```

**Added statistics tracking** (lines 189-196):
```python
self.stats = {
    'successful_scrapes': 0,
    'failed_scrapes': 0,
    'total_requests': 0,
    'pages_processed': 0,
    'duplicates_skipped': 0
}
```

**Updated tracking methods**:
- `fetch_page()`: Tracks total_requests
- `scrape_listing()`: Tracks successful_scrapes and failed_scrapes
- `scrape_page()`: Tracks pages_processed
- `save_to_postgres()`: Tracks duplicates_skipped and returns DB stats

**Updated main()** (lines 1053-1199):
- Loads Telegram credentials from .env
- Calculates comprehensive statistics
- Sends notifications on success, interruption, or error
- Includes cost estimation based on data usage

#### 2. `/Users/ismatsamadov/turbo_az/requirements.txt`
Added: `requests>=2.31.0  # Telegram notifications`

#### 3. `/Users/ismatsamadov/turbo_az/requirements-scraper.txt`
Added: `requests>=2.31.0`

---

## Message Formats

### Success Message

```
🚗 Turbo.az Scraping Complete!

⏱ Duration: 3h 45m 12s
📊 Pages Processed: 100

Listings Stats:
✅ Successful: 2,400
❌ Failed: 12
📝 Total Scraped: 2,412

Database Stats:
💾 Inserted: 2,380
⚠️ Duplicates Skipped: 32
📚 Total in DB: 42,480

Network Stats:
🌐 Total Requests: 7,236
💰 Est. Cost: $1.76

Performance:
⚡ Avg Time/Listing: 5.60s
🎯 Success Rate: 99.5%
```

### Interruption Message

```
⚠️ Turbo.az Scraping Interrupted!

⏱ Duration: 15m 30s
📊 Pages Processed: 10

Partial Stats:
✅ Successful: 240
❌ Failed: 3
📝 Scraped Before Stop: 243

💡 Progress saved - run again to resume!
```

### Error Message

```
❌ Turbo.az Scraping Error!

Error: Database connection timeout

💡 Progress saved - run again to resume!
```

---

## Cost Estimation Logic

```python
# Estimate: BrightData residential proxy ~$5 per GB
# Assumption: ~50KB per HTTP request (average)
estimated_data_gb = (total_requests * 50) / (1024 * 1024)  # KB to GB
estimated_cost = estimated_data_gb * 5  # $5 per GB
```

**Example Calculation:**
- 7,236 requests × 50KB = 361,800KB = 0.345GB
- 0.345GB × $5 = $1.73

---

## Testing

### Test with Single Page

```bash
cd /Users/ismatsamadov/turbo_az/scripts
END_PAGE=1 python3 turbo_scraper.py
```

**Expected Result:**
- Scraper runs normally
- Telegram notification sent to all configured chat IDs
- Logs show: `✅ Telegram notification sent to chat_id: XXXXXX`

### Test with Interruption

```bash
cd /Users/ismatsamadov/turbo_az/scripts
END_PAGE=10 python3 turbo_scraper.py
# Press Ctrl+C after a few listings
```

**Expected Result:**
- Progress saved
- Interruption notification sent with partial stats

---

## Troubleshooting

### No Notification Received

1. **Check .env file**: Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set correctly
2. **Check bot permissions**: Bot must be added to group chats (if using group IDs)
3. **Check logs**: Look for error messages like:
   - `Telegram credentials not configured, skipping notification`
   - `Failed to send Telegram message: 401 Unauthorized`

### Invalid Chat ID

**Symptom**: `Failed to send Telegram message to XXXXX: 400 Bad Request`

**Solution**:
- Verify chat ID is correct
- For groups: Chat ID should be negative (e.g., `-4879313859`)
- For users: Chat ID should be positive (e.g., `6192509415`)
- Get your chat ID from @userinfobot

### Bot Not in Group

**Symptom**: `Failed to send Telegram message: 403 Forbidden`

**Solution**: Add bot to the group chat before running scraper

---

## HTML Formatting

Telegram API supports HTML formatting. Current implementation uses:

- `<b>Text</b>` - Bold text
- Emojis for visual appeal
- Newlines for structure

**Alternative**: Can switch to Markdown by changing `'parse_mode': 'HTML'` to `'parse_mode': 'Markdown'`

---

## Future Enhancements

### Possible Additions

1. **Progress Updates**: Send notification every N pages during long scrapes
2. **Warning Thresholds**: Alert if failure rate exceeds X%
3. **Photo Attachments**: Send chart images with statistics
4. **Inline Buttons**: Add buttons to view logs, restart scraper, etc.
5. **Custom Cost Rates**: Make cost estimation configurable via .env

### Example Progress Update

```python
# In scrape_all_pages(), after processing each page:
if page_num % 100 == 0:
    message = f"📊 Progress Update: {page_num} pages completed..."
    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
```

---

## Dependencies

### Required Packages

- `requests>=2.31.0` - HTTP library for Telegram API calls

### Installation

```bash
# Minimal (scraping only)
pip install -r requirements-scraper.txt

# Full (with analysis/visualization)
pip install -r requirements.txt
```

---

## Security Notes

### Sensitive Information

- ⚠️ **Bot Token**: Keep `TELEGRAM_BOT_TOKEN` secret (never commit to Git)
- ⚠️ **Chat IDs**: Not sensitive, but should be in .env for flexibility
- ⚠️ **Message Content**: Consider if scraping stats should be confidential

### Best Practices

1. Use `.gitignore` to exclude `.env` file
2. Use environment variables in CI/CD (GitHub Secrets)
3. Rotate bot token if accidentally exposed
4. Limit bot permissions to only sending messages

---

## Related Files

- `scripts/turbo_scraper.py` - Main scraper with Telegram integration
- `.env` - Configuration file with credentials
- `requirements.txt` - Full dependencies
- `requirements-scraper.txt` - Minimal dependencies
- `documents/AUTO_SAVE_AND_DUPLICATES.md` - Checkpoint system documentation

---

## Summary

**Status**: ✅ Fully Implemented

**Features**:
- ✅ Sends detailed statistics on completion
- ✅ Handles interruptions and errors gracefully
- ✅ Supports multiple chat IDs
- ✅ Includes cost estimation
- ✅ HTML-formatted messages with emojis

**Next Steps**:
1. Test with real scraping run
2. Verify notifications received in Telegram
3. Adjust cost estimation if needed
4. Consider adding progress updates for long runs

---

*Implemented: 2025-12-31*
*Modified Files: turbo_scraper.py, requirements.txt, requirements-scraper.txt, .env*
*Dependencies Added: requests>=2.31.0*
