#!/usr/bin/env python3
"""
Regenerates feed.xml, notes-feed.xml, and dates.json from blog.html and notes.html.
Run this from the blog root directory before committing a new post:
    python3 generate-feed.py
"""

import re
import json
from datetime import datetime, timezone

BASE_URL = "https://sreekarscribbles.com"

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
        cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', raw)
        return datetime.strptime(cleaned, "%d %b, %Y").strftime("%Y-%m-%d")
    except Exception:
        return None

def build_feed(entries, title, description, link):
    items = []
    for href, post_title in entries:
        url = f"{BASE_URL}/{href}"
        items.append(f"""    <item>
      <title><![CDATA[{post_title}]]></title>
      <link>{url}</link>
      <guid>{url}</guid>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{title}</title>
    <link>{link}</link>
    <description>{description}</description>
    <language>en</language>
    <lastBuildDate>{now}</lastBuildDate>

{chr(10).join(items)}

  </channel>
</rss>
"""

# --- Blog feed ---
with open("blog.html", encoding="utf-8") as f:
    blog_content = f.read()

posts = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', blog_content)
if not posts:
    print("No posts found in blog.html. Exiting.")
    exit(1)

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(build_feed(posts, "Sreekar Scribbles", "Personal blog by Sreekar", f"{BASE_URL}/"))

dates = sorted(set(filter(None, (parse_post_date(href) for href, _ in posts))))
with open("dates.json", "w", encoding="utf-8") as f:
    json.dump(dates, f)

print(f"feed.xml updated with {len(posts)} posts.")
print(f"dates.json updated with {len(dates)} dates.")

# --- Notes feed ---
with open("notes.html", encoding="utf-8") as f:
    notes_content = f.read()

notes = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', notes_content)

with open("notes-feed.xml", "w", encoding="utf-8") as f:
    f.write(build_feed(notes, "Sreekar Scribbles — Notes", "Quick notes from everyday life by Sreekar", f"{BASE_URL}/notes.html"))

print(f"notes-feed.xml updated with {len(notes)} notes.")
