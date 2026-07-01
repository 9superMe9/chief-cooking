# 通过 DuckDuckGo 图片搜索接口获取直链，提取 Unsplash/Pexels ID
import httpx
import re
import json

KEYWORDS = {
    "beef": "beef stir fry",
    "shrimp": "garlic shrimp",
    "broccoli": "broccoli dish",
    "cucumber": "cucumber salad",
    "eggplant": "braised eggplant",
    "cabbage": "stir fried cabbage",
    "pork": "shredded pork stir fry",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://duckduckgo.com/",
}

def ddg_image_search(keyword):
    # first get a vqd token from the html page
    sess = httpx.Client(headers=HEADERS, timeout=25, follow_redirects=True)
    q = keyword.replace(" ", "+")
    # try the i.js endpoint directly (sometimes works without token)
    url = f"https://duckduckgo.com/i.js?q={q}&o=json&p=1"
    try:
        r = sess.get(url)
        if r.status_code == 200 and r.text.strip().startswith("{"):
            return r.json()
        # fallback: parse html for token
        r2 = sess.get(f"https://duckduckgo.com/?q={q}&iax=images&ia=images")
        m = re.search(r'vqd=["\'](\d+-\d+-\d+)["\']', r2.text)
        if m:
            vqd = m.group(1)
            url2 = f"https://duckduckgo.com/i.js?q={q}&o=json&p=1&vqd={vqd}"
            r3 = sess.get(url2)
            if r3.status_code == 200 and r3.text.strip().startswith("{"):
                return r3.json()
        return {}
    except Exception as e:
        print(f"  error: {e}")
        return {}

for key, kw in KEYWORDS.items():
    print(f"=== {key}: {kw} ===")
    data = ddg_image_search(kw)
    results = data.get("results", [])
    print(f"  results: {len(results)}")
    up_hits = []
    for item in results:
        img = item.get("image") or item.get("thumbnail") or ""
        if "unsplash" in img or "pexels" in img:
            up_hits.append(img)
    print(f"  unsplash/pexels hits: {len(up_hits)}")
    for h in up_hits[:4]:
        print(f"    {h[:130]}")
    # also show a few raw image hosts
    hosts = set()
    for item in results[:15]:
        img = item.get("image", "")
        if img:
            from urllib.parse import urlparse
            try:
                hosts.add(urlparse(img).netloc)
            except Exception:
                pass
    print(f"  sample hosts: {list(hosts)[:10]}")
