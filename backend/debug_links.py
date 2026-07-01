# 检查 Bing 网页搜索结果中 unsplash 相关链接
import httpx
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

url = "https://www.bing.com/search?q=site%3Aunsplash.com+beef+stir+fry"
r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
text = r.text

# count occurrences
for kw in ["unsplash.com/photos", "unsplash.com", "pexels.com", "images.unsplash"]:
    print(f"{kw}: {text.count(kw)}")

# find all unsplash.com occurrences with context
for m in re.finditer(r'unsplash\.com[^"\'<> ]{0,60}', text):
    print("  ", m.group(0)[:80])
