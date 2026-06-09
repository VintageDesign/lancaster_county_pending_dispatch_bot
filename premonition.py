#!/usr/bin/env python3

import feedparser
import time

FEED_URL = "https://webcad.lcwc911.us/Pages/Public/LiveIncidentsFeed.aspx"
KEYWORDS = ["keyword1", "PENDING"]  # customize these
POLL_INTERVAL = 30  # 5 minutes, matching the feed's declared TTl

seen_guids = set()

def check_feed():
    feed = feedparser.parse(FEED_URL)

    for entry in feed.entries:
        if entry.id in seen_guids:
            continue

        seen_guids.add(entry.id)
        combined = f"{entry.title} {entry.description}".lower()
        matched = [kw for kw in KEYWORDS if kw.lower() in combined]

        if matched:
            print(f"ALERT: {entry.published}")
            print(f"  {entry.title} — {entry.description}")
            print(f"  Matched: {matched}")

print(f"Monitoring {FEED_URL} every {POLL_INTERVAL}s for: {KEYWORDS}")

# Run once immediately on start, then on interval
while True:
    check_feed()
    time.sleep(POLL_INTERVAL)
