#!/usr/bin/env python3
"""
Regenerates feed.xml and dates.json from the post list in blog.html.
Run this from the blog root directory before committing a new post:
    python3 generate-feed.py
"""

import re
import json
from datetime import datetime, timezone

BASE_URL = "https://sreekarscribbles.com"
BLOG_HTML = "blog.html"
FEED_XML = "feed.xml"
DATES_JSON = "dates.json"

# Extract all <li><a href="...">Title</a></li> entries from blog.html
with open(BLOG_HTML, encoding="utf-8") as f:
    content = f.read()

posts = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', content)

if not posts:
    print("No posts found in blog.html. Exiting.")
    exit(1)

now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

def parse_post_date(href):
    """Read a post file and extract its date as YYYY-MM-DD, or None."""
    try:
        with open(href, encoding="utf-8") as f:
            html = f.read()
        match = re.search(r'<p class="date">([^<]+)</p>', html)
        if not match:
            return None
        raw = match.group(1).strip()
        # Strip ordinal suffixes: "22nd" -> "22", "1st" -> "1"
        cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', raw)
        return datetime.strptime(cleaned, "%d %b, %Y").strftime("%Y-%m-%d")
    except Exception:
        return None

items = []
dates = []

for href, title in posts:
    url = f"{BASE_URL}/{href}"
    items.append(f"""    <item>
      <title><![CDATA[{title}]]></title>
      <link>{url}</link>
      <guid>{url}</guid>
    </item>""")

    date = parse_post_date(href)
    if date:
        dates.append(date)

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sreekar Scribbles</title>
    <link>{BASE_URL}/</link>
    <description>Personal blog by Sreekar</description>
    <language>en</language>
    <lastBuildDate>{now}</lastBuildDate>

{chr(10).join(items)}

  </channel>
</rss>
"""

with open(FEED_XML, "w", encoding="utf-8") as f:
    f.write(feed)

dates = sorted(set(dates))
with open(DATES_JSON, "w", encoding="utf-8") as f:
    json.dump(dates, f)

print(f"feed.xml updated with {len(posts)} posts.")
print(f"dates.json updated with {len(dates)} dates.")
