#!/usr/bin/env python3

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.request import urlopen

RSS_URL = "https://prjctimg.me/feed.xml"
README_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "README.md")
MAX_POSTS = 10
SENTINEL_START = "<!--RECENTLY:START-->"
SENTINEL_END = "<!--RECENTLY:END-->"


def fetch_rss(url):
    try:
        with urlopen(url, timeout=15) as response:
            return response.read()
    except Exception as e:
        print(f"Warning: Failed to fetch RSS feed: {e}", file=sys.stderr)
        return None


def parse_rss(xml_data):
    root = ET.fromstring(xml_data)
    channel = root.find("channel")
    items = []
    for item in channel.findall("item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        pub_date_str = item.findtext("pubDate", "")
        pub_date = parse_date(pub_date_str)
        items.append({"title": title, "link": link, "pub_date": pub_date, "pub_date_str": pub_date_str})
    return items


def parse_date(rfc2822_str):
    try:
        return datetime.strptime(rfc2822_str, "%a, %d %b %Y %H:%M:%S %Z")
    except (ValueError, TypeError):
        return datetime.min


def format_date(dt):
    return dt.strftime("%b %d, %Y") if dt else ""


def format_posts(items):
    items.sort(key=lambda x: x["pub_date"], reverse=True)
    lines = ["## In case you missed it 🦋"]
    for item in items[:MAX_POSTS]:
        title = item["title"]
        link = item["link"]
        date = format_date(item["pub_date"])
        tag = ""
        display_title = title
        m = re.match(r'^\[(Blog|Devlog)\]\s+(.*)', title)
        if m:
            tag = m.group(1)
            display_title = m.group(2)
        tag_part = f"`[{tag}]`" if tag else ""
        lines.append(f"- {date} — {tag_part} [{display_title}]({link})")
    return "\n".join(lines)


def update_readme(readme_path, new_content):
    with open(readme_path, "r") as f:
        content = f.read()

    pattern = re.compile(
        rf"{re.escape(SENTINEL_START)}.*?{re.escape(SENTINEL_END)}",
        re.DOTALL,
    )
    replacement = f"{SENTINEL_START}\n{new_content}\n{SENTINEL_END}"

    if not pattern.search(content):
        content = content.rstrip() + f"\n\n{SENTINEL_START}\n{SENTINEL_END}\n"

    content = pattern.sub(replacement, content)

    with open(readme_path, "w") as f:
        f.write(content)


def main():
    xml_data = fetch_rss(RSS_URL)
    if xml_data is None:
        print("ERROR: Could not fetch RSS feed, skipping update.", file=sys.stderr)
        sys.exit(1)
    items = parse_rss(xml_data)
    posts_md = format_posts(items)
    update_readme(README_PATH, posts_md)
    print("README.md updated successfully.")


if __name__ == "__main__":
    main()
