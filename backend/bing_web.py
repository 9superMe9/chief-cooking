# 通过 Bing 网页搜索 site:unsplash.com 找图页 URL，提取 photo ID
import httpx
import re

KEYWORDS = {
    "beef": "beef stir fry",
    "shrimp": "garlic shrimp",
    "broccoli": "broccoli",
    "cucumber": "cucumber salad",
    "eggplant": "eggplant dish",
    "cabbage": "cabbage vegetable",
    "pork": "pork stir fry",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def bing_web(query):
    url = f"https://www.bing.com/search?q=site%3Aunsplash.com+{query.replace(' ', '+')}"
    r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
    return r.text

def extract_unsplash_ids(html):
    # unsplash photo pages: unsplash.com/photos/<slug>-<id>  id is 11 chars
    ids = []
    for m in re.findall(r'unsplash\.com/photos/[a-z0-9\-]*?-([a-zA-Z0-9_\-]{11})(?:[\"/?&]|$)', html):
        ids.append(m)
    # dedupe preserve order
    seen = set()
    out = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out

for key, kw in KEYWORDS.items():
    print(f"=== {key}: {kw} ===")
    html = bing_web(kw)
    print(f"  html len: {len(html)}")
    ids = extract_unsplash_ids(html)
    print(f"  unsplash ids: {ids[:10]}")
