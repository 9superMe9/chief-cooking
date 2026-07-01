# 抓取 Unsplash 搜索页 HTML，从嵌入 JSON 中提取 photo ID
import httpx
import re
import json

KEYWORDS = {
    "beef": "beef stir fry",
    "shrimp": "garlic shrimp",
    "broccoli": "broccoli",
    "cucumber": "cucumber",
    "eggplant": "eggplant",
    "cabbage": "cabbage",
    "pork": "shredded pork",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_search(keyword):
    url = f"https://unsplash.com/s/photos/{keyword.replace(' ', '-')}"
    try:
        r = httpx.get(url, headers=HEADERS, timeout=25, follow_redirects=True)
        return r.text
    except Exception as e:
        print(f"  fetch error: {e}")
        return ""

def extract_ids(html):
    # photo IDs are 11-char base64-ish, appear in /photos/<id> and images.unsplash.com/photo-...<id>
    ids = set()
    # pattern: /photos/<slug>-<id>  where id is 11 chars
    for m in re.findall(r'/photos/[a-z0-9\-]*?-([a-zA-Z0-9_-]{11})(?:[\"/?]|$)', html):
        ids.add(m)
    # also images.unsplash.com/photo-<timestamp>-<id>
    for m in re.findall(r'images\.unsplash\.com/photo-\d+-([a-zA-Z0-9_-]{11})', html):
        ids.add(m)
    return ids

for key, kw in KEYWORDS.items():
    print(f"=== {key}: {kw} ===")
    html = fetch_search(kw)
    print(f"  html len: {len(html)}")
    ids = extract_ids(html)
    print(f"  ids found: {len(ids)}")
    for i in list(ids)[:10]:
        print(f"    {i}")
