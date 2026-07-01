# 检查 Unsplash 与 Pexels 搜索页返回内容
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

for label, url in [
    ("unsplash", "https://unsplash.com/s/photos/beef-stir-fry"),
    ("pexels", "https://www.pexels.com/search/beef%20stir%20fry/"),
]:
    try:
        r = httpx.get(url, headers=HEADERS, timeout=25, follow_redirects=True)
        print(f"=== {label}: status {r.status_code}, len {len(r.text)} ===")
        print(repr(r.text[:600]))
        print()
    except Exception as e:
        print(f"=== {label}: error {e} ===")
