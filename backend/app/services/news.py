import logging
from datetime import datetime, timezone

import feedparser
import httpx

from app.config import settings

log = logging.getLogger(__name__)


async def fetch_news(max_items: int = 20) -> list[dict]:
    """Fetch and merge news from configured RSS feeds."""
    all_entries = []
    async with httpx.AsyncClient(timeout=15) as client:
        for feed_url in settings.news_rss_feeds:
            try:
                resp = await client.get(feed_url)
                resp.raise_for_status()
                feed = feedparser.parse(resp.text)
                for entry in feed.entries[:10]:
                    published = entry.get("published_parsed")
                    if published:
                        pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    else:
                        pub_dt = datetime.now(timezone.utc)
                    all_entries.append(
                        {
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "summary": entry.get("summary", ""),
                            "published": pub_dt.isoformat(),
                            "source": feed.feed.get("title", feed_url),
                        }
                    )
                log.debug("Fetched %d entries from %s", len(feed.entries[:10]), feed_url)
            except httpx.HTTPStatusError as e:
                log.warning("RSS feed returned %d: %s", e.response.status_code, feed_url)
            except httpx.ConnectError:
                log.warning("Could not connect to RSS feed: %s", feed_url)
            except Exception:
                log.exception("Unexpected error fetching RSS feed: %s", feed_url)

    all_entries.sort(key=lambda x: x["published"], reverse=True)
    log.info("Aggregated %d news items from %d feeds", len(all_entries), len(settings.news_rss_feeds))
    return all_entries[:max_items]
