# 通过 Unsplash 公开 napi 搜索接口获取 photo ID
import httpx
import re

KEYWORDS = {
    "beef": "beef stir fry",
    "shrimp": "garlic shrimp",
    "broccoli": "broccoli",
    "cucumber": "cucumber salad",
    "eggplant": "eggplant",
    "cabbage": "cabbage",
    "pork": "shredded pork",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

def search_unsplash(keyword):
    url = f"https://unsplash.com/napi/search/photos?query={keyword.replace(' ', '+')}&per_page=15&orientation=landscape"
    try:
        r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
        if r.status_code != 200:
            print(f"  status {r.status_code}")
            return []
        data = r.json()
        results = []
        for item in data.get("results", []):
            pid = item.get("id")
            desc = (item.get("alt_description") or item.get("description") or "")[:50]
            results.append((pid, desc))
        return results
    except Exception as e:
        print(f"  error: {e}")
        return []

for key, kw in KEYWORDS.items():
    print(f"=== {key}: {kw} ===")
    res = search_unsplash(kw)
    for pid, desc in res[:8]:
        print(f"  {pid}  {desc}")
