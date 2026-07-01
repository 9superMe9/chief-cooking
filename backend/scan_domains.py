# 扫描各关键词 murl 的域名分布，寻找 Unsplash/Pexels 直链
import re
import httpx
from collections import Counter
from urllib.parse import urlparse

KEYWORDS = {
    "beef": "beef stir fry",
    "shrimp": "garlic shrimp",
    "broccoli": "broccoli stir fry",
    "cucumber": "cucumber salad",
    "eggplant": "braised eggplant",
    "cabbage": "stir fried cabbage",
    "pork": "shredded pork stir fry",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

PAT = re.compile(r'murl&quot;:&quot;(https?://[^&]+)&')

def fetch(keyword):
    url = f"https://www.bing.com/images/search?q={keyword.replace(' ', '+')}&form=HDRSC2"
    r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
    return PAT.findall(r.text)

for key, kw in KEYWORDS.items():
    murls = fetch(kw)
    print(f"=== {key} ({kw}): {len(murls)} murls ===")
    domains = Counter()
    for m in murls:
        try:
            d = urlparse(m).netloc
            domains[d] += 1
        except Exception:
            pass
    for d, c in domains.most_common(8):
        print(f"  {c:3d}  {d}")
    # show any unsplash/pexels
    up = [m for m in murls if "unsplash" in m or "pexels" in m]
    print(f"  unsplash/pexels hits: {len(up)}")
    for u in up[:3]:
        print(f"    {u[:130]}")
