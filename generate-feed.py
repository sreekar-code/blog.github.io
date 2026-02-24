#!/usr/bin/env python3
"""
Regenerates feed.xml from the post list in blog.html.
Run this from the blog root directory before committing a new post:
    python3 generate-feed.py
"""

import re
from datetime import datetime, timezone

BASE_URL = "https://sreekarscribbles.com"
BLOG_HTML = "blog.html"
FEED_XML = "feed.xml"

# Extract all <li><a href="...">Title</a></li> entries from blog.html
with open(BLOG_HTML, encoding="utf-8") as f:
    content = f.read()

posts = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', content)

if not posts:
    print("No posts found in blog.html. Exiting.")
    exit(1)

now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

items = []
for href, title in posts:
    # href is like "blog/the-phoenix-tree.html" — make it absolute
    url = f"{BASE_URL}/{href}"
    items.append(f"""    <item>
      <title><![CDATA[{title}]]></title>
      <link>{url}</link>
      <guid>{url}</guid>
    </item>""")

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

print(f"feed.xml updated with {len(posts)} posts.")
