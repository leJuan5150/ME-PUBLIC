# daily-digest-feed

Scheduled GitHub Action that aggregates 21 YouTube channels + 3 Power Platform / Fabric newsletters into a single `feeds.json` file. Runs daily at 11:00 UTC (4 AM MST / 5 AM MDT) and commits the result to this repo.

The Cowork daily-digest scheduled agent fetches `feeds.json` at 5:30 AM local to populate its YouTube and newsletter sections. This exists because Cowork's network egress allowlist blocks `youtube.com`, `ppweekly.com`, `ppdevweekly.com`, and `powerbiweekly.info` directly — but `raw.githubusercontent.com` is allowed.

## Files

| File | Purpose |
|---|---|
| `fetch_feeds.py` | Main entry point — fetches all sources in parallel and writes `feeds.json` |
| `sources.py` | Editable config: the 24 sources (channel IDs + newsletter URLs) |
| `requirements.txt` | Single dep: `feedparser` |
| `feeds.json` | Generated output — committed by the Action every run |

## Consumer URL

```
https://raw.githubusercontent.com/leJuan5150/ME-PUBLIC/main/daily-digest-feed/feeds.json
```

## Local run

```bash
cd daily-digest-feed
pip install -r requirements.txt
python fetch_feeds.py
```

## Schema

See the [spec](https://github.com/leJuan5150/LEJUAN5150-NOTES) DATA MODEL section. Shape:

```json
{
  "generated_at": "ISO8601 UTC",
  "window_hours": 48,
  "sources": {
    "youtube": { "overlanding": [...], "power_platform": [...], "fabric_powerbi": [...], "ai": [...] },
    "newsletters": { "power_platform_weekly": {...}, "power_platform_dev_weekly": {...}, "power_bi_weekly": {...} }
  },
  "errors": []
}
```
