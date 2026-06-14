#!/usr/bin/env python3

import requests
import time
import os
import sys
import re
import html as html_lib

FEED_URL = "https://www.lcwc911.us/live-incident-list"
KEYWORDS = ["adamstown"]  # customize these
POLL_INTERVAL = 30

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set as environment variables.")
    sys.exit(1)

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

seen_ids = set()


def parse_fire_table(page_html):
    fire_section = re.search(
        r'Active Fire Incidents.*?(<table[^>]*>.*?</table>)',
        page_html,
        re.DOTALL | re.IGNORECASE,
    )
    if not fire_section:
        return []

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', fire_section.group(1), re.DOTALL | re.IGNORECASE)

    incidents = []
    for row in rows[1:]:  # skip header row
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(cells) < 4:
            continue
        clean = [html_lib.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c)).strip()) for c in cells]
        incidents.append({
            "datetime": clean[0],
            "type":     clean[1],
            "location": clean[2],
            "units":    clean[3],
        })

    return incidents


def check_feed():
    try:
        resp = requests.get(FEED_URL, headers=REQUEST_HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Fetch error: {e}")
        return

    for incident in parse_fire_table(resp.text):
        combined = f"{incident['type']} {incident['location']}".lower()
        if not any(kw.lower() in combined for kw in KEYWORDS):
            continue

        # No GUID on this page — datetime + location is unique per incident
        incident_id = f"{incident['datetime']}|{incident['location']}"
        if incident_id in seen_ids:
            continue

        seen_ids.add(incident_id)

        message = (
            f"{incident['type']}\n"
            f"{incident['location']}\n"
            f"Units: {incident['units']}"
        )
        print(message)
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message},
            timeout=10,
        )


print(f"Monitoring {FEED_URL} every {POLL_INTERVAL}s for fire incidents matching: {KEYWORDS}")

while True:
    check_feed()
    time.sleep(POLL_INTERVAL)
