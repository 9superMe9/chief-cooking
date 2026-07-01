# 通过 Bing 图片搜索抓取 murl 直链，提取 Unsplash/Pexels photo ID
import re
import httpx

KEYWORDS = {
    "beef": "beef stir fry",
    "shrimp": "garlic shrimp stir fried",
    "broccoli": "broccoli dish chinese",
    "cucumber": "cucumber salad chinese",
    "eggplant": "braised eggplant chinese",
    "cabbage": "stir fried cabbage chinese",
    "pork": "shredded pork stir fry",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_bing(keyword):
    url = f"https://www.bing.com/images/search?q={keyword.replace(' ', '+')}&form=HDRSC2"
    try:
        r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
        return r.text
    except Exception as e:
        print(f"  fetch error: {e}")
        return ""

def extract_murls(html):
    # Bing stores media url in murl param
    return re.findall(r'"murl":"(https?://[^"]+)"', html)

def find_unsplash_pexels(murls):
    results = {"unsplash": [], "pexels": []}
    for m in murls:
        # decode unicode escapes
        try:
            m_dec = m.encode().decode('unicode_escape')
        except Exception:
            m_dec = m
        u = re.search(r'images\.unsplash\.com/photo-([a-f0-9-]+)', m_dec)
        if u:
            pid = u.group(1).rstrip('-')
            results["unsplash"].append(pid)
            continue
        p = re.search(r'images\.pexels\.com/photos/(\d+)/', m_dec)
        if p:
            results["pexels"].append(p.group(1))
    return results

def main():
    candidates = {}
    for key, kw in KEYWORDS.items():
        print(f"=== {key}: {kw} ===")
        html = fetch_bing(kw)
        murls = extract_murls(html)
        print(f"  murls found: {len(murls)}")
        res = find_unsplash_pexels(murls)
        print(f"  unsplash ids: {res['unsplash'][:5]}")
        print(f"  pexels ids: {res['pexels'][:5]}")
        candidates[key] = res
    return candidates

if __name__ == "__main__":
    main()
