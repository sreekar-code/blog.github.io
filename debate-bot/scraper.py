"""
scraper.py — Fetch RSS feed and scrape full post content from Ghost blog.

Priority order:
  - RSS: http://localhost:2368/rss first, fall back to https://sreekarscribbles.com/rss
  - Post content: swap public URL host → localhost first, fall back to public URL
"""
from __future__ import annotations

import random
import logging
import re
from urllib.parse import urlparse, urlunparse

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

RSS_LOCAL = "http://localhost:2368/feed.xml"
RSS_PUBLIC = "https://sreekarscribbles.com/feed.xml"
LOCAL_BASE = "http://localhost:2368"
MAX_POSTS = 30
MAX_TEXT_CHARS = 4000
REQUEST_TIMEOUT = 10  # seconds


def _to_local_url(public_url: str) -> str:
    """Convert a public post URL to its localhost equivalent."""
    parsed = urlparse(public_url)
    local = parsed._replace(scheme="http", netloc="localhost:2368")
    return urlunparse(local)


def _fetch_feed() -> list[dict]:
    """
    Fetch RSS feed, trying localhost first then public URL.
    Returns list of entry dicts with keys: title, link.
    """
    for rss_url in [RSS_LOCAL, RSS_PUBLIC]:
        try:
            logger.info("Trying RSS feed: %s", rss_url)
            feed = feedparser.parse(rss_url)
            if feed.bozo and not feed.entries:
                logger.warning("Feed parse error for %s: %s", rss_url, feed.bozo_exception)
                continue
            if not feed.entries:
                logger.warning("No entries found in %s", rss_url)
                continue
            entries = [
                {"title": e.get("title", "Untitled"), "link": e.get("link", "")}
                for e in feed.entries[:MAX_POSTS]
                if e.get("link")
            ]
            if entries:
                logger.info("Fetched %d entries from %s", len(entries), rss_url)
                return entries
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", rss_url, exc)
    return []


def _scrape_post(public_url: str) -> str:
    """
    Scrape full post text from a Ghost blog URL.
    Tries localhost version first, falls back to public URL.
    Returns plain text truncated to MAX_TEXT_CHARS.
    """
    urls_to_try = [_to_local_url(public_url), public_url]
    html = None

    for url in urls_to_try:
        try:
            logger.info("Scraping post from: %s", url)
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            html = resp.text
            logger.info("Got HTML from %s (%d bytes)", url, len(html))
            break
        except requests.RequestException as exc:
            logger.warning("Failed to fetch post from %s: %s", url, exc)

    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Remove noise tags
    for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Try Ghost-specific selectors in order, then fall back to main
    content_el = (
        soup.select_one(".gh-content")
        or soup.select_one(".post-content")
        or soup.find("article")
        or soup.find("main")
    )

    if content_el:
        # Strip nav-only paragraphs (contain only <a> children, no real text)
        for p in content_el.find_all("p"):
            tag_children = [c for c in p.children if hasattr(c, "name") and c.name]
            is_nav = tag_children and all(c.name == "a" for c in tag_children)
            if p.get_text(strip=True) == "" or is_nav:
                p.decompose()
        # Strip horizontal rules used as dividers
        for hr in content_el.find_all("hr"):
            hr.decompose()

    if not content_el:
        logger.warning("No content element found for %s", public_url)
        return ""

    text = content_el.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:MAX_TEXT_CHARS]


def get_random_post() -> dict | None:
    """
    Fetch RSS feed, pick a random post, scrape its full content.
    Returns: { title: str, url: str, full_text: str }
    Returns None if anything fails critically.
    """
    entries = _fetch_feed()
    if not entries:
        logger.error("Could not fetch any RSS entries.")
        return None

    entry = random.choice(entries)
    title = entry["title"]
    public_url = entry["link"]

    full_text = _scrape_post(public_url)

    if not full_text:
        logger.warning("Empty content for '%s', trying another post if available.", title)
        # Try a few more candidates before giving up
        remaining = [e for e in entries if e["link"] != public_url]
        random.shuffle(remaining)
        for candidate in remaining[:3]:
            full_text = _scrape_post(candidate["link"])
            if full_text:
                title = candidate["title"]
                public_url = candidate["link"]
                break

    if not full_text:
        logger.error("Could not scrape content from any post.")
        return None

    return {"title": title, "url": public_url, "full_text": full_text}


if __name__ == "__main__":
    # Quick smoke test
    logging.basicConfig(level=logging.INFO)
    print("Fetching random post...")
    post = get_random_post()
    if post:
        print(f"\nTitle: {post['title']}")
        print(f"URL:   {post['url']}")
        print(f"Text preview (first 500 chars):\n{post['full_text'][:500]}")
    else:
        print("Failed to fetch a post.")
