"""daily-digest-feed — fetch all 24 sources, write feeds.json.

Runs in GitHub Actions at 11:00 UTC daily. See ../README.md for context.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib import request
from urllib.error import URLError

import feedparser  # type: ignore

from sources import (
    NEWSLETTER_SOURCES,
    YOUTUBE_SOURCES,
    all_youtube_sources,
    total_source_count,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
WINDOW_HOURS = 48
HTTP_TIMEOUT = 15
MAX_WORKERS = 8
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
OUTPUT_PATH = Path(__file__).parent / "feeds.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("daily-digest-feed")


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
def http_get(url: str, timeout: int = HTTP_TIMEOUT) -> bytes:
    req = request.Request(url, headers={"User-Agent": USER_AGENT})
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------
def _to_utc(struct_time) -> datetime | None:
    if not struct_time:
        return None
    try:
        return datetime(*struct_time[:6], tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def fetch_youtube(category: str, source: dict, cutoff: datetime) -> tuple[str, dict]:
    channel_id = source["channel_id"]
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    result: dict = {
        "creator": source["name"],
        "handle": source["handle"],
        "channel_id": channel_id,
        "videos": [],
        "error": None,
    }
    try:
        raw = http_get(url)
        parsed = feedparser.parse(raw)
        for entry in parsed.entries:
            published = _to_utc(getattr(entry, "published_parsed", None))
            if published is None or published < cutoff:
                continue
            summary = getattr(entry, "summary", "") or ""
            result["videos"].append(
                {
                    "title": getattr(entry, "title", ""),
                    "url": getattr(entry, "link", ""),
                    "published": published.isoformat().replace("+00:00", "Z"),
                    "description": summary[:500],
                }
            )
        log.info("youtube:%s %s → %d new", category, source["name"], len(result["videos"]))
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
        log.warning("youtube:%s %s FAILED: %s", category, source["name"], result["error"])
    return category, result


# ---------------------------------------------------------------------------
# Newsletters — Substack (RSS-driven)
# ---------------------------------------------------------------------------
_ISSUE_NUMBER_PATTERNS = (
    re.compile(r"issue[\s\-_]*#?(\d+)", re.IGNORECASE),  # "Issue 258", "issue-258"
    re.compile(r"#(\d+)\b"),                              # "#290"
    re.compile(r"/p/(\d+)(?:[/?#]|$)"),                   # ".../p/290"
    re.compile(r"-(\d+)(?:[/?#]|$)"),                     # ".../p/power-platform-weekly-issue-258"
)


def _extract_issue_number(title: str, link: str) -> int | None:
    for src in (title, link):
        if not src:
            continue
        for pat in _ISSUE_NUMBER_PATTERNS:
            m = pat.search(src)
            if m:
                try:
                    return int(m.group(1))
                except ValueError:
                    continue
    return None


class _SubstackSectionParser(HTMLParser):
    """Very rough section extractor: collects headings + following links."""

    def __init__(self) -> None:
        super().__init__()
        self.current_section: str | None = None
        self.sections: dict[str, list[dict]] = {}
        self._in_heading = False
        self._heading_buf: list[str] = []
        self._in_link = False
        self._link_href: str | None = None
        self._link_buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "h4"):
            self._in_heading = True
            self._heading_buf = []
        elif tag == "a":
            href = dict(attrs).get("href")
            if href and href.startswith("http"):
                self._in_link = True
                self._link_href = href
                self._link_buf = []

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4") and self._in_heading:
            self._in_heading = False
            heading = "".join(self._heading_buf).strip()
            if heading:
                self.current_section = heading
                self.sections.setdefault(heading, [])
        elif tag == "a" and self._in_link:
            text = "".join(self._link_buf).strip()
            if self.current_section and text and self._link_href:
                self.sections[self.current_section].append(
                    {"title": text, "url": self._link_href}
                )
            self._in_link = False
            self._link_href = None

    def handle_data(self, data):
        if self._in_heading:
            self._heading_buf.append(data)
        elif self._in_link:
            self._link_buf.append(data)


def fetch_substack(source: dict, cutoff: datetime) -> tuple[str, dict]:
    key = source["key"]
    result: dict = {
        "name": source["name"],
        "issue_number": None,
        "issue_date": None,
        "url": source["url"],
        "is_new": False,
        "sections": {},
        "error": None,
    }
    try:
        parsed = feedparser.parse(source["feed_url"])
        if not parsed.entries:
            raise RuntimeError("no entries in feed")
        latest = parsed.entries[0]
        published = _to_utc(getattr(latest, "published_parsed", None))
        title = getattr(latest, "title", "") or ""
        link = getattr(latest, "link", "") or source["url"]

        result["url"] = link
        result["issue_number"] = _extract_issue_number(title, link)
        if published:
            result["issue_date"] = published.date().isoformat()
            result["is_new"] = published >= cutoff

        # Parse sections out of the feed entry HTML content
        content_html = ""
        if hasattr(latest, "content") and latest.content:
            content_html = latest.content[0].get("value", "")
        elif hasattr(latest, "summary"):
            content_html = latest.summary or ""

        if content_html:
            parser = _SubstackSectionParser()
            parser.feed(content_html)
            # Drop empty sections
            result["sections"] = {k: v for k, v in parser.sections.items() if v}

        log.info(
            "newsletter:%s issue=%s new=%s sections=%d",
            key,
            result["issue_number"],
            result["is_new"],
            len(result["sections"]),
        )
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
        log.warning("newsletter:%s FAILED: %s", key, result["error"])
    return key, result


# ---------------------------------------------------------------------------
# Newsletter — Power BI Weekly (custom HTML)
# ---------------------------------------------------------------------------
class _PbiWeeklyIndexParser(HTMLParser):
    """Find the most recent issue-N.html link on the homepage."""

    _ISSUE_HREF_RE = re.compile(r"issue-(\d+)\.html", re.IGNORECASE)

    def __init__(self) -> None:
        super().__init__()
        self.best_number: int = -1
        self.best_href: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href", "") or ""
        m = self._ISSUE_HREF_RE.search(href)
        if not m:
            return
        num = int(m.group(1))
        if num > self.best_number:
            self.best_number = num
            self.best_href = href


class _PbiWeeklyIssueParser(HTMLParser):
    """Group links under the nearest preceding heading."""

    def __init__(self) -> None:
        super().__init__()
        self.current_section: str | None = None
        self.sections: dict[str, list[dict]] = {}
        self.issue_date: str | None = None
        self._in_heading = False
        self._heading_buf: list[str] = []
        self._in_link = False
        self._link_href: str | None = None
        self._link_buf: list[str] = []
        self._seen_first_date = False

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3"):
            self._in_heading = True
            self._heading_buf = []
        elif tag == "a":
            href = dict(attrs).get("href", "") or ""
            if href.startswith("http"):
                self._in_link = True
                self._link_href = href
                self._link_buf = []

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3") and self._in_heading:
            self._in_heading = False
            heading = "".join(self._heading_buf).strip()
            if heading:
                # h1 on the issue page usually contains the issue title/date
                self.current_section = heading
                self.sections.setdefault(heading, [])
        elif tag == "a" and self._in_link:
            text = "".join(self._link_buf).strip()
            if self.current_section and text and self._link_href:
                self.sections[self.current_section].append(
                    {"title": text, "url": self._link_href}
                )
            self._in_link = False
            self._link_href = None

    def handle_data(self, data):
        if self._in_heading:
            self._heading_buf.append(data)
        elif self._in_link:
            self._link_buf.append(data)
        # Crude: look for an ISO-ish date in body text once
        if not self._seen_first_date:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", data)
            if m:
                self.issue_date = m.group(1)
                self._seen_first_date = True


def fetch_pbi_weekly(source: dict, cutoff: datetime) -> tuple[str, dict]:
    key = source["key"]
    base = source["url"].rstrip("/")
    result: dict = {
        "name": source["name"],
        "issue_number": None,
        "issue_date": None,
        "url": source["url"],
        "is_new": False,
        "sections": {},
        "error": None,
    }
    try:
        homepage = http_get(base + "/").decode("utf-8", errors="replace")
        idx = _PbiWeeklyIndexParser()
        idx.feed(homepage)
        if idx.best_href is None:
            raise RuntimeError("no issue-N.html link found on homepage")

        href = idx.best_href
        if href.startswith("http"):
            issue_url = href
        elif href.startswith("/"):
            issue_url = base + href
        else:
            issue_url = base + "/" + href

        result["issue_number"] = idx.best_number
        result["url"] = issue_url

        issue_html = http_get(issue_url).decode("utf-8", errors="replace")
        parser = _PbiWeeklyIssueParser()
        parser.feed(issue_html)
        result["sections"] = {k: v for k, v in parser.sections.items() if v}

        if parser.issue_date:
            result["issue_date"] = parser.issue_date
            try:
                d = datetime.fromisoformat(parser.issue_date).replace(tzinfo=timezone.utc)
                result["is_new"] = d >= cutoff
            except ValueError:
                pass

        log.info(
            "newsletter:%s issue=%s new=%s sections=%d",
            key,
            result["issue_number"],
            result["is_new"],
            len(result["sections"]),
        )
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
        log.warning("newsletter:%s FAILED: %s", key, result["error"])
    return key, result


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def build_feed() -> dict:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=WINDOW_HOURS)
    log.info("cutoff=%s window=%dh", cutoff.isoformat(), WINDOW_HOURS)

    youtube_out: dict[str, list[dict]] = {cat: [] for cat in YOUTUBE_SOURCES}
    newsletters_out: dict[str, dict] = {}
    errors: list[str] = []
    success_count = 0
    total = total_source_count()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = []

        for category, source in all_youtube_sources():
            futures.append(pool.submit(fetch_youtube, category, source, cutoff))

        for source in NEWSLETTER_SOURCES:
            if source["type"] == "substack":
                futures.append(pool.submit(fetch_substack, source, cutoff))
            elif source["type"] == "custom" and source["key"] == "power_bi_weekly":
                futures.append(pool.submit(fetch_pbi_weekly, source, cutoff))
            else:
                log.warning("unknown newsletter type for %s", source["key"])

        for fut in as_completed(futures):
            try:
                key, data = fut.result()
            except Exception as exc:  # noqa: BLE001
                errors.append(f"task crashed: {type(exc).__name__}: {exc}")
                continue

            if key in YOUTUBE_SOURCES:
                youtube_out[key].append(data)
                if data.get("error") is None:
                    success_count += 1
                else:
                    errors.append(f"youtube/{key}/{data['creator']}: {data['error']}")
            else:
                newsletters_out[key] = data
                if data.get("error") is None:
                    success_count += 1
                else:
                    errors.append(f"newsletter/{key}: {data['error']}")

    # Preserve the spec's category order within youtube_out
    ordered_youtube = {cat: youtube_out[cat] for cat in YOUTUBE_SOURCES}

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "window_hours": WINDOW_HOURS,
        "sources": {
            "youtube": ordered_youtube,
            "newsletters": newsletters_out,
        },
        "errors": errors,
        "_meta": {
            "success_count": success_count,
            "total_sources": total,
        },
    }


def main() -> int:
    start = time.time()
    feed = build_feed()
    meta = feed["_meta"]
    success = meta["success_count"]
    total = meta["total_sources"]

    # Count total items for the summary line
    total_items = 0
    for cat_list in feed["sources"]["youtube"].values():
        for ch in cat_list:
            total_items += len(ch.get("videos", []))
    for nl in feed["sources"]["newsletters"].values():
        for items in nl.get("sections", {}).values():
            total_items += len(items)

    OUTPUT_PATH.write_text(
        json.dumps(feed, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    elapsed = time.time() - start
    log.info(
        "Fetched %d/%d sources, %d total items, %.1fs → %s",
        success,
        total,
        total_items,
        elapsed,
        OUTPUT_PATH.name,
    )

    if success < (total / 2):
        log.error("less than 50%% of sources succeeded (%d/%d) — failing run", success, total)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
